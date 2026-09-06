"""Delivery layer — TDD §4.7.

"Whitelist-enforced: delivery only ever goes to active, opted-in recipients
the Owner has approved. Enforcement happens at the delivery layer, not the
caller." This module is that enforcement point: nothing upstream (brief
generator, alert engine) can send around it, because they don't hold an
EmailProvider/SmsProvider directly — they go through DeliveryService.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

from app.interfaces import EmailProvider, SmsProvider
from app.models import DeliveryChannel, DeliveryStatus, Recipient


@dataclass
class DeliveryResult:
    recipient_id: int
    channel: str
    status: str
    sent_at: datetime
    error: str | None = None


class DeliveryService:
    def __init__(self, email_provider: EmailProvider, sms_provider: SmsProvider):
        self._email = email_provider
        self._sms = sms_provider

    def deliver(
        self,
        recipient: Recipient,
        channel: DeliveryChannel,
        subject: str,
        body: str,
    ) -> DeliveryResult:
        now = datetime.now(timezone.utc)

        if not recipient.active or channel.value not in (recipient.channels or []):
            return DeliveryResult(
                recipient_id=recipient.id,
                channel=channel.value,
                status=DeliveryStatus.SUPPRESSED.value,
                sent_at=now,
                error="recipient not active or not opted into this channel",
            )

        if channel is DeliveryChannel.EMAIL:
            if not recipient.email:
                return DeliveryResult(
                    recipient_id=recipient.id,
                    channel=channel.value,
                    status=DeliveryStatus.FAILED.value,
                    sent_at=now,
                    error="no email address on file",
                )
            ok = self._email.send(recipient.email, subject, body)
        elif channel is DeliveryChannel.SMS:
            if not recipient.phone:
                return DeliveryResult(
                    recipient_id=recipient.id,
                    channel=channel.value,
                    status=DeliveryStatus.FAILED.value,
                    sent_at=now,
                    error="no phone number on file",
                )
            ok = self._sms.send(recipient.phone, body)
        else:
            raise ValueError(f"unknown channel: {channel}")

        return DeliveryResult(
            recipient_id=recipient.id,
            channel=channel.value,
            status=DeliveryStatus.SENT.value if ok else DeliveryStatus.FAILED.value,
            sent_at=now,
        )
