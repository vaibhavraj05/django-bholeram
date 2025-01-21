Instagram app Backend
=======
Instagram App Backend
This backend API for an Instagram-like application includes functionalities for user authentication, post management, friend requests, and more. Built with Django and Django REST Framework, this project provides endpoints for user signup, authentication, post creation, friend requests, and other core social media functionalities.

Features
1. User Authentication
Signup API: Allows users to sign up with username, email, password, first_name, and last_name.
After signing up, users must verify their email to activate their account.
Send OTP API: Sends a One-Time Password (OTP) to the provided email for verification during the signup process.
Login API: Authenticates users using email and password, issuing a token on successful login.

2. User Profile
Profile Update: Users can update their profile information, including bio, profile picture, and social media links.
Public/Private Account Option: During signup, users can choose to have a public or private account. If the account is private, only friends can access their posts and profile information.

3. Friend Requests and Social Connections
Send Friend Request: Users can send friend requests to other users. If the other user accepts, they become friends.
Accept/Reject Friend Request: Users can accept or reject incoming friend requests.
View Friend Requests: Users can view all pending friend requests sent to them.
Follow Feature: Users can follow public accounts without needing to send a friend request.


4. Post Management
Create Post: Users can create new posts with images, captions, and more.
View Posts: Users can view posts based on privacy settings; only friends can view private posts.
Like and Comment: Users can like and comment on posts, creating interactions.


5. Feed and Saved Posts
User Feed: Displays posts from friends and public accounts the user follows.
Save Post: Users can save posts to their profile for later viewing.
Retrieve Saved Posts: Users can retrieve a list of saved posts.


API Endpoints

Authentication
POST /auth/signup/: Register a new user.
POST /auth/send-otp/: Send OTP to user's email for verification.
POST /auth/login/: Login and receive authentication token.
POST /auth/logout/: Logout the user and invalidate the token.

Profile Management
GET /profile/: Retrieve user profile details.
PUT /profile/update/: Update user profile information.
GET /profile/friends/: View list of friends.


Friend Request Management
POST /friend-requests/: Send a friend request.
GET /friend-requests/: List all pending friend requests.
PUT /friend-requests/<request_id>/: Accept or reject a friend request.

Post Management
POST /posts/: Create a new post.
GET /posts/: Retrieve posts (filtered by privacy settings).
POST /posts/<post_id>/like/: Like a post.
POST /posts/<post_id>/comment/: Comment on a post.

Feed and Saved Posts
GET /feed/: Retrieve user feed.
POST /posts/<post_id>/save/: Save a post to the user’s profile.
GET /saved-posts/: Retrieve a list of saved posts.
>>>>>>> df8f4ddba4596329ed2c0dcece7f066181919053
