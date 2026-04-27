import base64
import urllib.parse
import urllib.request

from django.conf import settings


def send_sms(to_number, message):
    if not settings.SMS_ENABLED:
        return False
    if settings.SMS_PROVIDER != "twilio":
        return False
    if not all(
        [
            settings.TWILIO_ACCOUNT_SID,
            settings.TWILIO_AUTH_TOKEN,
            settings.TWILIO_FROM_NUMBER,
            to_number,
            message,
        ]
    ):
        return False

    url = f"https://api.twilio.com/2010-04-01/Accounts/{settings.TWILIO_ACCOUNT_SID}/Messages.json"
    payload = urllib.parse.urlencode(
        {
            "From": settings.TWILIO_FROM_NUMBER,
            "To": to_number,
            "Body": message,
        }
    ).encode()
    credentials = f"{settings.TWILIO_ACCOUNT_SID}:{settings.TWILIO_AUTH_TOKEN}".encode()
    auth_header = base64.b64encode(credentials).decode()
    request = urllib.request.Request(
        url,
        data=payload,
        headers={
            "Authorization": f"Basic {auth_header}",
            "Content-Type": "application/x-www-form-urlencoded",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=settings.SMS_TIMEOUT):
            return True
    except Exception:
        return False


def send_appointment_request_sms_confirmation(appointment):
    if not appointment.phone:
        return False

    preferred_time = appointment.preferred_time.strftime("%H:%M") if appointment.preferred_time else "-"
    message = settings.APPOINTMENT_SMS_CONFIRMATION_MESSAGE.format(
        name=appointment.name,
        office=appointment.get_office_display(),
        preferred_date=appointment.preferred_date,
        preferred_time=preferred_time,
    )
    return send_sms(appointment.phone, message)
