from django.db import models


class AppointmentRequest(models.Model):
    class Country(models.TextChoices):
        DRC = "CD", "Democratic Republic of the Congo"
        RWANDA = "RW", "Rwanda"
        BURUNDI = "BI", "Burundi"
        UGANDA = "UG", "Uganda"
        KENYA = "KE", "Kenya"
        TANZANIA = "TZ", "Tanzania"
        CONGO = "CG", "Republic of the Congo"
        SOUTH_AFRICA = "ZA", "South Africa"
        BELGIUM = "BE", "Belgium"
        CHINA = "CN", "China"
        FRANCE = "FR", "France"
        CANADA = "CA", "Canada"
        UNITED_STATES = "US", "United States"
        UNITED_KINGDOM = "GB", "United Kingdom"
        OTHER = "ZZ", "Other / Not listed"

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        CONFIRMED = "confirmed", "Confirmed"
        COMPLETED = "completed", "Completed"
        CANCELLED = "cancelled", "Cancelled"

    class Office(models.TextChoices):
        KINSHASA = "kinshasa", "Kinshasa"
        BUKAVU = "bukavu", "Bukavu"

    name = models.CharField(max_length=150)
    email = models.EmailField()
    phone = models.CharField(max_length=30, blank=True)
    address = models.CharField(max_length=255, blank=True)
    country = models.CharField(max_length=2, choices=Country.choices, default=Country.DRC)
    office = models.CharField(max_length=20, choices=Office.choices, default=Office.KINSHASA)
    service = models.ForeignKey(
        "services.Service",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="appointment_requests",
    )
    preferred_date = models.DateField()
    preferred_time = models.TimeField(null=True, blank=True)
    message = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["preferred_date", "preferred_time", "-created_at"]

    def __str__(self):
        return f"{self.name} - {self.preferred_date}"
