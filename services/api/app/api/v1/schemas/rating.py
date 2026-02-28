from pydantic import BaseModel, Field


class CreateRatingRequest(BaseModel):
    movie_id: str
    score: float = Field(ge=0.0, le=10.0, description="Rating on 10-point scale (0.0-10.0)")


class UpdateRatingRequest(BaseModel):
    score: float = Field(ge=0.0, le=10.0)


class RatingResponse(BaseModel):
    id: str
    user_id: str
    movie_id: str
    score: float
    created_at: str
    updated_at: str

    model_config = {"from_attributes": True}


class MovieRatingAggregateResponse(BaseModel):
    avg_score: float
    count: int
    user_rating: float | None = None
