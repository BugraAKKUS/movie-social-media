from pydantic import BaseModel


class InitiateDuoMatchRequest(BaseModel):
    partner_id: str


class DuoMatchConsentRequest(BaseModel):
    consent: bool


class DuoMatchSessionResponse(BaseModel):
    id: str
    initiator_id: str
    partner_id: str
    state: str
    initiator_consented_at: str | None = None
    partner_consented_at: str | None = None
    data_expiry_at: str | None = None
    recommendations_generated_at: str | None = None
    created_at: str

    model_config = {"from_attributes": True}


class DuoMatchRecommendationResponse(BaseModel):
    movie: dict  # {id, title, posterUrl, genres}
    joint_score: float
    compatibility_reason: str
    user1_predicted_rating: float
    user2_predicted_rating: float
