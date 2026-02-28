"""
Spoiler detection service — bridges the API layer with the ML inference pipeline.
"""


class SpoilerResult:
    def __init__(self, overall_score: float, is_spoiler: bool, spans: list[dict]):
        self.overall_score = overall_score
        self.is_spoiler = is_spoiler
        self.spans = spans


_pipeline = None


def get_spoiler_pipeline():
    """Lazy-load the spoiler detection model."""
    global _pipeline
    if _pipeline is None:
        # TODO: Load the fine-tuned BERT model from model_registry
        # from services.ml.src.inference.spoiler_pipeline import SpoilerDetectionPipeline
        # _pipeline = SpoilerDetectionPipeline(settings.spoiler_model_path, settings.ml_device)
        _pipeline = _MockPipeline()
    return _pipeline


async def detect_spoilers(text: str, movie_title: str | None = None) -> SpoilerResult:
    """
    Run spoiler detection on text.

    For MVP without a trained model, returns a placeholder result.
    Once the model is trained (Phase 3), this will call the real pipeline.
    """
    pipeline = get_spoiler_pipeline()
    result = pipeline.detect(text, movie_title)
    return SpoilerResult(
        overall_score=result["overall_score"],
        is_spoiler=result["is_spoiler"],
        spans=result["spans"],
    )


class _MockPipeline:
    """Placeholder pipeline until the real BERT model is trained."""

    SPOILER_KEYWORDS = [
        "dies", "death", "killed", "murder", "ending", "twist",
        "reveals", "revealed", "turns out", "plot twist",
        "final scene", "climax", "secretly", "was actually",
    ]

    def detect(self, text: str, movie_title: str | None = None) -> dict:
        text_lower = text.lower()
        spans = []
        max_score = 0.0

        for keyword in self.SPOILER_KEYWORDS:
            start = 0
            while True:
                idx = text_lower.find(keyword, start)
                if idx == -1:
                    break
                score = 0.75
                max_score = max(max_score, score)
                spans.append({
                    "start": idx,
                    "end": idx + len(keyword),
                    "score": score,
                    "text": text[idx:idx + len(keyword)],
                })
                start = idx + 1

        return {
            "overall_score": max_score,
            "is_spoiler": max_score >= 0.7,
            "spans": spans,
        }
