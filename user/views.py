from .models import *
from rest_framework.decorators import APIView
from rest_framework import status
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from .utils import *
from django.contrib.auth import authenticate
from rest_framework.response import Response
from .authentications import get_token_for_user
from .permissions import IsUserVerified
from django.utils import timezone
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from .serializers import *
from .tasks import send_otp_email, send_reset_password_email
from .models import OtpVerification
from .utils import generate_otp
from rest_framework.permissions import AllowAny
from .utils import format_errors

OTP_LIMIT = 5
OTP_TIME_LIMIT = timedelta(hours=1)



class Signup(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        # Initialize the serializer with the data from the request
        serializer = SignupSerializer(data=request.data)
        
        # Check if the serializer is valid
        if serializer.is_valid():
            # Save the validated data
            serializer.save()
            
            # Return a successful response with the serialized data
            return Response(
                {"data": serializer.data},
                status=status.HTTP_201_CREATED,
            )
        else:
            
            error_detail = format_errors(serializer.errors)
            
          
            return Response(
                {"detail": error_detail},
                status=status.HTTP_400_BAD_REQUEST
            )
    

   


class SendOtp(APIView):
    def post(self, request):
        email = request.data.get("email")
        user = get_object_or_404(User, email=email)
        otp = generate_otp()
        recent_otps = OtpVerification.objects.filter(
            user=user, created_at__gte=timezone.now() - OTP_TIME_LIMIT
        )
        if recent_otps.count() >= OTP_LIMIT:
            return Response(
                {"error": "OTP request limit reached. Please try again later."},
                status=status.HTTP_429_TOO_MANY_REQUESTS,
            )
        send_otp_email.delay(user.id, otp)
        OtpVerification.objects.create(user=user, otp=otp)
        return Response({"detail": "OTP sent successfully"}, status=status.HTTP_200_OK)


class VerifyOtp(APIView):
    def post(self, request):
        serializer = VerifyOtpSerializer(data=request.data)
        if serializer.is_valid():
            return Response(
                {"detail": "OTP verified successfully"}, status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserProfile(APIView):
    permission_classes = [IsAuthenticated, IsUserVerified]

    def get(self, request, user_id=None):
        if user_id:
            user = get_object_or_404(User, id=user_id)
        else:
            user = request.user
        serializer = ProfileSerializer(user)
        return Response({"data":serializer.data},status=status.HTTP_200_OK)

    def put(self, request):
        user = request.user
        if user:
            serializer = ProfileSerializer(
                instance=user, data=request.data, partial=True
            )
            if serializer.is_valid():
                serializer.save()
                return Response(
                    {
                        "data": serializer.data,
                    },
                    status=status.HTTP_202_ACCEPTED,
                )
              
            error_detail = format_errors(serializer.errors)
            return Response({"error": error_detail})


class Login(APIView):
    permission_classes = [IsUserVerified]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data["email"]
            password = serializer.validated_data["password"]
            user = authenticate(email=email, password=password)
            if user:
                token = get_token_for_user(user)
                return Response(
                    {"data":
                        { "refresh": str(token),
                        "access": str(token.access_token),
                        "access_token_expiration": token.access_token.payload["exp"],
                        "refresh_token_expiration": token.payload["exp"],
                        }
                    }
                )
            else:
                return Response(
                    {"error": "Email or Password is not Valid"},
                    status=status.HTTP_422_UNPROCESSABLE_ENTITY,
                )
          
        error_detail = format_errors(serializer.errors)
        return Response(
                    {"error": error_detail},
                    status=status.HTTP_400_BAD_REQUEST
                )
        


class UpdatePassword(APIView):
    permission_classes = [IsAuthenticated, IsUserVerified]

    def put(self, request):
        serializer = UpdateSerializer(data=request.data,context = {'request' : request})
        user = request.user
        if serializer.is_valid():
            current_password = serializer.validated_data["current_password"]
            if user.check_password(current_password):
                user.set_password(serializer.validated_data["new_password"])
                user.last_password_change = timezone.now()
                user.save()

                return Response(
                    {"message": "Password updated successfully"},
                    status=status.HTTP_202_ACCEPTED,
                )
            else:
                return Response(
                    {"detail": "Current password is incorrect."},
                    status=status.HTTP_422_UNPROCESSABLE_ENTITY,
                )
        error_detail = format_errors(serializer.errors)
        return Response(
            {"error": error_detail}, status=status.HTTP_400_BAD_REQUEST
        )


class SendResetPasswordEmail(APIView):
    permission_classes = [IsUserVerified]

    def post(self, request):
        serializer = SendResetPasswordEmailSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data["email"]
            user = User.objects.get(email=email)
            user_id = urlsafe_base64_encode(force_bytes(user.id))
            token = PasswordResetTokenGenerator().make_token(user)
            reset_link = f"{request.scheme}://{request.get_host()}/user/reset-password/{user_id}/{token}"
            send_reset_password_email(user.id, reset_link)
            return Response(
                {"message": "Password reset link sent successfully."},
                status=status.HTTP_200_OK,
            )
        return Response({"detail" : serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class ResetPassword(APIView):
    def put(self, request, user_id, token):
        serializer = ResetPasswordSerializer(
            data=request.data, context={"user_id": user_id, "token": token}
        )

        if serializer.is_valid():

            return Response(
                {"message": "Password Reset Successfully"}, status=status.HTTP_200_OK
            )
        error_detail = format_errors(serializer.errors)
        return Response(
            {"error": error_detail}, status=status.HTTP_400_BAD_REQUEST
        )


class Logout(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        if user:
            user.last_password_change = timezone.now()
            user.save()
            return Response(status=status.HTTP_204_NO_CONTENT)

        else:
            return Response({"detail": "You have to login first for the logout"})


class FollowRequestView(APIView):
    permission_classes = [IsAuthenticated, IsUserVerified]
     
 
    def get(self, request):
        user = request.user
        
        if not user.is_private:
            return Response({
                "detail " : "Account is Public not implement this request"
            })

        follow_requests_received = Follow.objects.filter(following_id=user.id, status="pending")

        # Fetch follow requests where the logged-in user is the 'follower' (sent requests)
        follow_requests_sent = Follow.objects.filter(follower_id=user.id, status="pending")

        # Serialize and return the follow requests
        received_serializer = FollowSerializer(follow_requests_received, many=True)
        sent_serializer = FollowSerializer(follow_requests_sent, many=True)

        return Response({
            "follow_requests_received": received_serializer.data,
            "follow_requests_sent": sent_serializer.data
        }, status=status.HTTP_200_OK)

class FollowRequestUpdateView(APIView):
    permission_classes = [IsAuthenticated, IsUserVerified]

    def post(self, request, follow_request_id, action):
        user = request.user
        follow_request = get_object_or_404(
            Follow,  following_id=user.id, status="pending"
        )
        if action == "accept":
            follow_request.status = "accepted"
            follow_request.save()
            return Response(
                {"detail": "Follow request accepted."}, status=status.HTTP_200_OK
            )
        elif action == "reject":
            follow_request.status = "rejected"
            follow_request.save()
            return Response(
                {"detail": "Follow request rejected."}, status=status.HTTP_200_OK
            )
        else:
            return Response(
                {"error": "Invalid action."}, status=status.HTTP_400_BAD_REQUEST
            )


class FollowView(APIView):
    permission_classes = [IsAuthenticated, IsUserVerified]
    def get(self, request, user_id=None):
        """Get followers and following of a user"""
        user = request.user if not user_id else get_object_or_404(User, id=user_id)
        

        followers = Follow.objects.filter(following=user,status = "accepted")
        following = Follow.objects.filter(follower=user,status = "accepted")
        followers_data = [{"id": f.follower.id, "username": f.follower.username} for f in followers if f.follower]
        following_data = [{"id": f.following.id, "username": f.following.username if f.following else "Unknown"} for f in following]

        return Response({"data":{
            "followers": followers_data,
            "following": following_data,
        }
        }
        )


    def post(self, request, user_id):
        """Follow a user (send follow request or directly follow)"""
        follower_user = request.user
        followed_user = get_object_or_404(User, id=user_id)

        if follower_user == followed_user:
            return Response(
                {"detail": "You cannot follow yourself."},
                status=status.HTTP_400_BAD_REQUEST,
            )
            
        if followed_user.is_private:
            follow, created = Follow.objects.get_or_create(
                follower=follower_user,
                following=followed_user,
                defaults={'status': 'pending'}
            )

            if not created:
                if follow.status == 'pending':
                    return Response(
                        {"detail": "Follow request is already pending."},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                elif follow.status == 'accepted':
                    return Response(
                        {"detail": "You are already following this user."},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                elif follow.status == 'rejected':
                    return Response(
                        {"detail": "Follow request was rejected. You can send a new request."},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            return Response(
                {"detail": "Follow request sent successfully. Waiting for approval."},
                status=status.HTTP_200_OK
            )
        
            
        if Follow.objects.filter(follower=follower_user, following=followed_user).exists():
            return Response(
                {"detail": "You are already following this user."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        Follow.objects.create(follower=follower_user, following=followed_user)
        return Response(
            {"detail": "Followed successfully."},
            status=status.HTTP_201_CREATED,
        )

    def delete(self, request, user_id):
        """Unfollow a user"""
        follower_user = request.user
        followed_user = get_object_or_404(User, id=user_id)
        follow = Follow.objects.filter(follower=follower_user, following=followed_user).first()

        if not follow:
            return Response(
                {"detail": "You are not following this user."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        follow.delete()
        return Response(
            {"detail": "Unfollowed successfully."},
            status=status.HTTP_204_NO_CONTENT,
        )


class AcceptFollowRequestView(APIView):
    permission_classes = [IsAuthenticated, IsUserVerified]

    def post(self, request, user_id):
        try:
            follow_request = Follow.objects.get(id=user_id, status='pending')
        except Follow.DoesNotExist:
            return Response({"detail": "Follow request not found or already processed."}, status=status.HTTP_404_NOT_FOUND)

        if follow_request.following != request.user:
            return Response({"detail": "You can only act on follow requests you have received."}, status=status.HTTP_403_FORBIDDEN)

        follow_request.status = "accepted"
        follow_request.save()

        return Response({"detail": "Follow request accepted."}, status=status.HTTP_200_OK)




   