from django.conf import settings
from django.core import signing
from django.core.mail import send_mail
from django.urls import reverse
from django.utils.dateparse import parse_date, parse_time

from api.emails import (
    send_appointment_request_confirmation,
    send_appointment_request_notification,
)
from api.sms import send_appointment_request_sms_confirmation
from services.models import Service

from .models import AppointmentRequest


def appointment_payload_from_data(data):
    service = data.get("service")
    return {
        "name": data.get("name", ""),
        "email": data.get("email", ""),
        "phone": data.get("phone", ""),
        "address": data.get("address", ""),
        "country": data.get("country", AppointmentRequest.Country.DRC),
        "office": data.get("office", AppointmentRequest.Office.KINSHASA),
        "service_id": service.pk if service else None,
        "preferred_date": data["preferred_date"].isoformat(),
        "preferred_time": data["preferred_time"].isoformat() if data.get("preferred_time") else None,
        "message": data.get("message", ""),
    }


def make_appointment_verification_token(payload):
    return signing.dumps(payload, salt=settings.APPOINTMENT_EMAIL_VERIFICATION_SALT)


def load_appointment_verification_payload(token):
    return signing.loads(
        token,
        salt=settings.APPOINTMENT_EMAIL_VERIFICATION_SALT,
        max_age=settings.APPOINTMENT_EMAIL_VERIFICATION_MAX_AGE,
    )


def send_appointment_email_verification(request, payload):
    token = make_appointment_verification_token(payload)
    if settings.FRONTEND_BASE_URL:
        frontend_verify_path = settings.APPOINTMENT_FRONTEND_VERIFY_PATH.rstrip("/")
        verify_url = (
            f"{settings.FRONTEND_BASE_URL.rstrip('/')}"
            f"{frontend_verify_path}/{token}/"
        )
    else:
        verify_path = reverse("appointment:verify-email", kwargs={"token": token})
        verify_url = request.build_absolute_uri(verify_path)
    message = "\n".join(
        [
            f"Dear {payload['name']},",
            "",
            "Please confirm your email address to complete your appointment request.",
            "Your appointment will be saved only after you open this verification link:",
            "",
            verify_url,
            "",
            "If you did not request an appointment, you can ignore this email.",
            "",
            "Cabinet Nyamugabo",
        ]
    )
    send_mail(
        subject=settings.APPOINTMENT_EMAIL_VERIFICATION_SUBJECT,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[payload["email"]],
        fail_silently=True,
    )


def create_verified_appointment(payload):
    service = None
    service_id = payload.get("service_id")
    if service_id:
        service = Service.objects.filter(pk=service_id).first()

    appointment = AppointmentRequest.objects.create(
        name=payload["name"],
        email=payload["email"],
        phone=payload.get("phone", ""),
        address=payload.get("address", ""),
        country=payload.get("country", AppointmentRequest.Country.DRC),
        office=payload.get("office", AppointmentRequest.Office.KINSHASA),
        service=service,
        preferred_date=parse_date(payload["preferred_date"]),
        preferred_time=parse_time(payload["preferred_time"]) if payload.get("preferred_time") else None,
        message=payload.get("message", ""),
    )
    send_appointment_request_notification(appointment)
    send_appointment_request_confirmation(appointment)
    send_appointment_request_sms_confirmation(appointment)
    return appointment
