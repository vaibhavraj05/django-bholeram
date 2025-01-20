from django.db import models
from user.models import User
from user.models import Base
from django.utils import timezone
import uuid

class Post(Base):
    id = models.UUIDField(primary_key=True,default = uuid.uuid4,editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE,to_field='id', db_column='user_id')
    title = models.CharField(max_length=25)
    content = models.TextField()
    image = models.ImageField(upload_to="posts/", null=True, blank=True)
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.title
    class Meta:
        db_table = "post"


class SavedPost(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, to_field='id', related_name='saved_by')
    post = models.ForeignKey(Post, on_delete=models.CASCADE,to_field='id',related_name='saved_posts')
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        unique_together = ('user', 'post')
    def __str__(self):
        return f"{self.user} saved {self.post}"


class Comment(Base):
    id = models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE , to_field='id',db_column='user_id')
    post = models.ForeignKey(Post, on_delete=models.CASCADE ,to_field='id', db_column='post_id')
    content = models.TextField()
    parent = models.ForeignKey(
        'self', null=True, blank=True, on_delete=models.CASCADE,related_name='replies'
    )
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)
    def __str__(self):
        return self.content
    class Meta:
        db_table = "comment"


class Like(Base):
    id = models.UUIDField(primary_key=True,default=uuid.uuid4,)
    post = models.ForeignKey(Post, on_delete=models.CASCADE,to_field='id', db_column='post_id')
    user = models.ForeignKey(User, on_delete=models.CASCADE,to_field='id', db_column='user_id')
    class Meta:
        unique_together = ("post", "user")
        db_table = "like"
    def __str__(self):
        return f"{self.user} liked {self.post}"
