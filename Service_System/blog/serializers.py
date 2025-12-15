from rest_framework import serializers

from blog.models import Post
from django.contrib.auth.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email"]


class PostSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)

    class Meta:
        model = Post
        fields = (
            "id",
            "title",
            "text",
            "created_date",
            "published_date",
            "image",
            "author",
        )
