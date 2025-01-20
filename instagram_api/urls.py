"""
URL configuration for practise project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter
from post_app.views import PostViewSet
router = DefaultRouter()
router.register('posts', PostViewSet)
# router.register('comments', CommentViewSet)
# router.register(r'posts/(?P<post_id>\d+)/comments', CommentViewSet, basename='comments')


urlpatterns = [
    path('admin/', admin.site.urls),
    path('',include('user.urls')),
    path('',include(router.urls)),
    path('',include('post_app.urls'))
    # path('posts',PostViewSet.as_view({'post':'create','get':'list'})),
    # path('posts/<uuid:post_id>',PostViewSet.as_view({'put':'update','delete':'destroy',})),
    # path('posts/<uuid:post_id>/comment',CommentViewSet.as_view({'post': 'create','get':'list'}), name='comment-create'),
    # path('comments/<uuid:comment_id>/reply',ReplyCommentViewSet.as_view({'post':'create'}), name= 'reply-comment'),
    # path('posts/<uuid:post_id>/like',LikeViewSet.as_view({'post':'create','get':'list'})),
    # path('users/comments',CommentViewSet.as_view({'get':'list'})),
    # path('users/likes',LikeViewSet.as_view({'get' : 'list'})),
    # path('posts/<uuid:post_id>/', SavedPostView.as_view(),name = "save-posts"),
    # path('posts/<uuid:post_id>/save', SavedPostView.as_view(), name='save-post'),
    # path('posts/save', SavedPostView.as_view(), name='save-posts'),
    # #retrieve comments fby post id
    # path('posts/<uuid:post_id>/comments/<uuid:comment_id>/',CommentViewSet.as_view({'put': 'update','delete': 'destroy','get':'retrieve'})),
    # path('comments/<uuid:comment_id>/',CommentViewSet.as_view({'get' : 'retrieve','put' : 'update' , 'delete': 'destroy'}))   
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    