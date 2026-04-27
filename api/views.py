from django.core import signing
from django.contrib.auth import get_user_model
from rest_framework import generics
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from appointment.models import AppointmentRequest
from blog.models import Category, Post
from contact.models import ContactSubmission
from services.models import Service
from team.models import TeamMember
from appointment.verification import (
    appointment_payload_from_data,
    create_verified_appointment,
    load_appointment_verification_payload,
    send_appointment_email_verification,
)

User = get_user_model()

from .emails import send_contact_submission_notification
from .serializers import (
    AppointmentRequestSerializer,
    CategorySerializer,
    ContactSubmissionSerializer,
    HomePageSerializer,
    PostDetailSerializer,
    PostListSerializer,
    PostWriteSerializer,
    ServiceSerializer,
    TeamMemberSerializer,
    DashboardUserSerializer,
    UserRegistrationSerializer,
    UserSerializer,
)


class ApiRootView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        return Response(
            {
                "home": request.build_absolute_uri("/api/home/"),
                "register": request.build_absolute_uri("/api/auth/register/"),
                "login": request.build_absolute_uri("/api/auth/login/"),
                "services": request.build_absolute_uri("/api/services/"),
                "team": request.build_absolute_uri("/api/team/"),
                "blog_posts": request.build_absolute_uri("/api/blog/posts/"),
                "blog_categories": request.build_absolute_uri("/api/blog/categories/"),
                "contact_submissions": request.build_absolute_uri("/api/contact-submissions/"),
                "appointments": request.build_absolute_uri("/api/appointments/"),
                "users": request.build_absolute_uri("/api/users/"),
            }
        )


class HomePageAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        serializer = HomePageSerializer(
            {
                "featured_services": Service.objects.filter(is_featured=True)[:3],
                "team_members": TeamMember.objects.filter(is_active=True)[:3],
                "latest_posts": Post.objects.published().select_related("category", "author")[:3],
            }
        )
        return Response(serializer.data)


class ServiceListAPIView(generics.ListCreateAPIView):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class ServiceDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
    lookup_field = "slug"
    permission_classes = [IsAuthenticatedOrReadOnly]


class TeamMemberListAPIView(generics.ListCreateAPIView):
    serializer_class = TeamMemberSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        if self.request.method == "GET":
            return TeamMember.objects.filter(is_active=True)
        return TeamMember.objects.all()


class TeamMemberDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = TeamMemberSerializer
    lookup_field = "slug"
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        return TeamMember.objects.all()


class CategoryListAPIView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    pagination_class = None
    permission_classes = [IsAuthenticatedOrReadOnly]


class PostListAPIView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return PostWriteSerializer
        return PostListSerializer

    def get_queryset(self):
        return Post.objects.published().select_related("category", "author")

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        response_serializer = PostDetailSerializer(serializer.instance)
        headers = self.get_success_headers(response_serializer.data)
        return Response(response_serializer.data, status=201, headers=headers)


class PostDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    lookup_field = "slug"
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        return Post.objects.select_related("category", "author")

    def get_serializer_class(self):
        if self.request.method in {"PUT", "PATCH"}:
            return PostWriteSerializer
        return PostDetailSerializer

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        response_serializer = PostDetailSerializer(serializer.instance)
        return Response(response_serializer.data)


class ContactSubmissionListCreateAPIView(generics.ListCreateAPIView):
    queryset = ContactSubmission.objects.all().order_by("-created_at")
    serializer_class = ContactSubmissionSerializer

    def get_permissions(self):
        if self.request.method == "POST":
            return [AllowAny()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        submission = serializer.save()
        send_contact_submission_notification(submission)


class AppointmentRequestListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = AppointmentRequestSerializer

    def get_permissions(self):
        if self.request.method == "POST":
            return [AllowAny()]
        return [IsAuthenticated()]

    def get_queryset(self):
        return AppointmentRequest.objects.select_related("service")

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        payload = appointment_payload_from_data(serializer.validated_data)
        send_appointment_email_verification(request, payload)
        return Response(
            {
                "detail": "Verification email sent. Please verify your email address to complete the appointment request."
            },
            status=status.HTTP_202_ACCEPTED,
        )


class AppointmentEmailVerifyAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, token, *args, **kwargs):
        try:
            payload = load_appointment_verification_payload(token)
        except signing.SignatureExpired:
            return Response(
                {"detail": "This verification link has expired."},
                status=status.HTTP_410_GONE,
            )
        except signing.BadSignature:
            return Response(
                {"detail": "This verification link is invalid."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        appointment = create_verified_appointment(payload)
        return Response(
            {
                "detail": "Appointment verified successfully.",
                "appointment_id": appointment.id,
            },
            status=status.HTTP_200_OK,
        )


class AppointmentRequestDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = AppointmentRequest.objects.select_related("service")
    serializer_class = AppointmentRequestSerializer
    permission_classes = [IsAuthenticated]


class DashboardUserListAPIView(generics.ListAPIView):
    serializer_class = DashboardUserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return User.objects.select_related("profile").order_by("username")


class CurrentUserAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        return Response(UserSerializer(request.user).data)


class RegisterUserAPIView(generics.CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = UserRegistrationSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return Response(
            {
                "user": UserSerializer(user).data,
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            },
            status=status.HTTP_201_CREATED,
        )
