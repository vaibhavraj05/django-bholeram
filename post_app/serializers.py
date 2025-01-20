from .models import Post, Comment, Like, SavedPost
from rest_framework import serializers


class PostSerializer(serializers.ModelSerializer):
    likes = serializers.SerializerMethodField()
    comments = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = (
            "title",
            "content",
            "image",
            "id",
            "user",
            "likes",
            "comments",
            "created_at",
        )
        read_only_fields = ["user", "likes", "comments", "created_at"]

    def get_likes(self, obj):
        return Like.objects.filter(post=obj).count()

    def get_comments(self, obj):
        return Comment.objects.filter(post=obj).count()

    def create(self, validated_data):
        validated_data["user"] = self.context["request"].user
        return super().create(validated_data)

    def to_representation(self, instance):
        """Exclude `likes_count` in POST requests"""
        representation = super().to_representation(instance)
        request = self.context.get("request")
        if request and (request.method == "POST" or request.method == "PUT"):
            representation.pop("likes_count", None)
            representation.pop("comments", None)

        return representation

    def update(self, instance, validate_data):
        instance.title = validate_data.get("title", instance.title)
        instance.content = validate_data.get("content", instance.content)
        instance.image = validate_data.get("image", instance.image)
        instance.save()
        return instance


class SavedPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = SavedPost
        fields = ["user", "post", "created_at"]


class CommentSerializer(serializers.ModelSerializer):
    replies = serializers.SerializerMethodField()
    parent = serializers.SerializerMethodField()
    post = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ["id", "content","parent", "post", "replies", "user"]
        read_only_fields = ["user", "post"]

    def get_replies(self, obj):
        if obj.replies.exists():
            return CommentSerializer(obj.replies.all(), many=True).data
        return []
    
    def get_post(self,obj):
        return {
            "post_id": obj.post.id,
            "title": obj.post.title,
            "content": obj.post.content,
        }

    def create(self, validated_data):
        request = self.context.get("request")
        validated_data["user"] = request.user
        return super().create(validated_data)
    
    def get_parent(self,obj):
        return obj.parent.id if obj.parent else None
    
class LikeSerializer(serializers.ModelSerializer):
    liked_by = serializers.SerializerMethodField()
    post = serializers.SerializerMethodField()

    class Meta:
        model = Like
        fields = ["created_at", "post","liked_by_user"]
        read_only_fields = ["liked_by", "post"]

    def get_post(self, obj):
        # Return post details: ID, title, content
        return {
            "post_id": obj.post.id,
            "title": obj.post.title,
            "content": obj.post.content,
        }

    def get_liked_by_user(self, obj):
        # Return user details: ID and username
        return {
            "user_id": obj.user.id,
            "username": obj.user.username,
        }