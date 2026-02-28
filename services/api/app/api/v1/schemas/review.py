from pydantic import BaseModel


class SpoilerSpanResponse(BaseModel):
    start: int
    end: int
    score: float
    text: str


class CreateReviewRequest(BaseModel):
    movie_id: str
    content_text: str | None = None
    video_url: str | None = None
    watched_with_user_ids: list[str] | None = None


class ReviewResponse(BaseModel):
    id: str
    user_id: str
    movie_id: str
    content_text: str | None = None
    video_url: str | None = None
    spoiler_score: float
    is_spoiler: bool
    spoiler_spans: list[SpoilerSpanResponse]
    published_from_chat: bool
    like_count: int
    comment_count: int
    view_count: int
    created_at: str

    model_config = {"from_attributes": True}
