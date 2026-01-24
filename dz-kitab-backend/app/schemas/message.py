# app/schemas/message.py

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class MessageCreate(BaseModel):
    """Schéma pour créer un nouveau message"""
    announcement_id: int = Field(..., description="ID de l'annonce concernée")
    receiver_id: int = Field(..., description="ID du destinataire")
    content: str = Field(..., min_length=1, max_length=2000, description="Contenu du message")

class ContactSellerRequest(BaseModel):
    """Schéma pour le formulaire de contact vendeur"""
    announcement_id: int
    title: str = Field(..., description="Titre du livre (automatique)")
    email: str = Field(..., description="Email de l'acheteur (automatique)")
    address: Optional[str] = Field(None, max_length=200, description="Adresse de l'acheteur")
    phone: Optional[str] = Field(None, max_length=20, description="Téléphone de l'acheteur")
    message: str = Field(..., min_length=10, max_length=2000, description="Message à envoyer")

class MessageResponse(BaseModel):
    """Schéma de réponse pour un message"""
    id: int
    conversation_id: int
    sender_id: int
    receiver_id: int
    content: str
    status: str
    is_read: bool
    read_at: Optional[datetime] = None
    created_at: datetime
    sender_username: str
    receiver_username: str

    class Config:
        from_attributes = True

class ConversationResponse(BaseModel):
    """Schéma de réponse pour une conversation"""
    id: int
    announcement_id: Optional[int] = None
    buyer_id: int
    seller_id: int
    last_message: Optional[str] = None
    last_message_at: Optional[datetime] = None
    is_active: bool
    created_at: datetime
    
    # Informations sur l'autre utilisateur
    other_user_id: int
    other_user_username: str
    other_user_email: str
    
    # Informations sur l'annonce
    announcement_title: Optional[str] = None
    announcement_cover: Optional[str] = None
    
    # Compteur de messages non lus
    unread_count: int = 0

    class Config:
        from_attributes = True

class ConversationWithMessagesResponse(ConversationResponse):
    """Conversation avec ses messages"""
    messages: List[MessageResponse] = []

class ConversationListResponse(BaseModel):
    """Liste de conversations"""
    total: int
    unread_total: int
    conversations: List[ConversationResponse]
