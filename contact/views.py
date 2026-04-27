from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView

from .forms import ContactSubmissionForm
from .models import ContactSubmission


class ContactCreateView(CreateView):
    model = ContactSubmission
    form_class = ContactSubmissionForm
    template_name = "contact/contact_form.html"
    success_url = reverse_lazy("contact:success")


class ContactSuccessView(TemplateView):
    template_name = "contact/contact_success.html"
