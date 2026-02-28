from pydantic import BaseModel


class SpoilerDetectRequest(BaseModel):
    text: str
    movie_id: str | None = None


class SpoilerSpanResult(BaseModel):
    start: int
    end: int
    score: float
    text: str


class SpoilerDetectResponse(BaseModel):
    overall_score: float
    is_spoiler: bool
    spans: list[SpoilerSpanResult]
