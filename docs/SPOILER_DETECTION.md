# CineSocial — Spoiler Detection System

## Model Architecture: Dual-Head BERT

The spoiler classifier uses `bert-base-uncased` (110M parameters) with two classification heads:

```
Input text
    │
    ▼
BERT Encoder (12 layers, 768d)
    │
    ├── [CLS] token ─────────────────────── Sequence Head
    │   FC(768,256) → ReLU → Dropout(0.3)    │
    │   → FC(256,2) → Softmax                │
    │   Output: P(spoiler) binary             │
    │                                         │
    └── All tokens ──────────────────────── Token Head
        FC(768,256) → ReLU → Dropout(0.3)    │
        → FC(256,2) → Softmax                │
        Output: Per-token BIO labels          │
```

### Why Dual-Head?

1. **Sequence head**: Answers "Is this review a spoiler?" — binary classification on the [CLS] representation. Used to set `is_spoiler` flag and `spoiler_score`.

2. **Token head**: Answers "Which specific words/spans are spoilers?" — per-token classification identifying exact spoiler regions. Used to generate `spoiler_spans` for granular blur overlay.

### Loss Function

```
L = 0.6 * CrossEntropy(sequence_logits, sequence_labels)
  + 0.4 * CrossEntropy(token_logits, token_labels, mask=attention_mask)
```

The 60/40 weighting prioritizes whole-review classification (higher recall for safety) while still learning span boundaries.

## Training

### Dataset
- IMDB Spoiler Dataset + Goodreads spoiler reviews
- Labels: binary sequence label + token-level BIO annotations
- Train/val split: 80/20 stratified

### Hyperparameters
| Parameter | Value |
|---|---|
| Learning rate | 2e-5 |
| Batch size | 16 |
| Max sequence length | 512 |
| Epochs | 3–5 |
| Optimizer | AdamW (weight_decay=0.01) |
| Scheduler | Linear warmup (10% of steps) |
| Dropout | 0.3 |

### Target Metrics
- Sequence F1 > 0.85
- Token F1 > 0.75
- Precision prioritized over recall for span detection (avoid over-blurring)

## Inference Pipeline

```
Review text
    │
    ▼
Pre-process (clean, truncate to 512 tokens)
    │
    ▼
BERT Tokenizer (with offset mapping for span alignment)
    │
    ▼
Forward pass (both heads)
    │
    ├── Sequence softmax → threshold at 0.7 → is_spoiler bool
    │
    └── Token softmax → threshold at 0.5 → extract spans
        │
        ▼
    Merge adjacent spans (< 3 token gap)
        │
        ▼
    Map token offsets → character offsets
        │
        ▼
    Output: SpoilerResult(score, is_spoiler, spans[])
```

### Performance
- ~50–100ms on CPU for single review (acceptable for MVP)
- Runs synchronously in the request path during review creation

## Frontend Integration

The `SpoilerBlur` component wraps review text:

```tsx
<SpoilerBlur isRevealed={revealed} onReveal={() => setRevealed(true)}>
  <ReviewText spans={review.spoiler_spans} />
</SpoilerBlur>
```

- Non-spoiler reviews: rendered normally
- Spoiler reviews: text blurred with "Contains Spoilers — Tap to Reveal" overlay
- Granular mode: only spoiler spans are blurred, rest is readable

## Current Status

The production model requires training data and GPU time. The current implementation uses a **keyword-based mock** (`services/api/app/services/spoiler_service.py`) that matches common spoiler phrases as a development placeholder.
