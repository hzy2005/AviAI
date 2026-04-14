from app.db.base import Base
from app.models import BirdRecord  # noqa: F401
from app.models import Comment  # noqa: F401
from app.models import Like  # noqa: F401
from app.models import Post  # noqa: F401
from app.models import User  # noqa: F401

__all__ = ["Base"]
