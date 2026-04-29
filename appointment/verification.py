from html import escape

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


def get_public_frontend_base_url():
    frontend_base_url = settings.FRONTEND_BASE_URL
    if not settings.DEBUG and (
        not frontend_base_url
        or frontend_base_url.startswith("http://127.0.0.1")
        or frontend_base_url.startswith("http://localhost")
    ):
        return settings.DEFAULT_FRONTEND_BASE_URL
    return frontend_base_url


def send_appointment_email_verification(request, payload):
    token = make_appointment_verification_token(payload)
    frontend_base_url = get_public_frontend_base_url()
    if frontend_base_url:
        frontend_verify_path = settings.APPOINTMENT_FRONTEND_VERIFY_PATH.rstrip("/")
        verify_url = (
            f"{frontend_base_url.rstrip('/')}"
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
    escaped_name = escape(payload["name"])
    escaped_url = escape(verify_url)
    html_message = f"""
    <div style="margin:0;padding:0;background:#f4f6f8;font-family:Arial,Helvetica,sans-serif;color:#1f2937;">
      <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="background:#f4f6f8;padding:32px 12px;">
        <tr>
          <td align="center">
            <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="max-width:640px;background:#ffffff;border:1px solid #e5e7eb;border-radius:14px;overflow:hidden;">
              <tr>
                <td style="background:#0d4595;padding:28px 32px;color:#ffffff;">
                  <p style="margin:0 0 8px;font-size:12px;letter-spacing:2px;text-transform:uppercase;color:#f2b51d;font-weight:700;">Cabinet Nyamugabo</p>
                  <h1 style="margin:0;font-size:26px;line-height:1.25;font-weight:700;">Verification de votre adresse email</h1>
                </td>
              </tr>
              <tr>
                <td style="padding:32px;">
                  <p style="margin:0 0 18px;font-size:16px;line-height:1.7;">Bonjour {escaped_name},</p>
                  <p style="margin:0 0 22px;font-size:16px;line-height:1.7;">
                    Merci pour votre demande de rendez-vous. Pour proteger vos informations, veuillez confirmer votre adresse email avant l'enregistrement definitif de la demande.
                  </p>
                  <table role="presentation" cellspacing="0" cellpadding="0" style="margin:28px 0;">
                    <tr>
                      <td style="border-radius:8px;background:#b91c1c;">
                        <a href="{escaped_url}" style="display:inline-block;padding:15px 24px;color:#ffffff;text-decoration:none;font-size:14px;font-weight:700;letter-spacing:0.4px;text-transform:uppercase;">
                          Cliquer ici pour verifier
                        </a>
                      </td>
                    </tr>
                  </table>
                  <p style="margin:0 0 16px;font-size:14px;line-height:1.7;color:#6b7280;">
                    Si le bouton ne fonctionne pas, copiez ce lien dans votre navigateur:
                  </p>
                  <p style="margin:0 0 24px;word-break:break-all;font-size:13px;line-height:1.6;color:#0d4595;">
                    <a href="{escaped_url}" style="color:#0d4595;">{escaped_url}</a>
                  </p>
                  <p style="margin:0;font-size:14px;line-height:1.7;color:#6b7280;">
                    Si vous n'avez pas demande de rendez-vous, vous pouvez ignorer cet email.
                  </p>
                </td>
              </tr>
              <tr>
                <td style="background:#f9fafb;padding:20px 32px;border-top:1px solid #e5e7eb;">
                  <p style="margin:0;font-size:13px;color:#6b7280;">Cabinet Nyamugabo - Avocats d'Affaires</p>
                </td>
              </tr>
            </table>
          </td>
        </tr>
      </table>
    </div>
    """
    send_mail(
        subject=settings.APPOINTMENT_EMAIL_VERIFICATION_SUBJECT,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[payload["email"]],
        fail_silently=True,
        html_message=html_message,
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
