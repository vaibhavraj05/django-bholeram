from django.urls import path
from rest_framework.routers import DefaultRouter
from post_app.views import SavedPostView
from post_app.views import PostViewSet,CommentViewSet,LikeViewSet,ReplyCommentViewSet
router = DefaultRouter()
# router.register('posts', PostViewSet) 
# router.register('users',PostViewSet, basename='user')
# router.register('posts',CommentViewSet)

urlpatterns = [
    path('posts/<uuid:post_id>/',PostViewSet.as_view({'put':'update','delete':'destroy',})),
    path('posts/<str:post_id>/comment',CommentViewSet.as_view({'post': 'create','get':'list'}), name='comment-create'),
    path('comments/<str:comment_id>/reply',ReplyCommentViewSet.as_view({'post':'create'}), name= 'reply-comment'),
    path('posts/<str:post_id>/like',LikeViewSet.as_view({'post':'create','get':'list'})),
    path('users/comments',CommentViewSet.as_view({'get':'list'})),
    path('users/likes',LikeViewSet.as_view({'get' : 'list'})),
    path('posts/<str:post_id>', SavedPostView.as_view(),name = "save-posts"),
    path('posts/<str:post_id>/save', SavedPostView.as_view(), name='save-post'),
    path('posts/save', SavedPostView.as_view(), name='save-posts'),
    path('posts/<str:post_id>/comments/<str:comment_id>/',CommentViewSet.as_view({'put': 'update','delete': 'destroy','get':'retrieve'})),
    path('comments/<str:comment_id>/',CommentViewSet.as_view({'get' : 'retrieve','put' : 'update' , 'delete': 'destroy'})),
    path('users/<str:user_id>/posts',PostViewSet.as_view({'get':'list'}), name="get-user-post"),
]