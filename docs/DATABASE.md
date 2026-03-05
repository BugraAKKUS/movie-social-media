# CineSocial — Database Schema

## Relational Database (SQLAlchemy)

### users
| Column | Type | Constraints |
|---|---|---|
| id | UUID | PK, default uuid4 |
| username | String(50) | UNIQUE, NOT NULL |
| email | String(255) | UNIQUE, NOT NULL |
| password_hash | String(255) | NOT NULL |
| display_name | String(100) | nullable |
| bio | Text | nullable |
| avatar_url | String(500) | nullable |
| preference_vector_id | String(100) | nullable (Qdrant point ID) |
| created_at | DateTime | default utcnow |
| updated_at | DateTime | auto-update |

### movies
| Column | Type | Constraints |
|---|---|---|
| id | UUID | PK |
| tmdb_id | Integer | UNIQUE, NOT NULL |
| title | String(500) | NOT NULL |
| overview | Text | nullable |
| release_date | Date | nullable |
| poster_url | String(500) | nullable |
| backdrop_url | String(500) | nullable |
| genres | JSON | default [] |
| cast_list | JSON | default [] |
| director | String(200) | nullable |
| runtime_minutes | Integer | nullable |
| avg_rating | Numeric(4,2) | default 0 |
| rating_count | Integer | default 0 |
| content_vector_id | String(100) | nullable (Qdrant point ID) |

### ratings
| Column | Type | Constraints |
|---|---|---|
| id | UUID | PK |
| user_id | UUID | FK → users.id, NOT NULL |
| movie_id | UUID | FK → movies.id, NOT NULL |
| score | Numeric(3,1) | CHECK 0.0–10.0 |
| created_at | DateTime | default utcnow |
| updated_at | DateTime | auto-update |
| | | UNIQUE(user_id, movie_id) |

### reviews
| Column | Type | Constraints |
|---|---|---|
| id | UUID | PK |
| user_id | UUID | FK → users.id |
| movie_id | UUID | FK → movies.id |
| content_text | Text | nullable |
| video_url | String(500) | nullable |
| spoiler_score | Numeric(5,4) | default 0.0 |
| is_spoiler | Boolean | default false |
| spoiler_spans | JSON | default [] |
| published_from_chat | Boolean | default false |
| like_count | Integer | default 0 |
| comment_count | Integer | default 0 |
| share_count | Integer | default 0 |
| created_at | DateTime | default utcnow |

### chat_conversations
| Column | Type | Constraints |
|---|---|---|
| id | UUID | PK |
| user_id | UUID | FK → users.id |
| movie_id | UUID | FK → movies.id, nullable |
| title | String(200) | nullable |
| created_at | DateTime | default utcnow |
| updated_at | DateTime | auto-update |

### chat_messages
| Column | Type | Constraints |
|---|---|---|
| id | UUID | PK |
| conversation_id | UUID | FK → chat_conversations.id |
| role | String(20) | "user" or "assistant" |
| content | Text | NOT NULL |
| rag_sources | JSON | nullable |
| published_review_id | UUID | FK → reviews.id, nullable |
| created_at | DateTime | default utcnow |

### duo_match_sessions
| Column | Type | Constraints |
|---|---|---|
| id | UUID | PK |
| initiator_id | UUID | FK → users.id |
| partner_id | UUID | FK → users.id |
| state | String(50) | FSM state (see below) |
| initiator_consented_at | DateTime | nullable |
| partner_consented_at | DateTime | nullable |
| data_expiry_at | DateTime | nullable |
| recommendations | JSON | nullable |
| created_at | DateTime | default utcnow |
| updated_at | DateTime | auto-update |

**State machine**: `pending_partner_consent` → `both_consented` → `analyzing` → `recommendations_ready` → `viewed` → `expired`. Any state → `declined` or `revoked`.

### duo_match_temp_dm_index
| Column | Type | Constraints |
|---|---|---|
| id | UUID | PK |
| session_id | UUID | FK → duo_match_sessions.id |
| user_id | UUID | FK → users.id |
| preference_signals | JSON | genres, moods, entities |
| created_at | DateTime | default utcnow |

Auto-deleted after session expires or is revoked.

### watched_with
| Column | Type | Constraints |
|---|---|---|
| id | UUID | PK |
| review_id | UUID | FK → reviews.id |
| user_id | UUID | FK → users.id (tagger) |
| tagged_user_id | UUID | FK → users.id (tagged) |
| confirmed | Boolean | default false |
| created_at | DateTime | default utcnow |
| | | UNIQUE(review_id, user_id, tagged_user_id) |

## Neo4j Graph Schema

### Nodes
- `(:User {id, username})`
- `(:Movie {id, tmdb_id, title})`
- `(:Review {id})`

### Relationships
| Relationship | From → To | Properties |
|---|---|---|
| `[:RATED]` | User → Movie | score (decimal) |
| `[:REVIEWED]` | User → Movie | — |
| `[:WATCHED]` | User → Movie | — |
| `[:FOLLOWS]` | User → User | — |
| `[:WATCHED_WITH]` | User → User | movie_id, confirmed |
| `[:LIKED]` | User → Review | — |
| `[:COMMENTED_ON]` | User → Review | — |
| `[:ABOUT]` | Review → Movie | — |
| `[:AUTHORED_BY]` | Review → User | — |

## Qdrant Vector Collections

All collections use 384-dimensional vectors with cosine distance (sentence-transformers/all-MiniLM-L6-v2).

| Collection | Payload Fields | Purpose |
|---|---|---|
| movie_embeddings | movie_id, genres[], year, avg_rating | Content-based movie search |
| user_preferences | user_id | User taste profile (weighted avg) |
| review_embeddings | review_id, movie_id, user_id, is_spoiler | RAG source for AI chat |
| chat_embeddings | conversation_id, user_id, message_id | Chat history for context |
