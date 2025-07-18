import torch
import torch.nn as nn
from torch.utils.data import DataLoader, Subset
from torchaudio.datasets import LIBRISPEECH
from dist.finetuning.dataset import BulgarianSpeechDataset
import logging

from utils import get_device, load_config, load_pretrained, data_split
from utils import collate_fn
from utils import train_step
from model.losses.loss import Loss
from model.wav2vec2 import Wav2Vec


DEVICE = torch.device(get_device())
print(f"[INFO] Training will run on: {DEVICE.type.upper()}\n")

# Loading configuration data
config = load_config()
MODEL_NAME = str(config["model"]["model_name"])
MODEL_DIMENSIONS = int(config["model"]["model_dimensions"])

EPOCHS = int(config["training"]["epochs"])
BATCH_SIZE = int(config["training"]["batch_size"])
LEARNING_RATE = float(config["training"]["learning_rate"])

SAVE_CHECKPOINT_EVERY = int(config["logging"]["save_checkpoint_every"])
CHECKPOINT_DIR = str(config["logging"]["checkpoint_dir"])

# Load Pretraining dataset
#train_dataset = LIBRISPEECH("./dataset/", url="train-clean-100", download=False)
#val_dataset = LIBRISPEECH("./dataset/", url="dev-clean", download=False)
#val_dataset = Subset(val_dataset, list(range(1000)))

dataset = BulgarianSpeechDataset("./dist/finetuning/wavs")

train_dataset, val_dataset = data_split(dataset)

# Crate Dataloders
train_dataloader = DataLoader(train_dataset, BATCH_SIZE, True, collate_fn=collate_fn)
val_dataloader = DataLoader(val_dataset, BATCH_SIZE, False, collate_fn=collate_fn)

print("[INFO] All data loaders have been successfully initialized.")


model = Wav2Vec(MODEL_DIMENSIONS).to(DEVICE)
optimizer = torch.optim.Adam(model.parameters(), LEARNING_RATE)
loss_fn = Loss()
scheduler = torch.optim.lr_scheduler.StepLR(optimizer, step_size=5, gamma=0.5)

checkpoint_path = "./checkpoints/wav2vec-mini/wav2vec-mini-pretrained.pt"
checkpoint = load_pretrained(model, optimizer, scheduler, checkpoint_path)
start_epoch = checkpoint['epoch']
train_loss = checkpoint["train_loss"]
val_loss = checkpoint["val_loss"]
print(f"Train loss: {train_loss} | Val loss: {val_loss}")
train_step(model, config["training"]["epochs"], optimizer, loss_fn, scheduler, train_dataloader, val_dataloader, DEVICE, MODEL_NAME, SAVE_CHECKPOINT_EVERY, CHECKPOINT_DIR, 0)