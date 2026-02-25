from .models import ContactMessage


def unread_messages(request):
    if not request.user.is_authenticated:
        return {"unread_messages": 0}
    count = ContactMessage.objects.filter(
        user=request.user,
        reply__isnull=False,
    ).exclude(reply="").filter(is_read=False).count()
    return {"unread_messages": count}
