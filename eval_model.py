import torch
import numpy as np
import pandas as pd
from utils.datasets import FoodImagesDataset
from tqdm import tqdm
from torch.utils.data import DataLoader
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report
from sklearn.metrics import mean_absolute_percentage_error

import torch
import torch.nn as nn
import torch.nn.functional as F
from collections import OrderedDict
from torchvision import models
from glob import glob
from tqdm import tqdm

class FoodNetBaseline(nn.Module):
    def __init__(self, n_classes=5):
        super().__init__()
        self.net = models.resnet50(weights=models.ResNet50_Weights.DEFAULT)
        self.n_features = self.net.fc.in_features
        self.net.fc = nn.Identity()
        self.net.fc1 = nn.Sequential(
            OrderedDict(
                [
                    ("linear", nn.Linear(self.n_features, self.n_features)),
                    ("relu1", nn.ReLU()),
                    ("final", nn.Linear(self.n_features, 1)),
                ]
            )
        )

    def forward(self, x):
        x = self.net(x)
        reg_head = self.net.fc1(x)
        return reg_head

class FoodNetBaselineV2(nn.Module):
    def __init__(self, n_classes=5):
        super().__init__()
        self.net = models.resnet50(weights=models.ResNet50_Weights.DEFAULT)
        self.n_features = self.net.fc.in_features
        self.net.fc = nn.Identity()
        self.net.fc2 = nn.Sequential(
            OrderedDict(
                [
                    ("linear", nn.Linear(self.n_features, self.n_features)),
                    ("relu1", nn.ReLU()),
                    ("final", nn.Linear(self.n_features, n_classes)),
                ]
            )
        )

    def forward(self, x):
        x = self.net(x)
        class_head = self.net.fc2(x)
        return class_head
    
class FoodNetV1(nn.Module):
    def __init__(self, n_classes=5):
        super().__init__()
        self.net = models.resnet50(weights=models.ResNet50_Weights.DEFAULT)
        self.n_features = self.net.fc.in_features
        self.net.fc = nn.Identity()
        self.net.fc1 = nn.Sequential(
            OrderedDict(
                [
                    ("linear", nn.Linear(self.n_features, self.n_features)),
                    ("relu1", nn.ReLU()),
                    ("final", nn.Linear(self.n_features, 1)),
                ]
            )
        )
        self.net.fc2 = nn.Sequential(
            OrderedDict(
                [
                    ("linear", nn.Linear(self.n_features, self.n_features)),
                    ("relu1", nn.ReLU()),
                    ("final", nn.Linear(self.n_features, n_classes)),
                ]
            )
        )
        self.sigma1 = nn.Parameter(torch.zeros(1))
        self.sigma2 = nn.Parameter(torch.zeros(1))

    def forward(self, x):
        x = self.net(x)
        reg_head = self.net.fc1(x)
        class_head = self.net.fc2(x)
        return reg_head, class_head, self.sigma1, self.sigma2

class FoodNetV2(nn.Module):
    def __init__(self, n_classes=5):
        super().__init__()
        self.net = models.resnet50(weights=models.ResNet50_Weights.DEFAULT)
        self.n_features = self.net.fc.in_features
        self.net.fc = nn.Identity()
        self.net.fc1 = nn.Sequential(
            OrderedDict(
                [
                    ("linear", nn.Linear(self.n_features + n_classes, self.n_features + n_classes)),
                    ("relu1", nn.ReLU()),
                    ("final", nn.Linear(self.n_features + n_classes, 1)),
                ]
            )
        )
        self.net.fc2 = nn.Sequential(
            OrderedDict(
                [
                    ("linear", nn.Linear(self.n_features, self.n_features)),
                    ("relu1", nn.ReLU()),
                    ("final", nn.Linear(self.n_features, n_classes)),
                ]
            )
        )
        self.sigma1 = nn.Parameter(torch.zeros(1))
        self.sigma2 = nn.Parameter(torch.zeros(1))

    def forward(self, x):
        x = self.net(x)
        class_head = self.net.fc2(x)
        reg_head = self.net.fc1(torch.cat([x, class_head], dim=1))
        return reg_head, class_head, self.sigma1, self.sigma2
    
if __name__ == "__main__":
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

    df = pd.read_csv("./regression-20230213T104418Z-001/csv/train.csv")
    le = LabelEncoder()
    le.fit(df["food"])

    test_datasets = FoodImagesDataset(
        csv_file="./regression-20230213T104418Z-001/csv/test.csv",
        img_dir="./regression-20230213T104418Z-001/test",
        target_transform=le.transform,
    )
    test_dataloader = DataLoader(test_datasets, batch_size=512, shuffle=False)
    model_weights = glob("./model/foodnet_resnet50_baseline_regression_*_677.pth")
    for model_weight in tqdm(model_weights):
        model = FoodNetBaseline(len(le.classes_))
        model.load_state_dict(torch.load(model_weight))
        model.to(device)

        model.eval()
        reg = []
        classi = []

        with torch.no_grad():
            for i, data in enumerate(test_dataloader, 0):
                inputs, weight, labels = data
                weight, labels = weight.long(), labels.long()
                inputs, weight, labels = inputs.to(device), weight.to(device), labels.to(device)

                outputs = model.forward(inputs)
                
                classi.extend(["-"] * len(outputs))
                reg.extend(outputs.cpu().numpy().flatten().tolist())
            predict = pd.DataFrame({"reg": reg, "cls": classi})
        predict.to_csv(f"./out/{model_weight.split('/')[-1].split('.')[0]}.csv", index=False)
        