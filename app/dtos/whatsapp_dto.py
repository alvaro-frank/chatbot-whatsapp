# ==============================================================================
# FILE: app/dtos/whatsapp_dto.py
# DESCRIPTION: Data Transfer Object for WhatsApp incoming messages.
# ==============================================================================

from dataclasses import dataclass

@dataclass(frozen=True)
class IncomingMessageDTO:
    wa_id: str
    sender_name: str
    message_body: str

    @property
    def first_name(self) -> str:
        return self.sender_name.split()[0] if self.sender_name else ""