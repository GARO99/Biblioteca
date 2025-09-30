from sqlalchemy import func, select
from domain.repositories.base_repository import BaseRepository
from domain.entities.security.user import User

class UserRepository(BaseRepository[User]):
    def __init__(self, session): super().__init__(User, session)

    def find_by_email_ci(self, email: str) -> User | None:
        stmt = select(User).where(func.lower(User.email) == email.lower())
        return self.session.execute(stmt).scalar_one_or_none()
