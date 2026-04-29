from html import escape

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
    escaped_name = escape(appointment.name)
    escaped_service = escape(service)
    escaped_office = escape(appointment.get_office_display())
    escaped_date = escape(str(appointment.preferred_date))
    escaped_time = escape(preferred_time)
    html_message = f"""
    <div style="margin:0;padding:0;background:#f4f6f8;font-family:Arial,Helvetica,sans-serif;color:#1f2937;">
      <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="background:#f4f6f8;padding:32px 12px;">
        <tr>
          <td align="center">
            <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="max-width:640px;background:#ffffff;border:1px solid #e5e7eb;border-radius:14px;overflow:hidden;">
              <tr>
                <td style="background:#0d4595;padding:28px 32px;color:#ffffff;">
                  <p style="margin:0 0 8px;font-size:12px;letter-spacing:2px;text-transform:uppercase;color:#f2b51d;font-weight:700;">Cabinet Nyamugabo</p>
                  <h1 style="margin:0;font-size:26px;line-height:1.25;font-weight:700;">Votre demande de rendez-vous est recue</h1>
                </td>
              </tr>
              <tr>
                <td style="padding:32px;">
                  <p style="margin:0 0 18px;font-size:16px;line-height:1.7;">Bonjour {escaped_name},</p>
                  <p style="margin:0 0 24px;font-size:16px;line-height:1.7;">
                    Votre adresse email a ete verifiee et votre demande de rendez-vous a bien ete enregistree. Notre equipe vous contactera pour confirmer la disponibilite.
                  </p>
                  <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="border-collapse:collapse;border:1px solid #e5e7eb;border-radius:10px;overflow:hidden;">
                    <tr>
                      <td style="padding:14px 18px;background:#f9fafb;color:#6b7280;font-size:13px;font-weight:700;text-transform:uppercase;letter-spacing:0.6px;">Service</td>
                      <td style="padding:14px 18px;font-size:15px;color:#111827;">{escaped_service}</td>
                    </tr>
                    <tr>
                      <td style="padding:14px 18px;background:#f9fafb;color:#6b7280;font-size:13px;font-weight:700;text-transform:uppercase;letter-spacing:0.6px;">Bureau</td>
                      <td style="padding:14px 18px;font-size:15px;color:#111827;">{escaped_office}</td>
                    </tr>
                    <tr>
                      <td style="padding:14px 18px;background:#f9fafb;color:#6b7280;font-size:13px;font-weight:700;text-transform:uppercase;letter-spacing:0.6px;">Date preferee</td>
                      <td style="padding:14px 18px;font-size:15px;color:#111827;">{escaped_date}</td>
                    </tr>
                    <tr>
                      <td style="padding:14px 18px;background:#f9fafb;color:#6b7280;font-size:13px;font-weight:700;text-transform:uppercase;letter-spacing:0.6px;">Heure preferee</td>
                      <td style="padding:14px 18px;font-size:15px;color:#111827;">{escaped_time}</td>
                    </tr>
                  </table>
                  <p style="margin:24px 0 0;font-size:14px;line-height:1.7;color:#6b7280;">
                    Si une information est incorrecte, veuillez repondre directement a cet email.
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
        subject=settings.APPOINTMENT_CONFIRMATION_SUBJECT,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[appointment.email],
        fail_silently=True,
        html_message=html_message,
    )
