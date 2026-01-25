# app/routers/messages.py

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.database import get_db
from app.models.message import Message, Conversation, MessageStatus
from app.models.user import User
from app.models.book import Announcement, Book
from app.models.notification import Notification, NotificationType
from app.schemas.message import (
    MessageCreate,
    MessageResponse,
    ConversationResponse,
    ConversationWithMessagesResponse,
    ConversationListResponse,
    ContactSellerRequest
)
from app.middleware.auth import security
from app.services.jwt import verify_token
from app.services.email import send_email

router = APIRouter()

def get_current_user_id(token: str = Depends(security), db: Session = Depends(get_db)) -> int:
    """Obtenir l'ID de l'utilisateur actuel"""
    payload = verify_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalide"
        )
    
    email = payload.get("sub")
    user = db.query(User).filter(User.email == email).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Utilisateur non trouv"
        )
    
    return user.id

# ============================================
# CONTACT SELLER (Formulaire de contact)
# ============================================

@router.post("/contact-seller", status_code=status.HTTP_201_CREATED)
def contact_seller(
    contact_data: ContactSellerRequest,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """
    Contacter un vendeur via le formulaire de contact
    
    - Cree une conversation si elle n'existe pas
    - Envoie le premier message
    - Notifie le vendeur par email (optionnel)
    """
    try:
        print(f"Contact seller started: ann_id={contact_data.announcement_id}, buyer_id={user_id}")
        # 1. Vrifier l'annonce
        announcement = db.query(Announcement).filter(
            Announcement.id == contact_data.announcement_id
        ).first()
        
        if not announcement:
            print(f"Error: Announcement {contact_data.announcement_id} not found")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Annonce non trouve"
            )
        
        seller_id = announcement.user_id
        print(f"Seller found: {seller_id}")
        
        # 2. Empcher de se contacter soi-mme
        if user_id == seller_id:
            print(f"Error: User {user_id} tried to contact own announcement")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Vous ne pouvez pas contacter votre propre annonce"
            )
        
        # 3. Chercher ou crer la conversation
        print("Checking for existing conversation...")
        conversation = db.query(Conversation).filter(
            Conversation.announcement_id == contact_data.announcement_id,
            Conversation.buyer_id == user_id,
            Conversation.seller_id == seller_id
        ).first()
        
        if not conversation:
            print("Creating new conversation...")
            conversation = Conversation(
                announcement_id=contact_data.announcement_id,
                buyer_id=user_id,
                seller_id=seller_id
            )
            db.add(conversation)
            db.flush()
        
        print(f"Conversation ID: {conversation.id}")

        # 4. Crer le message (inclure les coordonnes de l'acheteur)
        full_content = contact_data.message
        if contact_data.address or contact_data.phone:
            full_content += "\n\n--- Coordonnes de contact ---"
            if contact_data.address:
                full_content += f"\nAdresse: {contact_data.address}"
            if contact_data.phone:
                full_content += f"\nTlphone: {contact_data.phone}"

        print("Creating message object...")
        message = Message(
            conversation_id=conversation.id,
            sender_id=user_id,
            receiver_id=seller_id,
            content=full_content
        )
        
        db.add(message)
        
        # 5. Mettre  jour la conversation
        conversation.last_message = contact_data.message[:100]
        conversation.last_message_at = datetime.utcnow()
        
        print("Commiting to database...")
        db.commit()
        db.refresh(message)
        print(f"Message created: {message.id}")
        
        # 6. Envoyer notification email au vendeur (Robust version)
        try:
            print("Preparing email notification...")
            seller = db.query(User).filter(User.id == seller_id).first()
            buyer = db.query(User).filter(User.id == user_id).first()
            
            # Use announcement.book relationship instead of extra query if possible
            book_title = "Livre"
            if announcement.book:
                book_title = announcement.book.title

            if seller and buyer:
                # 6a. Create in-app notification
                notification = Notification(
                    user_id=seller_id,
                    type=NotificationType.MESSAGE_RECEIVED,
                    title="Nouveau message",
                    message=f"{buyer.username} vous a envoye un message concernant '{book_title}'",
                    related_user_id=user_id,
                    related_announcement_id=contact_data.announcement_id,
                    action_url=f"/message?conversationId={conversation.id}"
                )
                db.add(notification)
                # Single commit for everything
                db.commit()

                email_subject = f"Nouveau message concernant '{book_title}'"
                email_html = f"""
                <h2>Nouveau message reu</h2>
                <p><strong>{buyer.username}</strong> vous a envoy un message concernant votre annonce:</p>
                <h3>{book_title}</h3>
                <p><strong>Message:</strong></p>
                <blockquote>{contact_data.message}</blockquote>
                <p>Connectez-vous  DZ-Kitab pour rpondre.</p>
                """
                
                print(f"Sending email to {seller.email}...")
                send_email(seller.email, email_subject, email_html)
                print("Email attempt finished")
        except Exception as e:
            print(f"Non-fatal error in email notification: {e}")
        
        return {
            "success": True,
            "message": "Message envoy avec succs",
            "conversation_id": conversation.id,
            "message_id": message.id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Erreur contact vendeur: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de l'envoi du message"
        )

# ============================================
# CONVERSATIONS
# ============================================

@router.get("/conversations", response_model=ConversationListResponse)
def get_my_conversations(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """
     Obtenir toutes les conversations de l'utilisateur
    """
    try:
        # Rcuprer les conversations o l'utilisateur est buyer ou seller
        query = db.query(Conversation).filter(
            (Conversation.buyer_id == user_id) | (Conversation.seller_id == user_id),
            Conversation.is_active == True
        )
        
        total = query.count()
        conversations = query.order_by(
            Conversation.last_message_at.desc()
        ).offset(skip).limit(limit).all()
        
        # Compter les messages non lus
        unread_total = db.query(Message).filter(
            Message.receiver_id == user_id,
            Message.is_read == False
        ).count()
        
        # Formater les rponses
        formatted_conversations = []
        for conv in conversations:
            # Dterminer l'autre utilisateur
            other_user_id = conv.seller_id if conv.buyer_id == user_id else conv.buyer_id
            other_user = db.query(User).filter(User.id == other_user_id).first()
            
            # Rcuprer l'annonce
            announcement = None
            announcement_title = None
            announcement_cover = None
            
            if conv.announcement_id:
                announcement = db.query(Announcement).filter(
                    Announcement.id == conv.announcement_id
                ).first()
                if announcement:
                    book = db.query(Book).filter(Book.id == announcement.book_id).first()
                    announcement_title = book.title if book else "Livre"
                    announcement_cover = book.cover_image_url if book else None
            
            # Compter messages non lus dans cette conversation
            unread_count = db.query(Message).filter(
                Message.conversation_id == conv.id,
                Message.receiver_id == user_id,
                Message.is_read == False
            ).count()
            
            formatted_conversations.append(ConversationResponse(
                id=conv.id,
                announcement_id=conv.announcement_id,
                buyer_id=conv.buyer_id,
                seller_id=conv.seller_id,
                last_message=conv.last_message,
                last_message_at=conv.last_message_at,
                is_active=conv.is_active,
                created_at=conv.created_at,
                other_user_id=other_user_id,
                other_user_username=other_user.username if other_user else "Utilisateur",
                other_user_email=other_user.email if other_user else "",
                announcement_title=announcement_title,
                announcement_cover=announcement_cover,
                unread_count=unread_count
            ))
        
        return ConversationListResponse(
            total=total,
            unread_total=unread_total,
            conversations=formatted_conversations
        )
        
    except Exception as e:
        print(f" Erreur rcupration conversations: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la rcupration des conversations"
        )

@router.get("/conversations/{conversation_id}", response_model=ConversationWithMessagesResponse)
def get_conversation(
    conversation_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """
     Obtenir une conversation avec tous ses messages
    """
    try:
        conversation = db.query(Conversation).filter(
            Conversation.id == conversation_id
        ).first()
        
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation non trouve"
            )
        
        # Vrifier que l'utilisateur fait partie de la conversation
        if user_id not in [conversation.buyer_id, conversation.seller_id]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Accs non autoris  cette conversation"
            )
        
        # Rcuprer les messages
        messages = db.query(Message).filter(
            Message.conversation_id == conversation_id
        ).order_by(Message.created_at.asc()).all()
        
        # Marquer les messages reus comme lus
        for message in messages:
            if message.receiver_id == user_id and not message.is_read:
                message.mark_as_read()
        
        db.commit()
        
        # Dterminer l'autre utilisateur
        other_user_id = conversation.seller_id if conversation.buyer_id == user_id else conversation.buyer_id
        other_user = db.query(User).filter(User.id == other_user_id).first()
        
        # Informations sur l'annonce
        announcement_title = None
        announcement_cover = None
        
        if conversation.announcement_id:
            announcement = db.query(Announcement).filter(
                Announcement.id == conversation.announcement_id
            ).first()
            if announcement:
                book = db.query(Book).filter(Book.id == announcement.book_id).first()
                announcement_title = book.title if book else "Livre"
                announcement_cover = book.cover_image_url if book else None
        
        # Formater les messages
        formatted_messages = []
        for msg in messages:
            sender = db.query(User).filter(User.id == msg.sender_id).first()
            receiver = db.query(User).filter(User.id == msg.receiver_id).first()
            
            formatted_messages.append(MessageResponse(
                id=msg.id,
                conversation_id=msg.conversation_id,
                sender_id=msg.sender_id,
                receiver_id=msg.receiver_id,
                content=msg.content,
                status=msg.status.value,
                is_read=msg.is_read,
                read_at=msg.read_at,
                created_at=msg.created_at,
                sender_username=sender.username if sender else "Utilisateur",
                receiver_username=receiver.username if receiver else "Utilisateur"
            ))
        
        return ConversationWithMessagesResponse(
            id=conversation.id,
            announcement_id=conversation.announcement_id,
            buyer_id=conversation.buyer_id,
            seller_id=conversation.seller_id,
            last_message=conversation.last_message,
            last_message_at=conversation.last_message_at,
            is_active=conversation.is_active,
            created_at=conversation.created_at,
            other_user_id=other_user_id,
            other_user_username=other_user.username if other_user else "Utilisateur",
            other_user_email=other_user.email if other_user else "",
            announcement_title=announcement_title,
            announcement_cover=announcement_cover,
            unread_count=0,
            messages=formatted_messages
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f" Erreur rcupration conversation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la rcupration de la conversation"
        )

# ============================================
# MESSAGES
# ============================================

@router.post("/conversations/{conversation_id}/messages", response_model=MessageResponse)
def send_message(
    conversation_id: int,
    content: str = Query(..., min_length=1, max_length=2000),
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """
     Envoyer un message dans une conversation
    """
    try:
        print(f"send_message started: conv_id={conversation_id}, user_id={user_id}")
        conversation = db.query(Conversation).filter(
            Conversation.id == conversation_id
        ).first()
        
        if not conversation:
            print(f"Error: Conversation {conversation_id} not found")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation non trouve"
            )
        
        # Vrifier que l'utilisateur fait partie de la conversation
        if user_id not in [conversation.buyer_id, conversation.seller_id]:
            print(f"Error: User {user_id} not in conversation {conversation_id}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Accs non autoris"
            )
        
        # Dterminer le destinataire
        receiver_id = conversation.seller_id if user_id == conversation.buyer_id else conversation.buyer_id
        print(f"Receiver determined: {receiver_id}")
        
        # Crer le message
        print("Creating message object...")
        message = Message(
            conversation_id=conversation_id,
            sender_id=user_id,
            receiver_id=receiver_id,
            content=content
        )
        
        db.add(message)
        
        # Mettre  jour la conversation
        conversation.last_message = content[:100]
        conversation.last_message_at = datetime.utcnow()
        
        print("Fetching users for notification...")
        sender = db.query(User).filter(User.id == user_id).first()
        receiver = db.query(User).filter(User.id == receiver_id).first()
        
        if sender and receiver:
            # Create in-app notification
            notification = Notification(
                user_id=receiver_id,
                type=NotificationType.MESSAGE_RECEIVED,
                title="Nouveau message",
                message=f"{sender.username} vous a envoye un message",
                related_user_id=user_id,
                action_url=f"/message?conversationId={conversation_id}"
            )
            db.add(notification)

        print("Commiting message and notification to database...")
        db.commit()
        db.refresh(message)
        print(f"Message and notification sent: {message.id}")

        return MessageResponse(
            id=message.id,
            conversation_id=message.conversation_id,
            sender_id=message.sender_id,
            receiver_id=message.receiver_id,
            content=message.content,
            status=message.status.value if hasattr(message.status, 'value') else str(message.status),
            is_read=message.is_read,
            read_at=message.read_at,
            created_at=message.created_at,
            sender_username=sender.username if sender else "Utilisateur",
            receiver_username=receiver.username if receiver else "Utilisateur"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Erreur envoi message: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur backend message: {str(e)}"
        )

@router.get("/test")
def test_messages():
    """Test endpoint"""
    return {
        "message": "Messages router is working!",
        "endpoints": [
            "POST /messages/contact-seller",
            "GET /messages/conversations",
            "GET /messages/conversations/{id}",
            "POST /messages/conversations/{id}/messages"
        ]
    }
