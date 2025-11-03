import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from database.db import Base
from database.models import User, Post, Comment
from main import app
from dependency import get_db
from utils.auth_util import password_hash, create_access_token
from datetime import timedelta

# Create in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database for each test"""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """Create a test client with database dependency override"""

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def test_user(db_session):
    """Create a test user"""
    user = User(
        username="testuser",
        email="test@example.com",
        password_hash=password_hash.hash("testpassword123"),
        active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def test_user_2(db_session):
    """Create a second test user"""
    user = User(
        username="testuser2",
        email="test2@example.com",
        password_hash=password_hash.hash("testpassword456"),
        active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def auth_token(test_user):
    """Generate authentication token for test user"""
    token = create_access_token(test_user.username, test_user.id, timedelta(minutes=20))
    return token


@pytest.fixture
def auth_token_user_2(test_user_2):
    """Generate authentication token for second test user"""
    token = create_access_token(test_user_2.username, test_user_2.id, timedelta(minutes=20))
    return token


@pytest.fixture
def auth_client(client, auth_token):
    """Create test client with authentication cookie"""
    client.cookies.set("token", auth_token)
    return client


@pytest.fixture
def auth_client_user_2(client, auth_token_user_2):
    """Create test client with authentication cookie for second user"""
    client.cookies.set("token", auth_token_user_2)
    return client


@pytest.fixture
def test_post(db_session, test_user):
    """Create a test post"""
    post = Post(
        title="Test Post",
        description="This is a test post description",
        owner_id=test_user.id,
        owner=test_user
    )
    db_session.add(post)
    db_session.commit()
    db_session.refresh(post)
    return post


@pytest.fixture
def test_comment(db_session, test_user, test_post):
    """Create a test comment"""
    comment = Comment(
        comment="This is a test comment",
        post_id=test_post.id,
        owner_id=test_user.id
    )
    db_session.add(comment)
    db_session.commit()
    db_session.refresh(comment)
    return comment