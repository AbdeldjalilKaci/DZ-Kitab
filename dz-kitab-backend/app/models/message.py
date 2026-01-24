# app/models/message.py

from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum

class MessageStatus(enum.Enum):
    SENT = "sent"
    READ = "read"
    ARCHIVED = "archived"

class Conversation(Base):
    """Table pour gérer les conversations entre utilisateurs"""
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    announcement_id = Column(Integer, ForeignKey("announcements.id", ondelete="SET NULL"), nullable=True)
    buyer_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    seller_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    last_message = Column(Text, nullable=True)
    last_message_at = Column(DateTime(timezone=True), server_default=func.now())
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relations
    announcement = relationship("Announcement", lazy="select")
    buyer = relationship("User", foreign_keys=[buyer_id], lazy="select")
    seller = relationship("User", foreign_keys=[seller_id], lazy="select")
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan", lazy="select")
    
    def __repr__(self):
        return f"<Conversation(id={self.id}, buyer={self.buyer_id}, seller={self.seller_id})>"

class Message(Base):
    """Table pour stocker les messages individuels"""
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False, index=True)
    sender_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    receiver_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    content = Column(Text, nullable=False)
    status = Column(Enum(MessageStatus), default=MessageStatus.SENT, index=True)
    
    is_read = Column(Boolean, default=False, index=True)
    read_at = Column(DateTime(timezone=True), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    # Relations
    conversation = relationship("Conversation", back_populates="messages", lazy="select")
    sender = relationship("User", foreign_keys=[sender_id], lazy="select")
    receiver = relationship("User", foreign_keys=[receiver_id], lazy="select")
    
    def mark_as_read(self):
        """Marquer le message comme lu"""
        if not self.is_read:
            self.is_read = True
            self.read_at = func.now()
            self.status = MessageStatus.READ
    
    def __repr__(self):
        return f"<Message(id={self.id}, sender={self.sender_id}, receiver={self.receiver_id})>"
