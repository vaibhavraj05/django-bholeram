from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .models import Post, Comment, Like
from .serializers import *
from .paginations import CustomPagination
from rest_framework.viewsets import ModelViewSet
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from user.permissions import IsUserVerified
import logging


logger = logging.getLogger(__name__)

class PostViewSet(ModelViewSet):
    queryset = Post.objects.filter(is_deleted=False).order_by("-created_at")
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated, IsUserVerified]
    lookup_field = 'id'

    def list(self, request, user_id=None):
        if user_id:
            post = Post.objects.filter(user_id=user_id, is_deleted=False).order_by(
                "-created_at"
            )
            if not post.exists():
                return Response(
                    {
                    "detail": "post not exists for this user"},
                    status=status.HTTP_404_NOT_FOUND,
                )
        else:
            user = request.user
            post = Post.objects.filter(user_id=user.id, is_deleted=False).order_by(
                "-created_at"
            )
            if not post.exists():
                return Response(
                    {"detail": "post not exists for this user"},
                    status=status.HTTP_404_NOT_FOUND,
                )
        paginator = CustomPagination(request, post, page_size=5)
        paginated_data = paginator.paginated_data
        serializer = PostSerializer(paginated_data, many=True)
        return paginator.get_paginated_response(serializer.data)
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        logger.info(f"Retrieved post: {instance}")
        return Response({"data": serializer.data})

    def destroy(self, request, id=None):
        post = get_object_or_404(Post, id=id, user=request.user, is_deleted=False)
        if post.user != request.user:
            return Response({
                "detail": "Unauthorized"
            },status=status.HTTP_401_UNAUTHORIZED)
        post.is_deleted = True
        post.deleted_at = timezone.now()
        post.save()
        return Response({"detail" : "Post Deleted Successfully"},status=status.HTTP_204_NO_CONTENT)
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
    
        if serializer.is_valid():
            serializer.save()  # Make sure to save the instance
            return Response({"data": serializer.data}, status=status.HTTP_201_CREATED)
        else:
            return Response({"errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, id=None):
        post = get_object_or_404(Post, id=id, user=request.user, is_deleted=False)
        if post.user != request.user:
            raise PermissionDenied("Not authorized to update this post")

        serializer = self.get_serializer(post, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                "data": serializer.data},
                status=status.HTTP_202_ACCEPTED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SavedPostView(APIView):
    permission_classes = [IsAuthenticated, IsUserVerified]

    def get(self, request):
        user = request.user
        saved_posts = SavedPost.objects.filter(user=user).select_related("post")
    
        if not saved_posts.exists():
            
            return Response({"data": []}, status=status.HTTP_200_OK)

        paginator = CustomPagination(request, saved_posts, page_size=5)
        paginated_data = paginator.paginated_data
        serializer = SavedPostSerializer(paginated_data, many=True)

        return paginator.get_paginated_response(serializer.data)
    
    def post(self, request, post_id):
        post = get_object_or_404(Post, id=post_id)
        user = request.user
        if SavedPost.objects.filter(user=user, post=post).exists():
            return Response(
                {"detail": "You have already saved this post."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        saved_post = SavedPost.objects.create(user=user, post=post)
        serializer = SavedPostSerializer(saved_post)
        return Response({"data": serializer.data}, status=status.HTTP_201_CREATED)

    def delete(self, request, post_id):
        post = get_object_or_404(Post, id=post_id)
        user = request.user

        saved_post = SavedPost.objects.filter(user=user, post=post).first()
        if not saved_post:
            return Response(
                {
                "detail": "This post is not in your saved list."},
                status=status.HTTP_204_NO_CONTENT,
            )
        saved_post.delete()
        return Response(
            {"detail" : "Post Unliked successfully"},status=status.HTTP_404_NOT_FOUND
        )


class CommentViewSet(ModelViewSet):
    queryset = Comment.objects.filter(is_deleted=False, parent=None).order_by(
        "-created_at"
    )
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated, IsUserVerified]
    lookup_field = 'comment_id'
    # lookup_field = 'post_id'

    def get_queryset(self):
        post_id = self.kwargs.get("post_id")
        if post_id:
            return Comment.objects.filter(
                post_id=post_id, parent=None, is_deleted=False
            ).order_by("-created_at")
        return Comment.objects.filter(is_deleted=False, parent=None)

    def create(self, request, *args, **kwargs):
        post_id = self.kwargs.get("post_id")
        post = get_object_or_404(Post, id=post_id)
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save(post=post, user=self.request.user)
            return Response(data={"data" : serializer.data},status=status.HTTP_201_CREATED)
        else:
            return Response(data={"data" : serializer.error},status=status.HTTP_201_CREATED)
        return resp
        

    def destroy(self, request, *args, **kwargs):
        post_id = self.kwargs.get('post_id')
        comment_id = self.kwargs.get('comment_id')
        if post_id :
            post = get_object_or_404(Post, id = post_id , user = request.user, is_deleted = False)
            comment = get_object_or_404(Comment, id=comment_id, post=post, user=request.user, is_deleted=False)
        else:
           comment = get_object_or_404(Comment, id=comment_id, user=request.user, is_deleted=False)
        comment.is_deleted = True
        comment.deleted_at = timezone.now()
        comment.save()
        return Response({"detail":"Comment deleted successfully"},status=status.HTTP_204_NO_CONTENT)

    def list(self, request, *args, **kwargs):
        post_id = kwargs.get('post_id')
        if not post_id:
            user = request.user
            comment = Comment.objects.filter(user = user.id,is_deleted = False).order_by("-created_at")
            if not comment.exists():
                return Response({
                    "detail": "Not any comments posted yet"
                },status=status.HTTP_404_NOT_FOUND)
                            
        else:   
            comment = Comment.objects.filter(post_id=post_id, is_deleted=False).order_by(
                "-created_at"
            )
            if not comment.exists():
                return Response(
                    {"detail": "comment not exists for this post"},
                    status=status.HTTP_404_NOT_FOUND,
                )
                
        paginator = CustomPagination(request, comment, page_size=5)
        paginated_data = paginator.paginated_data
        serializer = self.get_serializer(paginated_data, many=True)
        return Response({"data" : serializer.data},status=status.HTTP_200_OK)
    
    def retrieve(self, request, *args, **kwargs):
        post_id = self.kwargs.get('post_id')
        comment_id = self.kwargs.get('comment_id')
        if post_id :
           post = get_object_or_404(Post, id = post_id ,is_deleted= False)
           comment = get_object_or_404(Comment, id = comment_id ,post = post, is_deleted = False)
        else:
           comment = get_object_or_404(Comment, id = comment_id ,is_deleted = False)
        serializer = self.get_serializer(comment)
        return Response({
            "data" : serializer.data
        })

    def update(self, request,*args,**kwargs):
        post_id = self.kwargs.get('post_id')
        comment_id = self.kwargs.get('comment_id')
        if post_id:
            post = get_object_or_404(Post,id = post_id,user= request.user,is_deleted=False)
            # comment = get_object_or_404(Comment,post = post_id,user = request.user, is_deleted= False)
        comment = get_object_or_404(Comment, id=comment_id, is_deleted=False)
        serializer = self.get_serializer(comment, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'data':serializer.data}, status=status.HTTP_200_OK)
    

class ReplyCommentViewSet(ModelViewSet):
    queryset = Comment.objects.filter(is_deleted=False, parent=None).order_by(
        "-created_at"
    )
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated, IsUserVerified]
   
    def create(self, request, *args, **kwargs):
        comment_id = self.kwargs.get("comment_id")
        
        parent_comment = get_object_or_404(Comment,id = comment_id, is_deleted=False)
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=self.request.user, parent=parent_comment,post=parent_comment.post)
            resp = Response(data={"data" : serializer.data},status=status.HTTP_201_CREATED)
        else:
            resp = Response(data={"data" : serializer.error},status=status.HTTP_201_CREATED)
        return resp
        


class LikeViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated, IsUserVerified]

    def create(self, request, *args, **kwargs):
        post_id = self.kwargs.get("post_id") 
       
        if not post_id:
            return Response({"detail": "Post ID is required."}, status=status.HTTP_400_BAD_REQUEST)

        post = Post.objects.filter(id=post_id).first()
        if not post:
            return Response({"detail": "Post not found."}, status=status.HTTP_404_NOT_FOUND)

        if Like.objects.filter(user=request.user, post=post).exists():
           return Response({"detail" : "already liked"})

        like = Like.objects.create(user=request.user, post=post)
        serializer = LikeSerializer(like)
        return Response({"data":serializer.data}, status=status.HTTP_201_CREATED)
        
        
    def delete(self, request, post_id):
        post = get_object_or_404(Post, id=post_id)

        if Like.objects.filter(post=post).exists():
            Like.objects.filter(post=post).delete()
            likes_count = Like.objects.filter(post=post).count
            serializers = PostSerializer(instance=post)
            return Response({"detail" : "Post Unliked Successfully"},status=status.HTTP_204_NO_CONTENT)

        else:
            return Response({"detail" : "Your likes not found"},status=status.HTTP_404_NOT_FOUND)

    def list(self, request, *args,**kwargs):
        post_id = self.kwargs.get('post_id')
        if not post_id:
            user = request.user
            like = Like.objects.filter(user = user.id).order_by('-created_at')
            if not like.exists():
                return Response({
                    "detail" : "No Like found of this user"
                },status = status.HTTP_404_NOT_FOUND)
        else:
            like = Like.objects.filter(post_id=post_id).order_by(
                "-created_at"
            )
            if not like.exists():
                return Response(
                    {"detail": "No likes found"},
                    status=status.HTTP_404_NOT_FOUND,
                )
        paginator = CustomPagination(request, like, page_size=5)
        paginated_data = paginator.paginated_data
        serializer = LikeSerializer(paginated_data, many=True)
        return paginator.get_paginated_response(serializer.data)