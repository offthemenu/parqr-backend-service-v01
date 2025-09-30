from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from app.db.base import Base
from datetime import datetime, timezone
import base64
import secrets

class ChatMessage(Base):
    __tablename__ = 'chat_messages'

    id = Column(Integer, primary_key=True, index=True)
    sender_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    recipient_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)

    # Message content - encrypted for privacy
    message_content = Column(Text, nullable=False)  # Encrypted content
    message_type = Column(String(50), default='text', nullable=False)  # 'text', 'move_car_request'

    # Encryption key reference (simple approach for MVP)
    encryption_key = Column(String(100), nullable=False)

    # Metadata
    is_read = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    read_at = Column(DateTime, nullable=True)

    # Relationships
    sender = relationship("User", foreign_keys=[sender_id], backref="sent_messages")
    recipient = relationship("User", foreign_keys=[recipient_id], backref="received_messages")

    @staticmethod
    def simple_encrypt(message: str) -> tuple[str, str]:
        """
        Simple encryption for MVP - generates key and encrypts message
        Returns: (encrypted_message, encryption_key)
        """
        # Generate a simple key (for MVP - use proper encryption in production)
        key = secrets.token_urlsafe(32)

        # Simple base64 encoding with key offset (MVP approach)
        message_bytes = message.encode('utf-8')
        key_bytes = key.encode('utf-8')[:len(message_bytes)]

        # XOR encryption (simple for MVP)
        encrypted_bytes = bytes(a ^ b for a, b in zip(message_bytes, key_bytes))
        encrypted_message = base64.b64encode(encrypted_bytes).decode('utf-8')

        return encrypted_message, key

    @staticmethod
    def simple_decrypt(encrypted_message: str, encryption_key: str) -> str:
        """
        Simple decryption for MVP
        """
        try:
            # Decode the encrypted message
            encrypted_bytes = base64.b64decode(encrypted_message.encode('utf-8'))
            key_bytes = encryption_key.encode('utf-8')[:len(encrypted_bytes)]

            # XOR decryption
            decrypted_bytes = bytes(a ^ b for a, b in zip(encrypted_bytes, key_bytes))
            return decrypted_bytes.decode('utf-8')
        except Exception:
            return "[Message could not be decrypted]"

