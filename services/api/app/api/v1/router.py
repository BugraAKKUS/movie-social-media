from fastapi import APIRouter

from app.api.v1.endpoints import (
    auth,
    users,
    movies,
    ratings,
    reviews,
    feed,
    chat,
    duo_match,
    watched_with,
)

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(movies.router, prefix="/movies", tags=["movies"])
api_router.include_router(ratings.router, prefix="/ratings", tags=["ratings"])
api_router.include_router(reviews.router, prefix="/reviews", tags=["reviews"])
api_router.include_router(feed.router, prefix="/feed", tags=["feed"])
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])
api_router.include_router(duo_match.router, prefix="/duo-match", tags=["duo-match"])
api_router.include_router(watched_with.router, prefix="/watched-with", tags=["watched-with"])
