# CineSocial — System Architecture

## Overview

CineSocial is an AI-native film social media platform combining granular film discovery with TikTok-style UX and machine learning-powered features. Built as a monorepo with cross-platform frontends, a FastAPI backend, and self-hosted ML models.

## High-Level Architecture

```
┌─────────────┐  ┌─────────────┐
│  Next.js 15  │  │ React Native│
│   (Web)      │  │  (Expo)     │
└──────┬───────┘  └──────┬──────┘
       │                 │
       │   REST / WS     │
       └────────┬────────┘
                │
       ┌────────▼────────┐
       │   FastAPI        │
       │   (Python 3.12+) │
       └──┬──┬──┬──┬─────┘
          │  │  │  │
   ┌──────┘  │  │  └──────┐
   ▼         ▼  ▼         ▼
SQLite    Neo4j Qdrant  Redis
(dev)/    Graph Vector  Cache/
Postgres  DB    DB      Queue
(prod)
```

## Monorepo Structure

```
movie-social-media/
├── apps/
│   ├── web/          # Next.js 15 (App Router + Turbopack)
│   └── mobile/       # React Native (Expo SDK 52+)
├── packages/
│   ├── ui/           # Cross-platform UI components
│   ├── shared/       # Zod schemas, types, constants
│   ├── api-client/   # Generated TypeScript API client
│   └── config/       # ESLint, TypeScript, Prettier configs
├── services/
│   ├── api/          # FastAPI backend
│   └── ml/           # PyTorch ML models + training
├── infra/
│   └── docker-compose.yml  # Neo4j + Qdrant + Redis
└── docs/             # Architecture documentation
```

## Technology Stack

| Layer | Technology | Purpose |
|---|---|---|
| Build System | Turborepo + pnpm | Monorepo orchestration |
| Web | Next.js 15 + Tailwind | Server-rendered web app |
| Mobile | Expo SDK 52+ | Cross-platform mobile |
| Backend | FastAPI + Pydantic v2 | REST API + WebSocket |
| Primary DB | SQLAlchemy + Alembic | Relational data |
| Graph DB | Neo4j 5 Community | Social graph queries |
| Vector DB | Qdrant | Embedding similarity search |
| ML | PyTorch 2.x + HuggingFace | Spoiler detection, recommendations |
| Embeddings | all-MiniLM-L6-v2 (384d) | Text → vector encoding |
| Auth | JWT + OAuth2 | Token-based authentication |
| Task Queue | Celery + Redis | Background jobs |

## Core Features

### 1. TikTok-Style Vertical Feed
Full-screen snap-scroll feed of video reviews with engagement overlays, rating badges, and spoiler blur.

### 2. 10-Point Granular Rating System
Decimal ratings (0.0–10.0, step 0.1) as primary signal for the recommendation engine. Color-coded from red (low) through yellow to green (high).

### 3. AI Film Companion Chat
WebSocket-based conversational AI with multimodal RAG pulling context from movie, review, and chat embedding collections. Supports "Publish to Feed" to share AI conversations.

### 4. Duo-Match Recommendations
Mutual-consent AI feature that analyzes DM preference signals (not raw messages) between two users to suggest movies both would enjoy. Uses joint-utility scoring with Pareto fairness.

### 5. "Watched With" Social Tagging
Tag friends on reviews, creating Neo4j graph edges that influence recommendation diversity and social proximity scoring.

### 6. NLP Spoiler Detection
Dual-head BERT classifier providing both sequence-level (is this a spoiler?) and token-level (which words are spoilers?) predictions. Applied automatically to all reviews.

## Database Architecture

See [DATABASE.md](./DATABASE.md) for full schema documentation.

## ML Model Details

See [SPOILER_DETECTION.md](./SPOILER_DETECTION.md) and [DUO_MATCH_DESIGN.md](./DUO_MATCH_DESIGN.md).

## Development Setup

```bash
# Install frontend dependencies
pnpm install

# Install backend dependencies
cd services/api && python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"

# Start infrastructure
cd infra && docker compose up -d

# Start dev servers
pnpm --filter web dev     # Next.js on :3000
pnpm --filter mobile dev  # Expo on :8081
cd services/api && .venv/bin/python -m uvicorn app.main:app --reload --port 8000
```

## API Endpoints

| Method | Path | Description |
|---|---|---|
| POST | /api/v1/auth/register | Create account |
| POST | /api/v1/auth/login | Get JWT token |
| GET | /api/v1/users/me | Current user profile |
| GET | /api/v1/movies/ | Search movies |
| GET | /api/v1/movies/{id} | Movie detail |
| POST | /api/v1/ratings/ | Submit/update rating |
| GET | /api/v1/ratings/movie/{id} | Movie rating aggregate |
| POST | /api/v1/reviews/ | Create review |
| GET | /api/v1/feed/ | Paginated feed |
| WS | /api/v1/chat/ws/{id} | AI chat WebSocket |
| POST | /api/v1/duo-match/initiate | Start Duo-Match |
| POST | /api/v1/duo-match/{id}/consent | Give consent |
| POST | /api/v1/duo-match/{id}/revoke | Revoke consent |
