import pytest
from starlette import status


class TestUserCreation:
    """Test user creation endpoint"""

    def test_create_user_success(self, client):
        """Test successful user creation"""
        response = client.post(
            "/users/",
            json={
                "username": "newuser",
                "email": "newuser@example.com",
                "password": "password123"
            }
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["username"] == "newuser"
        assert data["email"] == "newuser@example.com"
        assert "id" in data
        assert "createdAt" in data
        assert "updatedAt" in data
        assert data["message"] == "User created successfully"

    def test_create_user_duplicate_username(self, client, test_user):
        """Test creating user with existing username"""
        response = client.post(
            "/users/",
            json={
                "username": "testuser",
                "email": "different@example.com",
                "password": "password123"
            }
        )

        assert response.status_code == status.HTTP_406_NOT_ACCEPTABLE
        assert response.json()["detail"] == "Username already exists"

    def test_create_user_invalid_data(self, client):
        """Test creating user with invalid data"""
        response = client.post(
            "/users/",
            json={
                "username": "newuser"
                # Missing required fields
            }
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestUserAuthentication:
    """Test user authentication and token generation"""

    def test_authenticate_user_success(self, client, test_user):
        """Test successful authentication"""
        response = client.post(
            "/users/token",
            data={
                "username": "testuser",
                "password": "testpassword123"
            }
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert "token" in response.cookies

    def test_authenticate_user_wrong_password(self, client, test_user):
        """Test authentication with wrong password"""
        response = client.post(
            "/users/token",
            data={
                "username": "testuser",
                "password": "wrongpassword"
            }
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_authenticate_user_nonexistent(self, client):
        """Test authentication with non-existent user"""
        response = client.post(
            "/users/token",
            data={
                "username": "nonexistent",
                "password": "password123"
            }
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestGetUserDetail:
    """Test getting user details"""

    def test_get_user_detail_success(self, auth_client, test_user):
        """Test getting user details with valid token"""
        response = auth_client.get("/users/")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == test_user.id
        assert data["username"] == test_user.username
        assert data["email"] == test_user.email
        assert "createdAt" in data
        assert "updatedAt" in data

    def test_get_user_detail_unauthorized(self, client):
        """Test getting user details without authentication"""
        response = client.get("/users/")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_user_detail_invalid_token(self, client):
        """Test getting user details with invalid token"""
        client.cookies.set("token", "invalidtoken")
        response = client.get("/users/")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestUpdateUser:
    """Test updating user details"""

    def test_update_user_username(self, auth_client, test_user):
        """Test updating username"""
        response = auth_client.put(
            "/users/",
            json={"username": "updateduser"}
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["username"] == "updateduser"
        assert data["message"] == "user updated successfully"

    def test_update_user_email(self, auth_client, test_user):
        """Test updating email"""
        response = auth_client.put(
            "/users/",
            json={"email": "updated@example.com"}
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["email"] == "updated@example.com"

    def test_update_user_no_fields(self, auth_client, test_user):
        """Test updating with no fields provided"""
        response = auth_client.put(
            "/users/",
            json={}
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json()["detail"] == "Atleast one field is required"

    def test_update_user_unauthorized(self, client):
        """Test updating user without authentication"""
        response = client.put(
            "/users/",
            json={"username": "newname"}
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestDeleteUser:
    """Test deleting user"""

    def test_delete_user_success(self, auth_client, test_user):
        """Test successful user deletion"""
        response = auth_client.delete("/users/")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["message"] == "Successfully deleted"
        assert data["id"] == test_user.id
        assert data["username"] == test_user.username

    def test_delete_user_unauthorized(self, client):
        """Test deleting user without authentication"""
        response = client.delete("/users/")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_delete_user_cascades_to_posts(self, auth_client, test_user, test_post, db_session):
        """Test that deleting user also deletes their posts"""
        from database.models import Post

        response = auth_client.delete("/users/")
        assert response.status_code == status.HTTP_200_OK

        # Verify post was also deleted
        post = db_session.query(Post).filter(Post.id == test_post.id).first()
        assert post is None