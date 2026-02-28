from app.db.session import engine, Base


async def on_startup():
    """Initialize database tables on startup."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def on_shutdown():
    """Clean up resources on shutdown."""
    await engine.dispose()
