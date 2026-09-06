"""Whitelist enforcement — TDD §4.7: 'delivery only ever goes to active,
opted-in recipients... enforcement happens at the delivery layer, not the
caller.' These tests are the proof that the enforcement can't be skipped by
an upstream caller forgetting to check."""

from app.delivery import DeliveryService
from app.fakes import FakeEmailProvider, FakeSmsProvider
from app.models import DeliveryChannel, DeliveryStatus, Recipient


def _service():
    return DeliveryService(FakeEmailProvider(), FakeSmsProvider())


def test_inactive_recipient_never_receives_delivery():
    recipient = Recipient(id=1, name="Inactive", email="x@example.com", channels=["email"], active=False)
    service = _service()

    result = service.deliver(recipient, DeliveryChannel.EMAIL, "subj", "body")

    assert result.status == DeliveryStatus.SUPPRESSED.value
    assert service._email.sent == []  # nothing reached the provider


def test_recipient_not_opted_into_channel_is_suppressed():
    recipient = Recipient(id=2, name="EmailOnly", email="x@example.com", channels=["email"], active=True)
    service = _service()

    result = service.deliver(recipient, DeliveryChannel.SMS, "subj", "body")

    assert result.status == DeliveryStatus.SUPPRESSED.value
    assert service._sms.sent == []


def test_active_opted_in_recipient_receives_delivery():
    recipient = Recipient(
        id=3, name="Active", email="x@example.com", phone="+15551234567",
        channels=["email", "sms"], active=True,
    )
    service = _service()

    email_result = service.deliver(recipient, DeliveryChannel.EMAIL, "subj", "body")
    sms_result = service.deliver(recipient, DeliveryChannel.SMS, "subj", "body")

    assert email_result.status == DeliveryStatus.SENT.value
    assert sms_result.status == DeliveryStatus.SENT.value
    assert service._email.sent == [("x@example.com", "subj", "body")]
    assert service._sms.sent == [("+15551234567", "body")]


def test_missing_contact_info_fails_rather_than_suppresses():
    recipient = Recipient(id=4, name="NoPhone", email="x@example.com", channels=["email", "sms"], active=True)
    service = _service()

    result = service.deliver(recipient, DeliveryChannel.SMS, "subj", "body")

    assert result.status == DeliveryStatus.FAILED.value
    assert result.error == "no phone number on file"
