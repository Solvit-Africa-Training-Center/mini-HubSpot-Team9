from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import UserRegistrationSerializer, UserLoginSerializer, UserSerializer


def get_tokens_for_user(user):
    """
    Utility function to generate JWT tokens for a given user.
    """
    refresh = RefreshToken.for_user(user)
    return {
        "refresh": str(refresh),
        "access": str(refresh.access_token),
    }


@api_view(["POST"])
@permission_classes([AllowAny])
def register(request):
    """
    Register a new user and return user details with JWT tokens.
    """
    serializer = UserRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        tokens = get_tokens_for_user(user)
        return Response(
            {
                "user": UserSerializer(user).data,
                "tokens": tokens,
            },
            status=status.HTTP_201_CREATED,
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
@permission_classes([AllowAny])
def login(request):
    """
    Authenticate a user and return user details with JWT tokens.
    """
    serializer = UserLoginSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data["user"]
        tokens = get_tokens_for_user(user)
        return Response(
            {
                "user": UserSerializer(user).data,
                "tokens": tokens,
            },
            status=status.HTTP_200_OK,
        )
    # Determine correct status code for invalid login
    return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)


@api_view(["POST"])
@permission_classes([AllowAny])
def token_refresh(request):
    """
    Refresh JWT access token using refresh token.
    """
    refresh_token = request.data.get("refresh")
    if not refresh_token:
        return Response({"detail": "Refresh token is required"}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        refresh = RefreshToken(refresh_token)
        access_token = str(refresh.access_token)
        return Response({
            "tokens": {
                "access": access_token, 
                "refresh": str(refresh)
            }
        })
    except Exception as e:
        return Response({"detail": "Invalid refresh token"}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def profile(request):
    """
    Retrieve the authenticated user's profile information.
    """
    serializer = UserSerializer(request.user)
    return Response(serializer.data, status=status.HTTP_200_OK)