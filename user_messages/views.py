# Author: Theoayman Haid De Azevedo
# Individual element - wrote the code

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from .models import user_messages


@login_required
def messages_page(request):
    inbox = user_messages.objects.filter(receiver=request.user, is_draft=False)
    sent = user_messages.objects.filter(sender=request.user, is_draft=False)
    drafts = user_messages.objects.filter(sender=request.user, is_draft=True)

    message_id = request.GET.get("message_id")
    selected_message = None
    mode = "new"

    if message_id:
        selected_message = user_messages.objects.filter(id=message_id).first()
        if selected_message and (selected_message.sender == request.user or selected_message.receiver == request.user):
            if selected_message.is_draft and selected_message.sender == request.user:
                mode = "edit"
            else:
                mode = "view"
        else:
            selected_message = None

    if request.method == "POST":
        action = request.POST.get("action")
        draft_id = request.POST.get("draft_id")
        receiver_email = request.POST.get("receiver_email", "").strip()
        subject = request.POST.get("subject", "").strip()
        body = request.POST.get("body", "").strip()

        if action == "delete" and draft_id:
            draft = user_messages.objects.filter(
                id=draft_id,
                sender=request.user,
                is_draft=True
            ).first()
            if draft:
                draft.delete()
            return redirect("/messages/")

        receiver = User.objects.filter(email=receiver_email).first() if receiver_email else None

        if action == "send":
            if not receiver or not subject:
                return redirect("/messages/")

            if draft_id:
                msg = get_object_or_404(user_messages, id=draft_id, sender=request.user, is_draft=True)
                msg.receiver = receiver
                msg.subject = subject
                msg.body = body
                msg.is_draft = False
                msg.save()
            else:
                user_messages.objects.create(
                    sender=request.user,
                    receiver=receiver,
                    subject=subject,
                    body=body,
                    is_draft=False
                )
            return redirect("/messages/")

        if action == "draft":
            if not receiver_email and not subject and not body:
                return redirect("/messages/")

            receiver = User.objects.filter(email=receiver_email).first() if receiver_email else None

            if draft_id:
                draft = get_object_or_404(user_messages, id=draft_id, sender=request.user, is_draft=True)
                draft.receiver = receiver
                draft.subject = subject
                draft.body = body
                draft.is_draft = True
                draft.save()
            else:
                user_messages.objects.create(
                    sender=request.user,
                    receiver=receiver,
                    subject=subject,
                    body=body,
                    is_draft=True
                )
            return redirect("/messages/")

    return render(request, "MessagePage.html", {
        "inbox": inbox,
        "sent": sent,
        "drafts": drafts,
        "selected_message": selected_message,
        "mode": mode,
    })