"""
Real-time spoiler detection inference pipeline.

Takes raw review text → BERT tokenization → dual-head forward pass →
character-level spoiler span extraction.
"""
import torch
from transformers import BertTokenizerFast
from typing import TypedDict

from services.ml.src.models.spoiler_classifier import SpoilerClassifier


class SpoilerSpan(TypedDict):
    start: int
    end: int
    score: float
    text: str


class SpoilerResult(TypedDict):
    overall_score: float
    is_spoiler: bool
    spans: list[SpoilerSpan]


class SpoilerDetectionPipeline:
    SEQUENCE_THRESHOLD = 0.7
    TOKEN_THRESHOLD = 0.5
    MIN_SPAN_LENGTH = 3

    def __init__(self, model_path: str, device: str = "cpu"):
        self.device = torch.device(device)
        self.tokenizer = BertTokenizerFast.from_pretrained(model_path)
        self.model = SpoilerClassifier.from_pretrained(model_path)
        self.model.to(self.device)
        self.model.eval()

    @torch.no_grad()
    def detect(self, text: str, movie_title: str | None = None) -> SpoilerResult:
        # Prepend movie context for named entity awareness
        if movie_title:
            input_text = f"[Movie: {movie_title}] {text}"
            offset_adjust = len(f"[Movie: {movie_title}] ")
        else:
            input_text = text
            offset_adjust = 0

        # Tokenize with offset mapping
        encoding = self.tokenizer(
            input_text,
            max_length=512,
            truncation=True,
            padding="max_length",
            return_tensors="pt",
            return_offsets_mapping=True,
        )

        offset_mapping = encoding.pop("offset_mapping")[0]
        input_ids = encoding["input_ids"].to(self.device)
        attention_mask = encoding["attention_mask"].to(self.device)

        outputs = self.model(input_ids=input_ids, attention_mask=attention_mask)

        # Sequence-level probability
        seq_probs = torch.softmax(outputs["sequence_logits"], dim=-1)
        overall_score = seq_probs[0, 1].item()

        # Token-level probabilities
        token_probs = torch.softmax(outputs["token_logits"], dim=-1)
        token_spoiler_probs = token_probs[0, :, 1].cpu().numpy()

        # Extract character-level spoiler spans
        spans = self._extract_spans(
            text, token_spoiler_probs, offset_mapping.numpy(), offset_adjust
        )

        return SpoilerResult(
            overall_score=round(overall_score, 4),
            is_spoiler=overall_score >= self.SEQUENCE_THRESHOLD,
            spans=spans,
        )

    def _extract_spans(
        self, original_text: str, token_probs, offset_mapping, offset_adjust: int
    ) -> list[SpoilerSpan]:
        """Merge consecutive spoiler tokens into character-level spans."""
        spans: list[SpoilerSpan] = []
        current_start: int | None = None
        current_scores: list[float] = []
        prev_end = 0

        for prob, (char_start, char_end) in zip(token_probs, offset_mapping):
            char_start, char_end = int(char_start), int(char_end)

            # Skip special tokens and padding
            if char_start == 0 and char_end == 0:
                if current_start is not None:
                    self._close_span(
                        spans, original_text, current_start, prev_end,
                        current_scores, offset_adjust,
                    )
                    current_start = None
                    current_scores = []
                continue

            if prob >= self.TOKEN_THRESHOLD:
                if current_start is None:
                    current_start = char_start
                current_scores.append(float(prob))
                prev_end = char_end
            else:
                if current_start is not None:
                    self._close_span(
                        spans, original_text, current_start, prev_end,
                        current_scores, offset_adjust,
                    )
                    current_start = None
                    current_scores = []

        if current_start is not None:
            self._close_span(
                spans, original_text, current_start, prev_end,
                current_scores, offset_adjust,
            )

        return spans

    def _close_span(
        self, spans, original_text, start, end, scores, offset_adjust
    ):
        adjusted_start = max(0, start - offset_adjust)
        adjusted_end = max(0, end - offset_adjust)

        if adjusted_end - adjusted_start >= self.MIN_SPAN_LENGTH:
            span_text = original_text[adjusted_start:adjusted_end]
            spans.append(SpoilerSpan(
                start=adjusted_start,
                end=adjusted_end,
                score=round(max(scores), 4),
                text=span_text,
            ))
