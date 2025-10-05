import numpy as np
import torch
from torch import nn
import json

in_channels = 3
num_nodes = 67

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# ----- Word Level Model -----
class MyModel(nn.Module):
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


# ----- Load Model -----
def load_word_model(state_dict_path):
    state_dict = torch.load(state_dict_path, map_location='cpu')
    model = MyModel(in_channels * num_nodes, [1472, 3520], [0.2, 0.2], 114)

    model.load_state_dict(state_dict)
    model.eval()

    return model


def load_json(file_path):
  with open(file_path, 'r') as f:
    return json.load(f)
  
# ----- Label Decoder -----
word_decoder = load_json("data/word_class_names.json")


# ----- Predict Word Gloss -----
def predict_word_gloss(model, x):
    x = x.unsqueeze(0).to(device)
    x = x[:, :num_nodes, :in_channels].to(torch.float32)

    with torch.no_grad():
      out = model(x)
      out = nn.functional.sigmoid(out)

    val, ypred = torch.max(out, 1)
    return word_decoder[ypred.item()], val.item()


if __name__ == "__main__":
    model = load_word_model("saved_models/word_level_model_states_v3.pth")
    print(model)