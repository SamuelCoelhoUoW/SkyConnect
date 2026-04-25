from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from .models import user_messages


@login_required
def messages_page(request):
    if request.method == "POST":
        if request.POST.get("delete_btn"):
            return delete_message(request)

        if request.POST.get("action"):
            return save_or_update_message(request)

        return redirect('/messages/')

    inbox = user_messages.objects.filter(receiver=request.user, is_draft=False)
    sent = user_messages.objects.filter(sender=request.user, is_draft=False)
    drafts = user_messages.objects.filter(sender=request.user, is_draft=True)

    message_id = request.GET.get("message_id")
    selected_message = None
    mode = "new"

    if message_id:
        try:
            selected_message = user_messages.objects.get(id=message_id)
            if selected_message.sender != request.user and selected_message.receiver != request.user:
                selected_message = None
            else:
                if selected_message.is_draft and selected_message.sender == request.user:
                    mode = "edit"
                else:
                    mode = "view"
        except user_messages.DoesNotExist:
            pass

    # -----------------------
    # HANDLE FORM SUBMIT
    # -----------------------
    if request.method == 'POST':

        draft_id = request.POST.get("draft_id")
        action = request.POST.get('action')
        receiver_email = request.POST.get('receiver_email')
        subject = request.POST.get('subject')
        body = request.POST.get('body')

        receiver = User.objects.filter(email=receiver_email).first()

        draft_id = request.POST.get('draft_id')

        # DELETE DRAFT
        if action == "delete" and draft_id:
            draft = user_messages.objects.filter(
                id=draft_id,
                sender=request.user,
                is_draft=True
            ).first()

            if draft:
                draft.delete()

            return redirect('/messages/')

        # -----------------------
        # SEND VALIDATION
        # -----------------------
        if action == "send":
            if not receiver_email or not receiver or not subject:
                return redirect('/messages/')

        # -----------------------
        # DRAFT VALIDATION
        # -----------------------
        if action == "draft":
            if not receiver_email and not subject and not body:
                # ALL EMPTY → block
                return redirect('/messages/')

        if draft_id:
            # UPDATE existing draft
            draft = get_object_or_404(user_messages, id=draft_id, sender=request.user)

            draft.receiver = receiver
            draft.subject = subject
            draft.body = body
            draft.is_draft = (action == "draft")

            draft.save()
        else:
            # CREATE new message
            user_messages.objects.create(
                sender=request.user,
                receiver=receiver,
                subject=subject,
                body=body,
                is_draft=(action == 'draft')
            )

        return redirect('/messages/')

    return render(request, 'MessagePage.html', {
        'inbox': inbox,
        'sent': sent,
        'drafts': drafts,
        'selected_message': selected_message,
        'mode': mode,
        'inbox_empty': not inbox.exists()  #  pass to template
    })

def delete_message(request):
    delete_id = request.POST.get("delete_id")

    if not delete_id:
        return redirect('/messages/')

    try:
        msg = user_messages.objects.get(id=delete_id, sender=request.user)
        msg.delete()
    except user_messages.DoesNotExist:
        pass

    return redirect('/messages/')


def save_or_update_message(request):
    message_id = request.POST.get("message_id")
    action = request.POST.get("action")

    subject = request.POST.get("subject")
    body = request.POST.get("body")
    receiver_email = request.POST.get("receiver_email")

    if request.POST.get("delete_btn"):
        return redirect('/messages/')

    if action not in ["send", "draft"]:
        return redirect('/messages/')

    if action == "send":
        if not subject or not receiver_email:
            return redirect('/messages/')

    receiver = None
    if receiver_email:
        receiver = User.objects.filter(email=receiver_email).first()
        if not receiver and action == "send":
            return redirect('/messages/')

    if message_id:
        try:
            msg = user_messages.objects.get(id=message_id, sender=request.user)
            msg.subject = subject
            msg.body = body
            msg.receiver = receiver
            if action == "send":
                msg.is_draft = False
            msg.save()
        except user_messages.DoesNotExist:
            pass
    else:
        user_messages.objects.create(
            sender=request.user,
            receiver=receiver,
            subject=subject,
            body=body,
            is_draft=(action == "draft")
        )

    return redirect('/messages/')
