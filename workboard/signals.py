# workboard/signals.py
from django.core.mail import send_mail
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from .models import Task

@receiver(post_save, sender=Task)
def send_task_notification(sender, instance, created, **kwargs):
    if created:
        subject = f"New Task Created: {instance.description}"
        message = f"A new task '{instance.description}' has been created."
    else:
        subject = f"Task Updated: {instance.description}"
        message = f"Task '{instance.description}' has been updated."

    # Gửi email cho người tạo công việc và người được giao
    send_mail(
        subject,
        message,
        settings.EMAIL_HOST_USER,  # Địa chỉ email người gửi
        [instance.assigned_to.email],  # Người được giao công việc
        fail_silently=False,
    )
