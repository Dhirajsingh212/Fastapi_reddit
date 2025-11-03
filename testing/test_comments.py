import pytest
from starlette import status


class TestCreateComment:
    """Test comment creation endpoint"""

    def test_create_comment_success(self, auth_client, test_user, test_post):
        """Test successful comment creation"""
        response = auth_client.post(
            f"/comment/{test_post.id}",
            json={"comment": "This is a great post!"}
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["comment"] == "This is a great post!"
        assert data["owner"]["id"] == test_user.id
        assert data["owner"]["username"] == test_user.username
        assert data["post"]["id"] == test_post.id
        assert data["post"]["title"] == test_post.title
        assert "created_at" in data
        assert "updated_at" in data

    def test_create_comment_unauthorized(self, client, test_post):
        """Test creating comment without authentication"""
        response = client.post(
            f"/comment/{test_post.id}",
            json={"comment": "Unauthorized comment"}
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json()["detail"] == "Not authenticated"

    def test_create_comment_post_not_found(self, auth_client):
        """Test creating comment on non-existent post"""
        response = auth_client.post(
            "/comment/99999",
            json={"comment": "Comment on non-existent post"}
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()["detail"] == "Post not found"

    def test_create_comment_invalid_post_id(self, auth_client):
        """Test creating comment with invalid post ID (0 or negative)"""
        response = auth_client.post(
            "/comment/0",
            json={"comment": "Invalid post ID"}
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_create_comment_missing_comment_field(self, auth_client, test_post):
        """Test creating comment without comment text"""
        response = auth_client.post(
            f"/comment/{test_post.id}",
            json={}
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestGetCommentsByPost:
    """Test getting comments for a post"""

    def test_get_comments_success(self, auth_client, test_post, test_comment):
        """Test getting all comments for a post"""
        response = auth_client.get(f"/comment/{test_post.id}")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 1
        assert data[0]["id"] == test_comment.id
        assert data[0]["comment"] == test_comment.comment
        assert data[0]["owner"]["id"] == test_comment.owner_id

    def test_get_comments_multiple(self, auth_client, test_post, test_user, test_user_2, db_session):
        """Test getting multiple comments for a post"""
        from database.models import Comment

        comment1 = Comment(comment="First comment", post_id=test_post.id, owner_id=test_user.id)
        comment2 = Comment(comment="Second comment", post_id=test_post.id, owner_id=test_user_2.id)
        db_session.add_all([comment1, comment2])
        db_session.commit()

        response = auth_client.get(f"/comment/{test_post.id}")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 2

    def test_get_comments_empty(self, auth_client, test_post):
        """Test getting comments when post has none"""
        response = auth_client.get(f"/comment/{test_post.id}")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0

    def test_get_comments_post_not_found(self, auth_client):
        """Test getting comments for non-existent post"""
        response = auth_client.get("/comment/99999")

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()["detail"] == "Post not found"

    def test_get_comments_unauthorized(self, client, test_post):
        """Test getting comments without authentication"""
        response = client.get(f"/comment/{test_post.id}")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json()["detail"] == "Not authenticated"

    def test_get_comments_invalid_post_id(self, auth_client):
        """Test getting comments with invalid post ID"""
        response = auth_client.get("/comment/0")

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestUpdateComment:
    """Test updating comments"""

    def test_update_comment_success(self, auth_client, test_comment):
        """Test successful comment update"""
        response = auth_client.put(
            f"/comment/{test_comment.id}",
            json={"comment": "Updated comment text"}
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["comment"] == "Updated comment text"
        assert data["id"] == test_comment.id
        assert data["message"] == "Comment updated successfully"

    def test_update_comment_not_owner(self, auth_client_user_2, test_comment):
        """Test updating comment by non-owner"""
        response = auth_client_user_2.put(
            f"/comment/{test_comment.id}",
            json={"comment": "Hacked comment"}
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.json()["detail"] == "You do not have permission to edit this comment"

    def test_update_comment_not_found(self, auth_client):
        """Test updating non-existent comment"""
        response = auth_client.put(
            "/comment/99999",
            json={"comment": "Updated text"}
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()["detail"] == "Comment not found"

    def test_update_comment_unauthorized(self, client, test_comment):
        """Test updating comment without authentication"""
        response = client.put(
            f"/comment/{test_comment.id}",
            json={"comment": "Updated text"}
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json()["detail"] == "Not authenticated"

    def test_update_comment_invalid_id(self, auth_client):
        """Test updating comment with invalid ID"""
        response = auth_client.put(
            "/comment/0",
            json={"comment": "Updated text"}
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_update_comment_empty_data(self, auth_client, test_comment):
        """Test updating comment with empty data"""
        response = auth_client.put(
            f"/comment/{test_comment.id}",
            json={}
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json()["detail"] == "Atleast one Field is required"


class TestDeleteComment:
    """Test deleting comments"""

    def test_delete_comment_success(self, auth_client, test_comment, db_session):
        """Test successful comment deletion"""
        response = auth_client.delete(f"/comment/{test_comment.id}")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == test_comment.id
        assert data["message"] == "Deleted comment"

        # Verify comment is actually deleted
        from database.models import Comment
        comment = db_session.query(Comment).filter(Comment.id == test_comment.id).first()
        assert comment is None

    def test_delete_comment_not_owner(self, auth_client_user_2, test_comment):
        """Test deleting comment by non-owner"""
        response = auth_client_user_2.delete(f"/comment/{test_comment.id}")

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.json()["detail"] == "You do not have permission to edit this comment"

    def test_delete_comment_not_found(self, auth_client):
        """Test deleting non-existent comment"""
        response = auth_client.delete("/comment/99999")

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()["detail"] == "Comment not found"

    def test_delete_comment_unauthorized(self, client, test_comment):
        """Test deleting comment without authentication"""
        response = client.delete(f"/comment/{test_comment.id}")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json()["detail"] == "Not authenticated"

    def test_delete_comment_invalid_id(self, auth_client):
        """Test deleting comment with invalid ID"""
        response = auth_client.delete("/comment/0")

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestCommentIntegration:
    """Integration tests for comment functionality"""

    def test_comment_workflow(self, auth_client, test_user, test_post, db_session):
        """Test complete comment workflow: create, read, update, delete"""
        # Create comment
        create_response = auth_client.post(
            f"/comment/{test_post.id}",
            json={"comment": "Initial comment"}
        )
        assert create_response.status_code == status.HTTP_200_OK
        comment_id = create_response.json()["id"]

        # Read comments
        get_response = auth_client.get(f"/comment/{test_post.id}")
        assert get_response.status_code == status.HTTP_200_OK
        comments = get_response.json()
        assert len(comments) == 1
        assert comments[0]["comment"] == "Initial comment"

        # Update comment
        update_response = auth_client.put(
            f"/comment/{comment_id}",
            json={"comment": "Updated comment"}
        )
        assert update_response.status_code == status.HTTP_200_OK
        assert update_response.json()["comment"] == "Updated comment"

        # Delete comment
        delete_response = auth_client.delete(f"/comment/{comment_id}")
        assert delete_response.status_code == status.HTTP_200_OK

        # Verify deletion
        from database.models import Comment
        comment = db_session.query(Comment).filter(Comment.id == comment_id).first()
        assert comment is None