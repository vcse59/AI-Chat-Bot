from sqlalchemy import Boolean, Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship, mapped_column, Mapped
from sqlalchemy.ext.hybrid import hybrid_property
from typing import List, Optional, TYPE_CHECKING
from ..database import Base

if TYPE_CHECKING:
    from .role import Role

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    _username: Mapped[str] = mapped_column("username", String, unique=True, index=True)
    _email: Mapped[str] = mapped_column("email", String, unique=True, index=True)
    _full_name: Mapped[Optional[str]] = mapped_column("full_name", String, nullable=True)
    _hashed_password: Mapped[str] = mapped_column("hashed_password", String)
    _is_active: Mapped[bool] = mapped_column("is_active", Boolean, default=True)
    _theme_preference: Mapped[str] = mapped_column("theme_preference", String, default="dark", nullable=False)
    roles: Mapped[List["Role"]] = relationship("Role", secondary="user_roles", back_populates="users")
    
    @hybrid_property
    def username(self) -> str:
        return self._username
        
    @username.setter
    def username(self, value: str) -> None:
        self._username = value
        
    @hybrid_property
    def email(self) -> str:
        return self._email
        
    @email.setter
    def email(self, value: str) -> None:
        self._email = value
        
    @hybrid_property
    def full_name(self) -> Optional[str]:
        return self._full_name
        
    @full_name.setter
    def full_name(self, value: Optional[str]) -> None:
        self._full_name = value
        
    @hybrid_property
    def hashed_password(self) -> str:
        return self._hashed_password
        
    @hashed_password.setter
    def hashed_password(self, value: str) -> None:
        self._hashed_password = value
        
    @hybrid_property
    def is_active(self) -> bool:
        return self._is_active
        
    @is_active.setter
    def is_active(self, value: bool) -> None:
        self._is_active = value

    @hybrid_property
    def theme_preference(self) -> str:
        return self._theme_preference
        
    @theme_preference.setter
    def theme_preference(self, value: str) -> None:
        self._theme_preference = value