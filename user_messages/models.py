from django.db import models
from django.contrib.auth.models import User

class user_messages(models.Model):
    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sent_messages'
    )

    receiver = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='received_messages',
        null=True,
        blank=True
    )

    # ✅ FIX: allow empty subject for drafts
    subject = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    body = models.TextField(
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    is_draft = models.BooleanField(default=False)

    def __str__(self):
        # ✅ Prevent None showing in admin
        return self.subject if self.subject else "(No Subject)"