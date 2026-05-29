import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
import csv
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder

DATASET_FILE = "model/gesture_detection/gesture_dataset.csv"
MODEL_FILE = "model/gesture_detection/gesture_model.pth"
EPOCHS = 100
BATCH_SIZE = 32
LEARNING_RATE = 0.001

# Load dataset
X = []
y = []

with open(DATASET_FILE, newline="") as f:
    reader = csv.reader(f)
    for row in reader:
        row = [float(v) for v in row]
        X.append(row[:-1])
        y.append(int(row[-1]))

X = np.array(X, dtype=np.float32)
y = np.array(y)

# Encode labels (1,2,3 → 0,1,2)
encoder = LabelEncoder()
y = encoder.fit_transform(y)

num_classes = len(np.unique(y))
input_size = X.shape[1]

print("Input size:", input_size)
print("Number of gestures:", num_classes)

# Train/test split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, shuffle=True
)

X_train = torch.tensor(X_train)
y_train = torch.tensor(y_train)
X_test = torch.tensor(X_test)
y_test = torch.tensor(y_test)

train_dataset = torch.utils.data.TensorDataset(X_train, y_train)
train_loader = torch.utils.data.DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True)

# Neural network
class GestureNet(nn.Module):
    def __init__(self, input_size, num_classes):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(input_size, 128),
            nn.ReLU(),
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Linear(32, num_classes)
        )

    def forward(self, x):
        return self.net(x)

model = GestureNet(input_size, num_classes)

criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=LEARNING_RATE)

# Training loop
for epoch in range(EPOCHS):
    model.train()
    total_loss = 0

    for batch_x, batch_y in train_loader:
        optimizer.zero_grad()
        outputs = model(batch_x)
        loss = criterion(outputs, batch_y)
        loss.backward()
        optimizer.step()
        total_loss += loss.item()

    model.eval()
    with torch.no_grad():
        outputs = model(X_test)
        predictions = torch.argmax(outputs, dim=1)
        accuracy = (predictions == y_test).float().mean().item()

    print(f"Epoch {epoch+1}/{EPOCHS} | Loss: {total_loss:.4f} | Accuracy: {accuracy*100:.2f}%")

# Save model
torch.save({
    "model_state": model.state_dict(),
    "label_encoder": encoder.classes_
}, MODEL_FILE)

print("Model saved to", MODEL_FILE)