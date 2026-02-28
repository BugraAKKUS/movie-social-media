"""
Cypher query templates for Neo4j social graph operations.
"""

# ─── Node Sync ───────────────────────────────────────────────

UPSERT_USER = """
MERGE (u:User {id: $id})
SET u.username = $username, u.display_name = $display_name
RETURN u
"""

UPSERT_MOVIE = """
MERGE (m:Movie {id: $id})
SET m.title = $title, m.tmdb_id = $tmdb_id,
    m.genres = $genres, m.release_year = $release_year
RETURN m
"""

# ─── Rating Edge ─────────────────────────────────────────────

UPSERT_RATING = """
MATCH (u:User {id: $user_id}), (m:Movie {id: $movie_id})
MERGE (u)-[r:RATED]->(m)
SET r.score = $score, r.created_at = datetime($created_at)
RETURN r
"""

# ─── Watched With ────────────────────────────────────────────

CREATE_WATCHED_WITH = """
MATCH (u1:User {id: $user_id}), (u2:User {id: $tagged_user_id})
MERGE (u1)-[w:WATCHED_WITH {movie_id: $movie_id}]->(u2)
SET w.review_id = $review_id, w.confirmed = $confirmed, w.date = datetime($date)
RETURN w
"""

CONFIRM_WATCHED_WITH = """
MATCH (u1:User {id: $user_id})-[w:WATCHED_WITH {review_id: $review_id}]->(u2:User {id: $tagged_user_id})
SET w.confirmed = true
RETURN w
"""

# ─── Social Recommendations ─────────────────────────────────

WATCHED_WITH_RECOMMENDATIONS = """
MATCH (me:User {id: $user_id})-[:WATCHED_WITH]->(friend:User)-[r:RATED]->(movie:Movie)
WHERE NOT (me)-[:RATED]->(movie)
  AND friend.id <> me.id
WITH movie, AVG(r.score) AS avg_friend_score, COUNT(DISTINCT friend) AS friend_count
RETURN movie.id AS movie_id, movie.title AS title,
       avg_friend_score, friend_count
ORDER BY friend_count DESC, avg_friend_score DESC
LIMIT $limit
"""

# ─── Social Proximity ───────────────────────────────────────

SOCIAL_PROXIMITY = """
MATCH path = shortestPath(
    (me:User {id: $user_id})-[:FOLLOWS|WATCHED_WITH*1..3]-(author:User {id: $author_id})
)
RETURN length(path) AS social_distance,
       SIZE([(me)-[:WATCHED_WITH]-(author) | 1]) AS direct_watch_count
"""

# ─── Duo-Match: Genre Overlap ───────────────────────────────

DUO_MATCH_GENRE_OVERLAP = """
MATCH (u1:User {id: $user1_id})-[r1:RATED]->(m:Movie)<-[r2:RATED]-(u2:User {id: $user2_id})
WHERE r1.score >= 7.0 AND r2.score >= 7.0
WITH m, r1.score AS score1, r2.score AS score2
RETURN m.genres AS genres,
       COUNT(m) AS co_liked_count,
       AVG(score1) AS avg_score_user1,
       AVG(score2) AS avg_score_user2
ORDER BY co_liked_count DESC
"""

# ─── Follow ─────────────────────────────────────────────────

CREATE_FOLLOW = """
MATCH (u1:User {id: $follower_id}), (u2:User {id: $followed_id})
MERGE (u1)-[f:FOLLOWS]->(u2)
SET f.since = datetime()
RETURN f
"""

REMOVE_FOLLOW = """
MATCH (u1:User {id: $follower_id})-[f:FOLLOWS]->(u2:User {id: $followed_id})
DELETE f
"""
