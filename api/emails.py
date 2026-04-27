from django.conf import settings
from django.core.mail import send_mail


def send_contact_submission_notification(submission):
    recipients = getattr(settings, "CONTACT_NOTIFICATION_EMAILS", [])
    if not recipients:
        return

    message = "\n".join(
        [
            "New contact submission received.",
            "",
            f"Name: {submission.name}",
            f"Email: {submission.email}",
            f"Phone: {submission.phone or '-'}",
            f"Subject: {submission.subject}",
            "",
            submission.message,
        ]
    )
    send_mail(
        subject=f"New contact submission: {submission.subject}",
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=recipients,
        fail_silently=True,
    )


def send_appointment_request_notification(appointment):
    recipients = getattr(settings, "APPOINTMENT_NOTIFICATION_EMAILS", [])
    if not recipients:
        return

    service = appointment.service.title if appointment.service else "-"
    preferred_time = appointment.preferred_time.strftime("%H:%M") if appointment.preferred_time else "-"
    message = "\n".join(
        [
            "New appointment request received.",
            "",
            f"Name: {appointment.name}",
            f"Email: {appointment.email}",
            f"Phone: {appointment.phone or '-'}",
            f"Address: {appointment.address or '-'}",
            f"Country: {appointment.get_country_display()}",
            f"Office: {appointment.get_office_display()}",
            f"Service: {service}",
            f"Preferred date: {appointment.preferred_date}",
            f"Preferred time: {preferred_time}",
            "",
            appointment.message or "-",
        ]
    )
    send_mail(
        subject=f"New appointment request: {appointment.name}",
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=recipients,
        fail_silently=True,
    )


def send_appointment_request_confirmation(appointment):
    if not appointment.email:
        return

    service = appointment.service.title if appointment.service else "your selected service"
    preferred_time = appointment.preferred_time.strftime("%H:%M") if appointment.preferred_time else "-"
    message = "\n".join(
        [
            f"Dear {appointment.name},",
            "",
            "Thank you for booking an appointment with Cabinet Nyamugabo.",
            "We have received your request and our team will contact you to confirm availability.",
            "",
            "Appointment details:",
            f"Service: {service}",
            f"Office: {appointment.get_office_display()}",
            f"Preferred date: {appointment.preferred_date}",
            f"Preferred time: {preferred_time}",
            "",
            "If any of these details are incorrect, please reply to this email.",
            "",
            "Cabinet Nyamugabo",
        ]
    )
    send_mail(
        subject=settings.APPOINTMENT_CONFIRMATION_SUBJECT,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[appointment.email],
        fail_silently=True,
    )
