import numpy as np
import torch
from torch import nn
import json

in_channels = 3
num_nodes = 67

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

def load_json(file_path):
  with open(file_path, 'r') as f:
    return json.load(f)

# ----- Label Decoder -----
word_decoder = load_json("data/include_class_names.json")

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
        # x, _ = self.attention(x, x, x) # (B,T,H_last)
        x = self.frame_fc(x)           # (B,T,frame_dim)
        return x

# ----- Sequence Classifier -----
class SequenceClassifier(nn.Module):
    def __init__(self, in_frame_dim, temporal_size, num_temporal_layers, numHeads, temporal_dropout,
                 class_hidden_neurons, class_dropout_rates, output_size, rnn_type="TRANSFORMER"):
        """
        in_frame_dim: per-frame embedding dimension
        temporal_size: hidden size of temporal encoder
        num_temporal_layers: how many GRU/LSTM layers
        temporal_dropout: dropout for the temporal encoder
        class_hidden_neurons: list of hidden layer sizes for the classifier
        class_droput_rates: list of dropouts per layer (same length as class_hidden_neurons)
        """
        super().__init__()
        self.use_transformer = rnn_type == "TRANSFORMER"

        if rnn_type == "GRU":
            self.rnn = nn.GRU(in_frame_dim, temporal_size,
                              num_layers=num_temporal_layers,
                              bidirectional=True, batch_first=True,
                              dropout=temporal_dropout if num_temporal_layers > 1 else 0.0)

        elif rnn_type == "TRANSFORMER":
            self.rnn = nn.TransformerEncoder(
                nn.TransformerEncoderLayer(d_model=in_frame_dim, nhead=numHeads, dropout=temporal_dropout, batch_first=True),
                num_layers=num_temporal_layers
            )

        fc_input_size = temporal_size if self.use_transformer else 2 * temporal_size

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


# ----- Combined Model -----
class MyModel(nn.Module):
    def __init__(self, in_frame_size, frame_proj_neurons, proj_dropout_rates, frame_fc_dropout,
                 frame_dim, temporal_size, num_temporal_layers, numHeads, temporal_dropout,
                 class_hidden_neurons, class_dropout_rates, output_size, rnn_type="TRANSFORMER"):
        super().__init__()
        self.frame_encoder = FrameEncoder(in_frame_size, frame_proj_neurons, proj_dropout_rates,
                                          frame_dim, frame_fc_dropout)

        self.sequence_classifier = SequenceClassifier(frame_dim, temporal_size, num_temporal_layers, numHeads, temporal_dropout,
                                                      class_hidden_neurons, class_dropout_rates, output_size, rnn_type=rnn_type)

    def forward(self, x):
        # x: (B,T,F) where F = N*features
        frame_emb = self.frame_encoder(x)   # (B,T,frame_dim)
        out = self.sequence_classifier(frame_emb)  # (B,num_classes)
        return out


# ----- Load Model -----
def load_word_model(state_dict_path):
    state_dict = torch.load(state_dict_path, map_location='cpu')

    model = MyModel(
        num_nodes*in_channels,
        [], [], 0.0, 480, 1024, 3, 8, 0.0, [1024], [0.5],
        len(word_decoder), rnn_type="TRANSFORMER"
    )

    model.load_state_dict(state_dict)
    model.eval()

    return model


# ----- Predict Word Gloss -----
def predict_word_gloss(model, frame_seq):
    if not frame_seq or len(frame_seq) == 0:
        return "", 0.0
    
    x = torch.stack(frame_seq).unsqueeze(0).to(device)
    x = x[:, :, :num_nodes, :in_channels].to(torch.float32)

    with torch.no_grad():
        out = model(x)
        out = nn.functional.sigmoid(out)

    val, ypred = torch.max(out, 1)
    return word_decoder[ypred.item()], val.item()


if __name__ == "__main__":
    model = load_word_model("saved_models/word_level_model_states_include.pth")
    print(model)

    x = [torch.randn(num_nodes, in_channels) for _ in range(30)]  # Example input: 30 frames

    word, confidence = predict_word_gloss(model, x)
    print(f"Predicted word: {word}, confidence: {confidence}")