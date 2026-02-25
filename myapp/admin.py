from django.contrib import admin
from django.core.mail import send_mail
from django.urls import reverse
from django.utils import timezone
from django.utils.html import format_html, format_html_join

from .models import Booking, ContactMessage, Profile, TourImage, TourService


class TourImageInline(admin.TabularInline):
    model = TourImage
    extra = 1


@admin.register(TourService)
class TourServiceAdmin(admin.ModelAdmin):
    list_display = ("title", "location", "price", "created_at")
    search_fields = ("title", "location")
    inlines = [TourImageInline]


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ("tour", "user", "travel_date", "people", "payment_method", "status", "created_at")
    list_filter = ("status", "payment_method", "travel_date")
    search_fields = ("tour__title", "user__username", "phone")

    def save_model(self, request, obj, form, change):
        previous_status = None
        if change:
            previous_status = Booking.objects.get(pk=obj.pk).status
        super().save_model(request, obj, form, change)

        if change and previous_status != obj.status and obj.user.email:
            subject = f"Booking status updated: {obj.get_status_display()}"
            message = (
                f"Hello {obj.user.username},\n\n"
                f"Your booking for {obj.tour.title} is now marked as {obj.get_status_display()}.\n"
                f"Travel date: {obj.travel_date}\n"
                f"People: {obj.people}\n"
                f"Payment method: {obj.get_payment_method_display()}\n\n"
                "Thank you for choosing Tourism Hotel."
            )
            send_mail(subject, message, None, [obj.user.email], fail_silently=True)


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "phone", "booking_count", "last_travel_date")
    readonly_fields = ("stay_history",)
    fieldsets = (
        (None, {"fields": ("user", "phone", "avatar")}),
        ("Stay History", {"fields": ("stay_history",)}),
    )

    def booking_count(self, obj):
        return obj.user.bookings.count()

    booking_count.short_description = "Total bookings"

    def last_travel_date(self, obj):
        return (
            obj.user.bookings.order_by("-travel_date")
            .values_list("travel_date", flat=True)
            .first()
        )

    last_travel_date.short_description = "Last travel date"

    def stay_history(self, obj):
        bookings = (
            obj.user.bookings.select_related("tour")
            .order_by("-travel_date")
            .all()
        )
        if not bookings:
            return "No stays yet."
        return format_html_join(
            "<br/>",
            "{} — {} — {} people — {}",
            (
                (
                    format_html(
                        '<a href="{}">{}</a>',
                        reverse("admin:myapp_booking_change", args=(booking.pk,)),
                        booking.travel_date,
                    ),
                    booking.tour.title,
                    booking.people,
                    booking.get_status_display(),
                )
                for booking in bookings
            ),
        )

    stay_history.short_description = "Stay history"


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "subject", "destination", "created_at", "replied_at", "user")
    search_fields = ("name", "email", "subject", "destination", "message", "reply", "user__username")
    list_filter = ("created_at", "replied_at")

    def save_model(self, request, obj, form, change):
        previous_reply = None
        if change:
            previous_reply = ContactMessage.objects.get(pk=obj.pk).reply

        if obj.reply and obj.reply != previous_reply:
            obj.replied_at = timezone.now()
            obj.is_read = False

        super().save_model(request, obj, form, change)

        if obj.reply and obj.email and obj.reply != previous_reply:
            subject = obj.subject or "Reply to your message"
            message = (
                f"Hello {obj.name},\n\n"
                f"{obj.reply}\n\n"
                "Thank you for contacting Tourism Hotel."
            )
            send_mail(subject, message, None, [obj.email], fail_silently=True)

# Register your models here.
