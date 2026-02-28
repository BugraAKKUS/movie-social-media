"""
Dual-head BERT model for spoiler detection.

Head 1 (sequence-level): Binary classification — P(spoiler | review)
Head 2 (token-level): Per-token spoiler probability for span highlighting

Architecture:
    Input -> BERT Encoder (12 layers, 768 hidden)
        -> [CLS] -> FC(768, 256) -> ReLU -> Dropout(0.3) -> FC(256, 2)  [sequence]
        -> All tokens -> FC(768, 256) -> ReLU -> Dropout(0.3) -> FC(256, 2)  [token]
"""
import torch
import torch.nn as nn
from transformers import BertModel, BertPreTrainedModel, BertConfig


class SpoilerClassifier(BertPreTrainedModel):
    config_class = BertConfig

    def __init__(self, config: BertConfig):
        super().__init__(config)
        self.bert = BertModel(config)
        self.dropout = nn.Dropout(0.3)

        # Sequence-level spoiler classification: [CLS] -> 2 classes
        self.sequence_classifier = nn.Sequential(
            nn.Linear(config.hidden_size, 256),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(256, 2),  # [not_spoiler, spoiler]
        )

        # Token-level spoiler span detection: each token -> 2 classes
        self.token_classifier = nn.Sequential(
            nn.Linear(config.hidden_size, 256),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(256, 2),  # [not_spoiler_token, spoiler_token]
        )

        self.post_init()

    def forward(
        self,
        input_ids: torch.Tensor,
        attention_mask: torch.Tensor | None = None,
        token_type_ids: torch.Tensor | None = None,
        sequence_labels: torch.Tensor | None = None,
        token_labels: torch.Tensor | None = None,
    ) -> dict:
        outputs = self.bert(
            input_ids,
            attention_mask=attention_mask,
            token_type_ids=token_type_ids,
        )

        # Sequence-level: [CLS] token representation
        cls_output = outputs.last_hidden_state[:, 0, :]  # (batch, 768)
        sequence_logits = self.sequence_classifier(self.dropout(cls_output))

        # Token-level: all token representations
        token_output = outputs.last_hidden_state  # (batch, seq_len, 768)
        token_logits = self.token_classifier(self.dropout(token_output))

        loss = None
        if sequence_labels is not None and token_labels is not None:
            loss_fn = nn.CrossEntropyLoss()

            # Sequence loss
            seq_loss = loss_fn(sequence_logits, sequence_labels)

            # Token loss (masked to ignore padding)
            active_loss = attention_mask.view(-1) == 1
            active_logits = token_logits.view(-1, 2)[active_loss]
            active_labels = token_labels.view(-1)[active_loss]
            token_loss = loss_fn(active_logits, active_labels)

            # Combined loss: sequence classification weighted higher
            loss = 0.6 * seq_loss + 0.4 * token_loss

        return {
            "loss": loss,
            "sequence_logits": sequence_logits,  # (batch, 2)
            "token_logits": token_logits,  # (batch, seq_len, 2)
        }
