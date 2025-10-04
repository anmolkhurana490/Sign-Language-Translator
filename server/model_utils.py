import numpy as np
import torch
from torch import nn

in_channels = 3
num_nodes = 67

# ----- Word Level Model -----
class WordLevelModel(nn.Module):
  def __init__(self, input_size, hidden_sizes, dropout_rates, output_size):
    super().__init__()

    classifier_layers = [nn.Flatten()]

    for size, rate in zip(hidden_sizes, dropout_rates):
      classifier_layers.extend([
          nn.Linear(input_size, size),
          nn.BatchNorm1d(size),
          nn.ReLU(),
          nn.Dropout(rate)
      ])

      input_size = size

    classifier_layers.append(nn.Linear(input_size, output_size))

    self.classifier = nn.Sequential(*classifier_layers)


  def forward(self, x):
    out = self.classifier(x)
    return out


# ----- Frame Encoder -----
class FrameEncoder(nn.Module):
    def __init__(self, in_frame_size, hidden_neurons, dropout_rates, frame_dim, frame_fc_dropout):
        """
        in_frame_size: features per node (e.g. x,y,z,conf → 4)
        hidden_neurons: list of hidden layer sizes [64, 128, ...]
        frame_dim: output embedding dimension for each frame
        dropout_rates: list of dropouts per layer (same length as hidden_neurons)
        frame_fc_dropout: dropout for the fully-connected layer
        """
        super().__init__()
        layers = []
        input_dim = in_frame_size

        if dropout_rates is None:
            dropout_rates = [0.0] * len(hidden_neurons)

        # Feature Projections per node
        for h, dr in zip(hidden_neurons, dropout_rates):
            layers.append(nn.Linear(input_dim, h))
            layers.append(nn.ReLU())
            layers.append(nn.Dropout(dr))
            input_dim = h

        self.node_proj = nn.Sequential(*layers)

        # Frame fully-connected projection
        self.frame_fc = nn.Sequential(
            nn.Linear(input_dim, frame_dim),
            nn.ReLU(),
            nn.Dropout(frame_fc_dropout)  # global dropout
        )

    def forward(self, x):
        # x: (B, T, N*F) -> flatten nodes per frame
        x = x.reshape(x.shape[0], x.shape[1], -1)  # (B,T,N*F)

        x = self.node_proj(x)          # (B,T,H_last)
        x = self.frame_fc(x)           # (B,T,frame_dim)
        return x

# ----- Sequence Classifier -----
class SequenceClassifier(nn.Module):
    def __init__(self, in_frame_dim, temporal_size, num_temporal_layers, temporal_dropout, output_size,
                 class_hidden_neurons, class_dropout_rates, rnn_type="GRU", bidir=True):
        """
        in_frame_dim: per-frame embedding dimension
        temporal_size: hidden size of temporal encoder
        num_temporal_layers: how many GRU/LSTM layers
        temporal_dropout: dropout for the temporal encoder
        class_hidden_neurons: list of hidden layer sizes for the classifier
        class_droput_rates: list of dropouts per layer (same length as class_hidden_neurons)
        rnn_type: "GRU" | "LSTM" | "RNN" | "TRANSFORMER"
        """
        super().__init__()
        self.use_transformer = rnn_type == "TRANSFORMER"

        if rnn_type == "GRU":
            self.rnn = nn.GRU(in_frame_dim, temporal_size,
                              num_layers=num_temporal_layers,
                              bidirectional=bidir, batch_first=True,
                              dropout=temporal_dropout if num_temporal_layers > 1 else 0.0)

        elif rnn_type == "LSTM":
            self.rnn = nn.LSTM(in_frame_dim, temporal_size,
                               num_layers=num_temporal_layers,
                               bidirectional=bidir, batch_first=True,
                               dropout=temporal_dropout if num_temporal_layers > 1 else 0.0)

        elif rnn_type == "TRANSFORMER":
            self.rnn = nn.TransformerEncoder(
                nn.TransformerEncoderLayer(d_model=in_frame_dim, nhead=8, dropout=temporal_dropout, batch_first=True),
                num_layers=num_temporal_layers
            )

        else:
            self.rnn = nn.RNN(in_frame_dim, temporal_size,
                              num_layers=num_temporal_layers,
                              bidirectional=bidir, batch_first=True,
                              dropout=temporal_dropout if num_temporal_layers > 1 else 0.0)

        fc_input_size = temporal_size if (self.use_transformer or not bidir) else 2 * temporal_size

        # temporal pooling + classifier
        self.temp_pool = nn.AdaptiveAvgPool2d((1, fc_input_size))  # (B, 1, fc_input)

        layers = []
        input_dim = fc_input_size

        for h, dr in zip(class_hidden_neurons, class_dropout_rates):
            layers.append(nn.Linear(input_dim, h))
            layers.append(nn.ReLU())
            layers.append(nn.Dropout(dr))
            input_dim = h

        layers.append(nn.Linear(input_dim, output_size))

        self.classifier = nn.Sequential(*layers)

    def forward(self, x):
        # x: (B, T, D)
        if self.use_transformer:
            seq_out = self.rnn(x)                   # (B,T,2*H)
        else:
            seq_out, _ = self.rnn(x)                # (B,T,2*H)

        # seq_out = seq_out.transpose(1, 2)       # (B,2*H,T)
        pooled = self.temp_pool(seq_out).squeeze(-2)  # (B,2*H)
        out = self.classifier(pooled)
        return out


# ----- Sentence Level Model -----
class MyModel(nn.Module):
    def __init__(self, in_frame_size, frame_proj_neurons, proj_dropout_rates, frame_fc_dropout,
                 frame_dim, temporal_size, num_temporal_layers, temporal_dropout, output_size,
                 class_hidden_neurons, class_dropout_rates, rnn_type="GRU", bidir=True):
        super().__init__()
        self.frame_encoder = FrameEncoder(in_frame_size, frame_proj_neurons, proj_dropout_rates,
                                          frame_dim, frame_fc_dropout)

        self.sequence_classifier = SequenceClassifier(frame_dim, temporal_size, num_temporal_layers, temporal_dropout, output_size,
                                                      class_hidden_neurons, class_dropout_rates, rnn_type=rnn_type, bidir=bidir)

    def forward(self, x):
        # x: (B,T,F) where F = N*features
        frame_emb = self.frame_encoder(x)   # (B,T,frame_dim)
        out = self.sequence_classifier(frame_emb)  # (B,num_classes)
        return out


# ----- Load Models -----
def load_word_level_model(state_dict_path):
    state_dict = torch.load(state_dict_path, map_location='cpu')
    model = WordLevelModel(in_channels * num_nodes, [1472, 3520], [0.2, 0.2], 114)

    model.load_state_dict(state_dict)
    model.eval()

    return model

def load_sentence_level_model(state_dict_path):
    state_dict = torch.load(state_dict_path, map_location='cpu')

    model = MyModel(
        num_nodes*in_channels,
        [448], [0.3], 0.45, 384, 704, 2, 0.15, 101,
        [], [], rnn_type="GRU"
    )

    model.load_state_dict(state_dict)
    model.eval()

    return model


if __name__ == "__main__":
    model1 = load_word_level_model("saved_models/word_level_model_states_v3.pth")
    model2 = load_sentence_level_model("saved_models/sentence_level_model_states_v3.pth")

    print(model1)
    print(model2)