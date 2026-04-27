from django.contrib.auth import get_user_model
from rest_framework import serializers

from appointment.models import AppointmentRequest
from blog.models import Category, Post
from contact.models import ContactSubmission
from services.models import Service
from team.models import TeamMember
from account.models import UserProfile

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "is_staff",
            "is_superuser",
        ]
        read_only_fields = ["id", "is_staff", "is_superuser"]


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "password",
        ]
        read_only_fields = ["id"]

    def validate_email(self, value):
        if value and User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def validate_username(self, value):
        if User.objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError("A user with this username already exists.")
        return value

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = [
            "id",
            "title",
            "slug",
            "short_description",
            "description",
            "icon",
            "is_featured",
            "order",
        ]


class TeamMemberSerializer(serializers.ModelSerializer):
    full_name = serializers.ReadOnlyField()

    class Meta:
        model = TeamMember
        fields = [
            "id",
            "first_name",
            "last_name",
            "full_name",
            "slug",
            "role",
            "bio",
            "email",
            "phone",
            "linkedin_url",
            "photo_url",
            "is_active",
            "order",
        ]


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = [
            "phone",
            "role_title",
            "bio",
            "avatar_url",
            "is_dashboard_user",
        ]


class DashboardUserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "is_staff",
            "is_superuser",
            "profile",
        ]


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "slug", "description"]


class PostListSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    author = TeamMemberSerializer(read_only=True)

    class Meta:
        model = Post
        fields = [
            "id",
            "title",
            "slug",
            "summary",
            "category",
            "author",
            "featured_image_url",
            "published_at",
        ]


class PostDetailSerializer(PostListSerializer):
    class Meta(PostListSerializer.Meta):
        fields = PostListSerializer.Meta.fields + ["body"]


class PostWriteSerializer(serializers.ModelSerializer):
    category_id = serializers.PrimaryKeyRelatedField(
        source="category",
        queryset=Category.objects.all(),
        required=False,
        allow_null=True,
    )
    author_id = serializers.PrimaryKeyRelatedField(
        source="author",
        queryset=TeamMember.objects.all(),
        required=False,
        allow_null=True,
    )

    class Meta:
        model = Post
        fields = [
            "id",
            "title",
            "slug",
            "summary",
            "body",
            "category_id",
            "author_id",
            "status",
            "featured_image_url",
            "published_at",
        ]


class ContactSubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactSubmission
        fields = ["id", "name", "email", "phone", "subject", "message", "status", "created_at"]
        read_only_fields = ["id", "status", "created_at"]


class AppointmentRequestSerializer(serializers.ModelSerializer):
    service = ServiceSerializer(read_only=True)
    service_id = serializers.PrimaryKeyRelatedField(
        source="service",
        queryset=Service.objects.all(),
        write_only=True,
        required=False,
        allow_null=True,
    )

    class Meta:
        model = AppointmentRequest
        fields = [
            "id",
            "name",
            "email",
            "phone",
            "address",
            "country",
            "office",
            "service",
            "service_id",
            "preferred_date",
            "preferred_time",
            "message",
            "status",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]

    def validate_preferred_date(self, value):
        from django.utils import timezone

        if value < timezone.localdate():
            raise serializers.ValidationError("Preferred date cannot be in the past.")
        return value


class HomePageSerializer(serializers.Serializer):
    featured_services = ServiceSerializer(many=True)
    team_members = TeamMemberSerializer(many=True)
    latest_posts = PostListSerializer(many=True)
