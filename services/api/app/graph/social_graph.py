"""
Business logic for Neo4j social graph operations.
"""
from app.graph.driver import get_neo4j_driver
from app.graph import queries


async def sync_user_to_graph(user_id: str, username: str, display_name: str | None = None):
    driver = await get_neo4j_driver()
    async with driver.session() as session:
        await session.run(
            queries.UPSERT_USER,
            id=user_id, username=username, display_name=display_name or username,
        )


async def sync_rating_to_graph(user_id: str, movie_id: str, score: float, created_at: str):
    driver = await get_neo4j_driver()
    async with driver.session() as session:
        await session.run(
            queries.UPSERT_RATING,
            user_id=user_id, movie_id=movie_id, score=score, created_at=created_at,
        )


async def create_watched_with_edge(
    user_id: str, tagged_user_id: str, movie_id: str, review_id: str, date: str
):
    driver = await get_neo4j_driver()
    async with driver.session() as session:
        await session.run(
            queries.CREATE_WATCHED_WITH,
            user_id=user_id, tagged_user_id=tagged_user_id,
            movie_id=movie_id, review_id=review_id,
            confirmed=False, date=date,
        )


async def get_social_recommendations(user_id: str, limit: int = 20) -> list[dict]:
    driver = await get_neo4j_driver()
    async with driver.session() as session:
        result = await session.run(
            queries.WATCHED_WITH_RECOMMENDATIONS,
            user_id=user_id, limit=limit,
        )
        return [dict(record) async for record in result]


async def get_social_proximity(user_id: str, author_id: str) -> float:
    """Returns a 0.0-1.0 proximity score based on graph distance."""
    driver = await get_neo4j_driver()
    async with driver.session() as session:
        result = await session.run(
            queries.SOCIAL_PROXIMITY,
            user_id=user_id, author_id=author_id,
        )
        record = await result.single()
        if record is None:
            return 0.0
        distance = record["social_distance"]
        return 1.0 / (1.0 + distance)
