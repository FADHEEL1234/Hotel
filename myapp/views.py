from django.db.models import Q
from django.shortcuts import get_object_or_404, render
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import redirect
from django.contrib.auth.views import LoginView
from django.urls import reverse
from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

from .forms import ProfileForm, UserUpdateForm
from .models import Booking, ContactMessage, Profile, TourImage, TourService


def home(request):
    latest_tours = TourService.objects.order_by("-created_at")[:3]
    return render(request, "myapp/home.html", {"latest_tours": latest_tours})


def tour_list(request):
    query = request.GET.get("q", "").strip()
    max_price = request.GET.get("max_price", "").strip()

    tours = TourService.objects.all()
    if query:
        tours = tours.filter(Q(title__icontains=query) | Q(location__icontains=query))
    if max_price:
        try:
            tours = tours.filter(price__lte=max_price)
        except ValueError:
            pass

    tours = tours.order_by("-created_at")
    context = {
        "tours": tours,
        "query": query,
        "max_price": max_price,
    }
    return render(request, "myapp/tour_list.html", context)


def tour_detail(request, tour_id):
    tour = get_object_or_404(TourService, pk=tour_id)
    gallery = TourImage.objects.filter(tour=tour)
    return render(request, "myapp/tour_detail.html", {"tour": tour, "gallery": gallery})


def contact(request):
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        email = request.POST.get("email", "").strip()
        subject = request.POST.get("subject", "").strip()
        destination = request.POST.get("destination", "").strip()
        message = request.POST.get("message", "").strip()

        errors = []
        if not name:
            errors.append("Please enter your name.")
        if not email:
            errors.append("Please enter your email.")
        if not message:
            errors.append("Please enter your message.")

        if not errors:
            ContactMessage.objects.create(
                user=request.user if request.user.is_authenticated else None,
                name=name,
                email=email,
                subject=subject,
                destination=destination,
                message=message,
            )
            messages.success(request, "Your message has been sent. We will reply soon.")
            return redirect("myapp:contact")

        return render(
            request,
            "myapp/contact.html",
            {"errors": errors, "form": request.POST},
        )

    return render(request, "myapp/contact.html")


def register(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("myapp:home")
    else:
        form = UserCreationForm()

    return render(request, "registration/register.html", {"form": form})


class CustomLoginView(LoginView):
    def get_success_url(self):
        if self.request.user.is_superuser:
            return "/admin/"
        if self.request.user.is_staff:
            return reverse("myapp:admin_dashboard")
        return reverse("myapp:home")


@login_required
def create_booking(request, tour_id):
    tour = get_object_or_404(TourService, pk=tour_id)
    if request.method == "POST":
        travel_date = request.POST.get("travel_date", "").strip()
        people = request.POST.get("people", "").strip()
        phone = request.POST.get("phone", "").strip()
        payment_method = request.POST.get("payment_method", "").strip()

        errors = []
        if not travel_date:
            errors.append("Please choose a travel date.")
        if not people.isdigit() or int(people) <= 0:
            errors.append("Please enter a valid number of people.")
        if not phone:
            errors.append("Please provide a phone number.")
        valid_methods = {choice[0] for choice in Booking.PAYMENT_CHOICES}
        if payment_method not in valid_methods:
            errors.append("Please choose a payment method.")

        if not errors:
            Booking.objects.create(
                tour=tour,
                user=request.user,
                travel_date=travel_date,
                people=int(people),
                phone=phone,
                payment_method=payment_method,
            )
            return redirect("myapp:booking_list")

        return render(
            request,
            "myapp/booking_form.html",
            {"tour": tour, "errors": errors, "form": request.POST},
        )

    return render(request, "myapp/booking_form.html", {"tour": tour})


@login_required
def booking_list(request):
    bookings = (
        Booking.objects.filter(user=request.user)
        .select_related("tour")
        .order_by("-created_at")
    )
    return render(request, "myapp/booking_list.html", {"bookings": bookings})


@login_required
def profile(request):
    profile_obj = getattr(request.user, "profile", None)
    if profile_obj is None:
        profile_obj = Profile.objects.create(user=request.user)

    if request.method == "POST":
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileForm(request.POST, request.FILES, instance=profile_obj)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, "Profile updated successfully.")
            return redirect("myapp:profile")
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileForm(instance=profile_obj)

    return render(
        request,
        "myapp/profile.html",
        {"user_form": user_form, "profile_form": profile_form},
    )


@login_required
def message_notifications(request):
    messages_qs = (
        ContactMessage.objects.filter(user=request.user, reply__isnull=False)
        .exclude(reply="")
        .order_by("-replied_at", "-created_at")
    )
    unread_count = messages_qs.filter(is_read=False).count()
    if messages_qs.exists():
        messages_qs.filter(is_read=False).update(is_read=True)
    return render(
        request,
        "myapp/message_notifications.html",
        {"messages": messages_qs, "unread_count": unread_count},
    )


@user_passes_test(lambda u: u.is_staff)
def admin_dashboard(request):
    bookings = Booking.objects.select_related("tour", "user").order_by("-created_at")
    total = bookings.count()
    pending = bookings.filter(status=Booking.STATUS_PENDING).count()
    confirmed = bookings.filter(status=Booking.STATUS_CONFIRMED)
    cancelled = bookings.filter(status=Booking.STATUS_CANCELLED).count()
    revenue = sum(b.tour.price * b.people for b in confirmed)

    context = {
        "total": total,
        "pending": pending,
        "confirmed_count": confirmed.count(),
        "cancelled": cancelled,
        "revenue": revenue,
        "recent": bookings[:8],
    }
    return render(request, "myapp/admin_dashboard.html", context)




@login_required
def booking_receipt(request, booking_id):
    booking = get_object_or_404(
        Booking.objects.select_related("tour", "user"),
        pk=booking_id,
        user=request.user,
    )
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="receipt-{booking.id}.pdf"'

    pdf = canvas.Canvas(response, pagesize=letter)
    width, height = letter
    y = height - 72

    pdf.setFont("Helvetica-Bold", 18)
    pdf.drawString(72, y, "Tourism Hotel - Booking Receipt")
    y -= 28

    pdf.setFont("Helvetica", 11)
    pdf.drawString(72, y, f"Reference: TR-{booking.id:05d}")
    y -= 20
    pdf.drawString(72, y, f"Guest: {booking.user.username}")
    y -= 20
    pdf.drawString(72, y, f"Tour: {booking.tour.title} ({booking.tour.location})")
    y -= 20
    pdf.drawString(72, y, f"Travel date: {booking.travel_date}")
    y -= 20
    pdf.drawString(72, y, f"People: {booking.people}")
    y -= 20
    pdf.drawString(72, y, f"Phone: {booking.phone}")
    y -= 20
    pdf.drawString(72, y, f"Payment method: {booking.get_payment_method_display()}")
    y -= 20
    pdf.drawString(72, y, f"Status: {booking.get_status_display()}")
    y -= 20
    pdf.drawString(72, y, f"Booked on: {booking.created_at.strftime('%B %d, %Y')}")

    pdf.showPage()
    pdf.save()
    return response
