"""
Messaging API - recruiter-candidate communication
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, func, desc
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.message import Message
from app.schemas.features import MessageCreate, MessageResponse, ConversationSummary
from app.core.socket_manager import manager
from typing import List

router = APIRouter()


@router.post("/", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
async def send_message(
    data: MessageCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Send a message to another user"""
    # Verify receiver exists
    receiver = db.query(User).filter(User.id == data.receiver_id).first()
    if not receiver:
        raise HTTPException(status_code=404, detail="Receiver not found")
    
    if data.receiver_id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot message yourself")
    
    # Permission check: Recruiters can message anyone. 
    # Job seekers can only message if they have a match OR if the recruiter started the conversation.
    if current_user.role == "job_seeker":
        # Check for existing conversation
        has_intro = db.query(Message).filter(
            Message.sender_id == data.receiver_id,
            Message.receiver_id == current_user.id
        ).first()
        
        # Check for a match if no intro exists
        has_match = False
        if not has_intro:
            # Need to check if there is ANY match between this candidate and any job of the recruiter
            from app.models.match import Match
            from app.models.job import Job
            from app.models.candidate import Candidate
            
            # Find the candidate record for the current user (based on email)
            candidate = db.query(Candidate).filter(Candidate.email == current_user.email).first()
            if candidate:
                # Check if there is a match between this candidate and the receiver recruiter
                has_match = db.query(Match).join(Job).filter(
                    Match.candidate_id == candidate.id,
                    Job.recruiter_id == data.receiver_id
                ).first() is not None

        if not has_intro and not has_match:
            raise HTTPException(
                status_code=403,
                detail="Candidates can only message recruiters after a match is made or the recruiter contacts you first."
            )
    
    message = Message(
        sender_id=current_user.id,
        receiver_id=data.receiver_id,
        content=data.content,
        match_id=data.match_id
    )
    db.add(message)
    db.commit()
    db.refresh(message)
    
    # Real-time update via WebSocket
    try:
        from loguru import logger
        await manager.send_json_to_user({
            "type": "new_message",
            "message": {
                "id": message.id,
                "sender_id": message.sender_id,
                "receiver_id": message.receiver_id,
                "match_id": message.match_id,
                "content": message.content,
                "is_read": message.is_read,
                "created_at": message.created_at.isoformat() + "Z",  # Explicit UTC
                "sender_name": current_user.full_name
            }
        }, data.receiver_id)
        # Also echo back to sender for multi-tab sync
        await manager.send_json_to_user({
            "type": "new_message",
            "message": {
                "id": message.id,
                "sender_id": message.sender_id,
                "receiver_id": message.receiver_id,
                "match_id": message.match_id,
                "content": message.content,
                "is_read": message.is_read,
                "created_at": message.created_at.isoformat() + "Z",
                "sender_name": current_user.full_name
            }
        }, current_user.id)
    except Exception as ws_err:
        logger.error(f"Failed to send real-time message update: {ws_err}")

    return MessageResponse(
        id=message.id,
        sender_id=message.sender_id,
        receiver_id=message.receiver_id,
        match_id=message.match_id,
        content=message.content,
        is_read=message.is_read,
        created_at=message.created_at,
        sender_name=current_user.full_name
    )


@router.get("/conversations", response_model=List[ConversationSummary])
async def list_conversations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all conversations for current user"""
    # Get all unique conversation partners
    sent = db.query(Message.receiver_id).filter(Message.sender_id == current_user.id).distinct().all()
    received = db.query(Message.sender_id).filter(Message.receiver_id == current_user.id).distinct().all()
    
    partner_ids = set([r[0] for r in sent] + [r[0] for r in received])
    
    conversations = []
    for partner_id in partner_ids:
        partner = db.query(User).filter(User.id == partner_id).first()
        if not partner:
            continue
        
        # Get last message
        last_msg = db.query(Message).filter(
            or_(
                and_(Message.sender_id == current_user.id, Message.receiver_id == partner_id),
                and_(Message.sender_id == partner_id, Message.receiver_id == current_user.id)
            )
        ).order_by(Message.created_at.desc()).first()
        
        # Count unread
        unread = db.query(Message).filter(
            Message.sender_id == partner_id,
            Message.receiver_id == current_user.id,
            Message.is_read == False
        ).count()
        
        if last_msg:
            conversations.append(ConversationSummary(
                other_user_id=partner_id,
                other_user_name=partner.full_name,
                last_message=last_msg.content[:100],
                last_message_at=last_msg.created_at,
                unread_count=unread
            ))
    
    # Sort by most recent
    conversations.sort(key=lambda c: c.last_message_at, reverse=True)
    return conversations


@router.get("/thread/{user_id}", response_model=List[MessageResponse])
async def get_thread(
    user_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get message thread with a specific user"""
    messages = db.query(Message).filter(
        or_(
            and_(Message.sender_id == current_user.id, Message.receiver_id == user_id),
            and_(Message.sender_id == user_id, Message.receiver_id == current_user.id)
        )
    ).order_by(Message.created_at.asc()).all()
    
    # Mark received messages as read
    unread = db.query(Message).filter(
        Message.sender_id == user_id,
        Message.receiver_id == current_user.id,
        Message.is_read == False
    ).all()
    for msg in unread:
        msg.is_read = True
    db.commit()
    
    results = []
    for msg in messages:
        sender = db.query(User).filter(User.id == msg.sender_id).first()
        # Ensure created_at is returned in ISO format with Z suffix
        # so the frontend treats it as UTC and converts to local time correctly
        results.append(MessageResponse(
            id=msg.id,
            sender_id=msg.sender_id,
            receiver_id=msg.receiver_id,
            match_id=msg.match_id,
            content=msg.content,
            is_read=msg.is_read,
            created_at=msg.created_at,
            sender_name=sender.full_name if sender else "Unknown"
        ))
    
    return results


@router.get("/unread-count")
async def get_unread_count(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get total unread message count"""
    count = db.query(Message).filter(
        Message.receiver_id == current_user.id,
        Message.is_read == False
    ).count()
    
    return {"unread_count": count}
