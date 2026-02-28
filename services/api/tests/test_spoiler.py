import pytest
from app.services.spoiler_service import detect_spoilers


@pytest.mark.asyncio
async def test_spoiler_detection_positive():
    """Test that spoiler keywords are detected."""
    text = "In the ending, the main character dies in the final scene."
    result = await detect_spoilers(text, movie_title="Test Movie")

    assert result.is_spoiler is True
    assert result.overall_score >= 0.7
    assert len(result.spans) > 0

    span_texts = [s["text"] for s in result.spans]
    assert "ending" in span_texts
    assert "dies" in span_texts


@pytest.mark.asyncio
async def test_spoiler_detection_negative():
    """Test that non-spoiler text is not flagged."""
    text = "This movie has great cinematography and an amazing soundtrack."
    result = await detect_spoilers(text)

    assert result.is_spoiler is False
    assert result.overall_score < 0.7
    assert len(result.spans) == 0


@pytest.mark.asyncio
async def test_spoiler_spans_have_correct_offsets():
    """Test that spoiler spans point to correct text positions."""
    text = "The twist reveals everything"
    result = await detect_spoilers(text)

    for span in result.spans:
        assert text[span["start"]:span["end"]] == span["text"]
