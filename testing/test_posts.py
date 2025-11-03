import pytest
from starlette import status


class TestCreatePost:
    """Test post creation endpoint"""

    def test_create_post_success(self, auth_client, test_user):
        """Test successful post creation"""
        response = auth_client.post(
            "/posts/",
            json={
                "title": "My First Post",
                "description": "This is my first post description"
            }
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["title"] == "My First Post"
        assert data["description"] == "This is my first post description"
        assert data["owner"]["id"] == test_user.id
        assert data["owner"]["username"] == test_user.username
        assert data["message"] == "Post created"
        assert "created_at" in data
        assert "updated_at" in data

    def test_create_post_unauthorized(self, client):
        """Test creating post without authentication"""
        response = client.post(
            "/posts/",
            json={
                "title": "Unauthorized Post",
                "description": "This should fail"
            }
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_create_post_missing_fields(self, auth_client):
        """Test creating post with missing required fields"""
        response = auth_client.post(
            "/posts/",
            json={"title": "Only Title"}
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestGetUserPosts:
    """Test getting user's posts"""

    def test_get_user_all_posts_success(self, auth_client, test_user, test_post):
        """Test getting all posts for authenticated user"""
        response = auth_client.get("/posts/user/all")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 1
        assert data[0]["id"] == test_post.id
        assert data[0]["title"] == test_post.title
        assert data[0]["owner"]["id"] == test_user.id

    def test_get_user_all_posts_multiple(self, auth_client, test_user, db_session):
        """Test getting multiple posts for user"""
        from database.models import Post

        # Create additional posts
        post1 = Post(title="Post 1", description="Description 1", owner_id=test_user.id)
        post2 = Post(title="Post 2", description="Description 2", owner_id=test_user.id)
        db_session.add_all([post1, post2])
        db_session.commit()

        response = auth_client.get("/posts/user/all")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 2

    def test_get_user_all_posts_empty(self, auth_client, test_user):
        """Test getting posts when user has none"""
        response = auth_client.get("/posts/user/all")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0

    def test_get_user_all_posts_unauthorized(self, client):
        """Test getting user posts without authentication"""
        response = client.get("/posts/user/all")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestGetAllPosts:
    """Test getting all posts (public endpoint)"""

    def test_get_all_posts_success(self, client, test_post):
        """Test getting all posts"""
        response = client.get("/posts/all")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        assert any(post["id"] == test_post.id for post in data)

    def test_get_all_posts_empty(self, client):
        """Test getting all posts when none exist"""
        response = client.get("/posts/all")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0

    def test_get_all_posts_multiple_users(self, client, test_user, test_user_2, db_session):
        """Test getting posts from multiple users"""
        from database.models import Post

        post1 = Post(title="User 1 Post", description="Desc 1", owner_id=test_user.id)
        post2 = Post(title="User 2 Post", description="Desc 2", owner_id=test_user_2.id)
        db_session.add_all([post1, post2])
        db_session.commit()

        response = client.get("/posts/all")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 2


class TestUpdatePost:
    """Test updating posts"""

    def test_update_post_title(self, auth_client, test_post):
        """Test updating post title"""
        response = auth_client.put(
            f"/posts/{test_post.id}",
            json={"title": "Updated Title"}
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["title"] == "Updated Title"
        assert data["description"] == test_post.description
        assert data["message"] == "Post updated"

    def test_update_post_description(self, auth_client, test_post):
        """Test updating post description"""
        response = auth_client.put(
            f"/posts/{test_post.id}",
            json={"description": "Updated Description"}
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["description"] == "Updated Description"
        assert data["title"] == test_post.title

    def test_update_post_both_fields(self, auth_client, test_post):
        """Test updating both title and description"""
        response = auth_client.put(
            f"/posts/{test_post.id}",
            json={
                "title": "New Title",
                "description": "New Description"
            }
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["title"] == "New Title"
        assert data["description"] == "New Description"

    def test_update_post_no_fields(self, auth_client, test_post):
        """Test updating post with no fields"""
        response = auth_client.put(
            f"/posts/{test_post.id}",
            json={}
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json()["detail"] == "Atleast one field should be provided"

    def test_update_post_not_owner(self, auth_client_user_2, test_post):
        """Test updating post by non-owner"""
        response = auth_client_user_2.put(
            f"/posts/{test_post.id}",
            json={"title": "Hacked Title"}
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.json()["detail"] == "You are not the owner of the post"

    def test_update_post_not_found(self, auth_client):
        """Test updating non-existent post"""
        response = auth_client.put(
            "/posts/99999",
            json={"title": "New Title"}
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()["detail"] == "Post not found"

    def test_update_post_unauthorized(self, client, test_post):
        """Test updating post without authentication"""
        response = client.put(
            f"/posts/{test_post.id}",
            json={"title": "New Title"}
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_update_post_invalid_id(self, auth_client):
        """Test updating post with invalid ID (0 or negative)"""
        response = auth_client.put(
            "/posts/0",
            json={"title": "New Title"}
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestDeletePost:
    """Test deleting posts"""

    def test_delete_post_success(self, auth_client, test_post, db_session):
        """Test successful post deletion"""
        response = auth_client.delete(f"/posts/{test_post.id}")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == test_post.id
        assert data["message"] == "Post deleted"

        # Verify post is actually deleted
        from database.models import Post
        post = db_session.query(Post).filter(Post.id == test_post.id).first()
        assert post is None

    def test_delete_post_not_owner(self, auth_client_user_2, test_post):
        """Test deleting post by non-owner"""
        response = auth_client_user_2.delete(f"/posts/{test_post.id}")

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.json()["detail"] == "You are not the owner of this post"

    def test_delete_post_not_found(self, auth_client):
        """Test deleting non-existent post"""
        response = auth_client.delete("/posts/99999")

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()["detail"] == "Post not found"

    def test_delete_post_unauthorized(self, client, test_post):
        """Test deleting post without authentication"""
        response = client.delete(f"/posts/{test_post.id}")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_delete_post_cascades_to_comments(self, auth_client, test_post, test_comment, db_session):
        """Test that deleting post also deletes its comments"""
        from database.models import Comment

        response = auth_client.delete(f"/posts/{test_post.id}")

        assert response.status_code == status.HTTP_200_OK

        # Verify comment was also deleted
        comment = db_session.query(Comment).filter(Comment.id == test_comment.id).first()
        assert comment is None