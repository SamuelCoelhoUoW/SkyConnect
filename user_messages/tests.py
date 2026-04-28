# Author: Theoayman Haid De Azevedo
# Individual element - wrote the code and performed test

from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from .models import user_messages


class MessagesPageTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.sender = User.objects.create_user(
            username="sender",
            email="sender@test.com",
            password="pass12345"
        )
        cls.receiver = User.objects.create_user(
            username="receiver",
            email="receiver@test.com",
            password="pass12345"
        )
        cls.other = User.objects.create_user(
            username="other",
            email="other@test.com",
            password="pass12345"
        )

    def setUp(self):
        self.url = reverse("messages")

    def test_redirects_anonymous_user(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login/", response.url)

    def test_get_messages_page_logged_in(self):
        self.client.login(username="sender", password="pass12345")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "MessagePage.html")

    def test_inbox_sent_drafts_are_filtered(self):
        inbox_msg = user_messages.objects.create(
            sender=self.receiver,
            receiver=self.sender,
            subject="Inbox msg",
            body="hello",
            is_draft=False
        )
        sent_msg = user_messages.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            subject="Sent msg",
            body="sent body",
            is_draft=False
        )
        draft_msg = user_messages.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            subject="Draft msg",
            body="draft body",
            is_draft=True
        )
        user_messages.objects.create(
            sender=self.other,
            receiver=self.receiver,
            subject="Not mine",
            body="nope",
            is_draft=False
        )

        self.client.login(username="sender", password="pass12345")
        response = self.client.get(self.url)

        self.assertIn(inbox_msg, response.context["inbox"])
        self.assertIn(sent_msg, response.context["sent"])
        self.assertIn(draft_msg, response.context["drafts"])
        self.assertEqual(len(response.context["inbox"]), 1)
        self.assertEqual(len(response.context["sent"]), 1)
        self.assertEqual(len(response.context["drafts"]), 1)

    def test_send_message_creates_message(self):
        self.client.login(username="sender", password="pass12345")
        response = self.client.post(self.url, {
            "action": "send",
            "receiver_email": "receiver@test.com",
            "subject": "Hello",
            "body": "Message body",
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(user_messages.objects.count(), 1)

        msg = user_messages.objects.first()
        self.assertEqual(msg.sender, self.sender)
        self.assertEqual(msg.receiver, self.receiver)
        self.assertEqual(msg.subject, "Hello")
        self.assertEqual(msg.body, "Message body")
        self.assertFalse(msg.is_draft)

    def test_send_message_with_missing_receiver_does_not_create(self):
        self.client.login(username="sender", password="pass12345")
        response = self.client.post(self.url, {
            "action": "send",
            "receiver_email": "missing@test.com",
            "subject": "Hello",
            "body": "Body",
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(user_messages.objects.count(), 0)

    def test_save_draft_creates_draft(self):
        self.client.login(username="sender", password="pass12345")
        response = self.client.post(self.url, {
            "action": "draft",
            "receiver_email": "receiver@test.com",
            "subject": "Draft subject",
            "body": "Draft body",
        })
        self.assertEqual(response.status_code, 302)

        draft = user_messages.objects.get()
        self.assertTrue(draft.is_draft)
        self.assertEqual(draft.sender, self.sender)
        self.assertEqual(draft.receiver, self.receiver)
        self.assertEqual(draft.subject, "Draft subject")

    def test_empty_draft_is_not_created(self):
        self.client.login(username="sender", password="pass12345")
        response = self.client.post(self.url, {
            "action": "draft",
            "receiver_email": "",
            "subject": "",
            "body": "",
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(user_messages.objects.count(), 0)

    def test_delete_draft(self):
        draft = user_messages.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            subject="Delete me",
            body="draft body",
            is_draft=True
        )
        self.client.login(username="sender", password="pass12345")
        response = self.client.post(self.url, {
            "action": "delete",
            "draft_id": draft.id
        })
        self.assertEqual(response.status_code, 302)
        self.assertFalse(user_messages.objects.filter(id=draft.id).exists())

    def test_view_message_by_id(self):
        msg = user_messages.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            subject="View me",
            body="Secret",
            is_draft=False
        )
        self.client.login(username="sender", password="pass12345")
        response = self.client.get(self.url, {"message_id": msg.id})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["selected_message"], msg)
        self.assertEqual(response.context["mode"], "view")

    def test_view_draft_by_sender_sets_edit_mode(self):
        draft = user_messages.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            subject="Draft edit",
            body="Draft body",
            is_draft=True
        )
        self.client.login(username="sender", password="pass12345")
        response = self.client.get(self.url, {"message_id": draft.id})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["selected_message"], draft)
        self.assertEqual(response.context["mode"], "edit")
