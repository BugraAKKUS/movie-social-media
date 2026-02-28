"""
Training script for the dual-head BERT spoiler classifier.

Usage:
    python -m services.ml.src.training.train_spoiler \
        --dataset_path data/processed/spoiler_train.json \
        --output_dir model_registry/spoiler_classifier \
        --epochs 3 \
        --batch_size 16 \
        --learning_rate 2e-5

Dataset format (JSON lines):
    {"text": "review text...", "is_spoiler": true, "spoiler_spans": [[start, end], ...]}
"""
import argparse
import json
from pathlib import Path

import torch
from torch.utils.data import Dataset, DataLoader
from torch.optim import AdamW
from transformers import BertTokenizerFast, get_linear_schedule_with_warmup
from sklearn.metrics import f1_score, precision_score, recall_score

from services.ml.src.models.spoiler_classifier import SpoilerClassifier


class SpoilerDataset(Dataset):
    def __init__(self, data: list[dict], tokenizer: BertTokenizerFast, max_length: int = 512):
        self.data = data
        self.tokenizer = tokenizer
        self.max_length = max_length

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        item = self.data[idx]
        text = item["text"]
        is_spoiler = item["is_spoiler"]
        spoiler_spans = item.get("spoiler_spans", [])

        # Tokenize with offset mapping
        encoding = self.tokenizer(
            text,
            max_length=self.max_length,
            truncation=True,
            padding="max_length",
            return_tensors="pt",
            return_offsets_mapping=True,
        )

        input_ids = encoding["input_ids"].squeeze()
        attention_mask = encoding["attention_mask"].squeeze()
        offset_mapping = encoding["offset_mapping"].squeeze()

        # Sequence label
        sequence_label = 1 if is_spoiler else 0

        # Token labels from character-level spans
        token_labels = torch.zeros(self.max_length, dtype=torch.long)
        for start, end in spoiler_spans:
            for i, (tok_start, tok_end) in enumerate(offset_mapping):
                tok_start, tok_end = tok_start.item(), tok_end.item()
                if tok_start == 0 and tok_end == 0:
                    continue
                if tok_start >= start and tok_end <= end:
                    token_labels[i] = 1

        return {
            "input_ids": input_ids,
            "attention_mask": attention_mask,
            "sequence_labels": torch.tensor(sequence_label, dtype=torch.long),
            "token_labels": token_labels,
        }


def train(args):
    device = torch.device(args.device)

    # Load dataset
    with open(args.dataset_path) as f:
        data = [json.loads(line) for line in f]

    # Split 90/10
    split_idx = int(len(data) * 0.9)
    train_data, val_data = data[:split_idx], data[split_idx:]

    # Initialize tokenizer and model
    tokenizer = BertTokenizerFast.from_pretrained("bert-base-uncased")
    model = SpoilerClassifier.from_pretrained("bert-base-uncased")
    model.to(device)

    # Datasets
    train_dataset = SpoilerDataset(train_data, tokenizer)
    val_dataset = SpoilerDataset(val_data, tokenizer)
    train_loader = DataLoader(train_dataset, batch_size=args.batch_size, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=args.batch_size)

    # Optimizer and scheduler
    optimizer = AdamW(model.parameters(), lr=args.learning_rate, weight_decay=0.01)
    total_steps = len(train_loader) * args.epochs
    scheduler = get_linear_schedule_with_warmup(
        optimizer, num_warmup_steps=int(0.1 * total_steps), num_training_steps=total_steps
    )

    # Training loop
    best_f1 = 0.0
    for epoch in range(args.epochs):
        model.train()
        total_loss = 0.0

        for batch in train_loader:
            batch = {k: v.to(device) for k, v in batch.items()}
            outputs = model(
                input_ids=batch["input_ids"],
                attention_mask=batch["attention_mask"],
                sequence_labels=batch["sequence_labels"],
                token_labels=batch["token_labels"],
            )

            loss = outputs["loss"]
            loss.backward()

            torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
            optimizer.step()
            scheduler.step()
            optimizer.zero_grad()

            total_loss += loss.item()

        avg_loss = total_loss / len(train_loader)

        # Validation
        model.eval()
        all_preds, all_labels = [], []
        with torch.no_grad():
            for batch in val_loader:
                batch = {k: v.to(device) for k, v in batch.items()}
                outputs = model(
                    input_ids=batch["input_ids"],
                    attention_mask=batch["attention_mask"],
                )
                preds = outputs["sequence_logits"].argmax(dim=-1).cpu().tolist()
                labels = batch["sequence_labels"].cpu().tolist()
                all_preds.extend(preds)
                all_labels.extend(labels)

        f1 = f1_score(all_labels, all_preds)
        precision = precision_score(all_labels, all_preds)
        recall = recall_score(all_labels, all_preds)

        print(
            f"Epoch {epoch + 1}/{args.epochs} | "
            f"Loss: {avg_loss:.4f} | "
            f"F1: {f1:.4f} | P: {precision:.4f} | R: {recall:.4f}"
        )

        if f1 > best_f1:
            best_f1 = f1
            output_path = Path(args.output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
            model.save_pretrained(output_path)
            tokenizer.save_pretrained(output_path)
            print(f"  Saved best model (F1={f1:.4f}) to {output_path}")

    print(f"\nTraining complete. Best F1: {best_f1:.4f}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train spoiler classifier")
    parser.add_argument("--dataset_path", type=str, required=True)
    parser.add_argument("--output_dir", type=str, default="model_registry/spoiler_classifier")
    parser.add_argument("--epochs", type=int, default=3)
    parser.add_argument("--batch_size", type=int, default=16)
    parser.add_argument("--learning_rate", type=float, default=2e-5)
    parser.add_argument("--device", type=str, default="cpu")
    args = parser.parse_args()
    train(args)
