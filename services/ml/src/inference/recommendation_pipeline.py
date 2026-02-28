"""
Recommendation inference pipeline.

Handles:
1. Single-user recommendations via content + collaborative filtering
2. Duo-Match joint recommendations via joint-utility scoring
3. DM preference extraction for Duo-Match
"""
import re
from collections import Counter


# ─── DM Preference Extraction ───────────────────────────────

GENRE_KEYWORDS = {
    "action": ["action", "fight", "explosion", "chase", "stunts"],
    "comedy": ["comedy", "funny", "hilarious", "laugh", "humor"],
    "drama": ["drama", "emotional", "moving", "powerful", "intense"],
    "horror": ["horror", "scary", "terrifying", "creepy", "nightmare"],
    "sci-fi": ["sci-fi", "science fiction", "space", "future", "alien"],
    "romance": ["romance", "love", "romantic", "relationship"],
    "thriller": ["thriller", "suspense", "tension", "edge of seat", "gripping"],
    "animation": ["animation", "animated", "pixar", "anime", "cartoon"],
    "documentary": ["documentary", "real story", "true story", "non-fiction"],
}

MOOD_KEYWORDS = {
    "feel-good": ["feel good", "uplifting", "heartwarming", "wholesome", "happy"],
    "intense": ["intense", "gripping", "edge of seat", "nail-biting"],
    "thought-provoking": ["thought provoking", "deep", "philosophical", "makes you think"],
    "dark": ["dark", "disturbing", "bleak", "grim", "heavy"],
    "fun": ["fun", "entertaining", "enjoyable", "good time", "popcorn"],
    "emotional": ["emotional", "cry", "tears", "moving", "touching"],
}


def extract_dm_preferences(messages: list[str]) -> dict:
    """
    Extract preference signals from DM messages.
    Returns structured signals WITHOUT storing raw messages.

    This is the privacy-preserving extraction step:
    raw text in → structured signals out → raw text discarded.
    """
    text = " ".join(messages).lower()

    # Extract genre preferences
    genre_scores: Counter = Counter()
    for genre, keywords in GENRE_KEYWORDS.items():
        for kw in keywords:
            count = text.count(kw)
            if count > 0:
                genre_scores[genre] += count

    # Extract mood preferences
    mood_scores: Counter = Counter()
    for mood, keywords in MOOD_KEYWORDS.items():
        for kw in keywords:
            count = text.count(kw)
            if count > 0:
                mood_scores[mood] += count

    # Extract movie title mentions (simple heuristic: capitalized multi-word phrases)
    mentioned_titles = re.findall(
        r'\b[A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)+\b',
        " ".join(messages),  # Use original case
    )

    return {
        "genres": dict(genre_scores),
        "moods": dict(mood_scores),
        "mentions": list(set(mentioned_titles))[:20],  # Cap at 20 mentions
    }


def compute_dm_signal_vector(
    user1_prefs: dict, user2_prefs: dict, embedder
) -> list[float]:
    """
    Compute a shared preference vector from two users' extracted DM signals.

    dm_preference_vec = normalize(
        topic_vec(shared_genres) + mood_vec(shared_moods) + entity_vec(co_mentions)
    )
    """
    # Find shared genre interests
    shared_genres = set(user1_prefs.get("genres", {})) & set(user2_prefs.get("genres", {}))

    # Find shared mood preferences
    shared_moods = set(user1_prefs.get("moods", {})) & set(user2_prefs.get("moods", {}))

    # Find co-mentioned movies
    co_mentions = set(user1_prefs.get("mentions", [])) & set(user2_prefs.get("mentions", []))

    # Build a text summary of shared preferences
    parts = []
    if shared_genres:
        parts.append(f"Genres: {', '.join(shared_genres)}")
    if shared_moods:
        parts.append(f"Mood: {', '.join(shared_moods)}")
    if co_mentions:
        parts.append(f"Movies mentioned: {', '.join(list(co_mentions)[:5])}")

    if not parts:
        return [0.0] * 384  # No shared signal

    text = ". ".join(parts)
    return embedder.embed_query(text).tolist()
