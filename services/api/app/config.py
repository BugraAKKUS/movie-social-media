from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # App
    app_name: str = "CineSocial API"
    debug: bool = True

    # Database
    database_url: str = "sqlite+aiosqlite:///./cinesocial.db"

    # Auth
    secret_key: str = "change-me-to-a-random-secret-key"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # TMDB
    tmdb_api_key: str = ""

    # Neo4j
    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = "cinesocial-dev"

    # Qdrant
    qdrant_host: str = "localhost"
    qdrant_port: int = 6333

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # ML
    ml_device: str = "cpu"
    spoiler_model_path: str = "services/ml/model_registry/spoiler_classifier"
    embedding_model_name: str = "sentence-transformers/all-MiniLM-L6-v2"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
