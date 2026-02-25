from django.db import models
from django.contrib.auth import get_user_model

class TourService(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    location = models.CharField(max_length=100)
    image = models.ImageField(upload_to="tours/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class TourImage(models.Model):
    tour = models.ForeignKey(TourService, on_delete=models.CASCADE, related_name="gallery")
    image = models.ImageField(upload_to="tours/gallery/")
    caption = models.CharField(max_length=120, blank=True)

    def __str__(self):
        return f"{self.tour.title} image"


class Booking(models.Model):
    STATUS_PENDING = "pending"
    STATUS_CONFIRMED = "confirmed"
    STATUS_CANCELLED = "cancelled"

    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_CONFIRMED, "Confirmed"),
        (STATUS_CANCELLED, "Cancelled"),
    ]

    PAYMENT_MPESA = "mpesa"
    PAYMENT_TIGOPESA = "tigopesa"
    PAYMENT_AIRTEL = "airtel"
    PAYMENT_CRDB = "crdb"
    PAYMENT_NMB = "nmb"
    PAYMENT_CASH = "cash"

    PAYMENT_CHOICES = [
        (PAYMENT_MPESA, "M-Pesa"),
        (PAYMENT_TIGOPESA, "Tigo Pesa"),
        (PAYMENT_AIRTEL, "Airtel Money"),
        (PAYMENT_CRDB, "CRDB"),
        (PAYMENT_NMB, "NMB"),
        (PAYMENT_CASH, "Cash"),
    ]

    tour = models.ForeignKey(TourService, on_delete=models.CASCADE, related_name="bookings")
    user = models.ForeignKey("auth.User", on_delete=models.CASCADE, related_name="bookings")
    travel_date = models.DateField()
    people = models.PositiveIntegerField()
    phone = models.CharField(max_length=30)
    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_CHOICES,
        default=PAYMENT_MPESA,
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.tour.title}"


class Profile(models.Model):
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE, related_name="profile")
    phone = models.CharField(max_length=30, blank=True)
    avatar = models.ImageField(upload_to="profiles/", blank=True, null=True)

    def __str__(self):
        return self.user.username


class ContactMessage(models.Model):
    user = models.ForeignKey("auth.User", on_delete=models.SET_NULL, null=True, blank=True, related_name="contact_messages")
    name = models.CharField(max_length=120)
    email = models.EmailField()
    subject = models.CharField(max_length=200, blank=True)
    destination = models.CharField(max_length=120, blank=True)
    message = models.TextField()
    reply = models.TextField(blank=True)
    is_read = models.BooleanField(default=False)
    replied_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.subject or 'Contact message'}"


# Create your models here.
