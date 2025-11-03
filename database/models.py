
from sqlalchemy.ext.declarative import declared_attr
from database.db import Base
from sqlalchemy import event, Integer, String, DateTime, Boolean, ForeignKey,func
from sqlalchemy.orm import Mapped,mapped_column,relationship

class TimestampMixin:
    @declared_attr
    def created_at(cls):
        return mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    @declared_attr
    def updated_at(cls):
        return mapped_column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now(), nullable=False)


class User(Base,TimestampMixin):
    __tablename__ = "users"
    id:Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username:Mapped[str] = mapped_column(String, nullable=False, unique=True)
    email:Mapped[str] = mapped_column(String, nullable=False, unique=True)
    password_hash:Mapped[str] = mapped_column(String, nullable=False)
    active:Mapped[bool] = mapped_column(Boolean)

    posts:Mapped[list['Post']] = relationship(
        back_populates="owner",
        cascade="all, delete-orphan",
    )
    comments:Mapped[list['Comment']] = relationship(back_populates="owner",cascade="all, delete-orphan")


class Post(Base, TimestampMixin):
    __tablename__ = "posts"
    id:Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title:Mapped[str] = mapped_column(String, nullable=False, unique=True)
    description:Mapped[str] = mapped_column(String, nullable=False)
    owner_id:Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))

    owner:Mapped['User'] = relationship(back_populates="posts")
    comments:Mapped[list['Comment']] = relationship(back_populates='post',cascade="all, delete-orphan")

class Comment(Base, TimestampMixin):
    __tablename__ = "comments"
    id:Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    comment:Mapped[str] = mapped_column(String, nullable=False)
    owner_id:Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    post_id:Mapped[int] = mapped_column(Integer, ForeignKey("posts.id"))

    owner:Mapped['User'] = relationship(back_populates="comments")
    post:Mapped['Post'] = relationship(back_populates="comments")
