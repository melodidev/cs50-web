from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    avatar_url = models.URLField(default='https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQwoc-wOHrC7EoqCbHPbhQdpNOR2uDZB8tzmA&usqp=CAU')
    bio = models.CharField(max_length=100, default='No bio yet.')

    def __str__(self):
        return f"{self.username}"

    def serialize(self):
        return {
            "id": self.id,
            "username": self.username,
            "avatar_url": self.avatar_url,
            "bio": self.bio
        }


class Post(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name="post_user_id")
    content = models.CharField(max_length=140)
    time = models.DateTimeField()

    def __str__(self):
        return f"{self.user_id.username} made a post at {self.time}"

    def serialize(self):
        return {
            "id": self.id,
            "user": self.user_id.serialize(),
            "content": self.content,
            "time": self.time
        }

class Follow(models.Model):
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name="follower")
    followed_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="followed_user")

    def __str__(self):
        return f"{self.follower.username} started following {self.followed_user.username}"

class Like(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name="like_user_id")
    post_id = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="post_id")

    def __str__(self):
        return f"{self.user_id.username} liked a post"

    def serialize(self):
        return {
            "user_id": self.user_id,
            "post_id": self.post_id
    }

"""
python manage.py makemigrations
python manage.py migrate
"""
