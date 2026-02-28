# Import all models so SQLAlchemy registers them
from app.models.user import User  # noqa: F401
from app.models.movie import Movie  # noqa: F401
from app.models.rating import Rating  # noqa: F401
from app.models.review import Review  # noqa: F401
from app.models.chat import ChatConversation, ChatMessage  # noqa: F401
from app.models.duo_match import DuoMatchSession, DuoMatchTempDMIndex  # noqa: F401
from app.models.watched_with import WatchedWith  # noqa: F401
