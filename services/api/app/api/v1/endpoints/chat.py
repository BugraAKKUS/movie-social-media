from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.dependencies import get_current_user
from app.models.chat import ChatConversation, ChatMessage
from app.models.user import User

router = APIRouter()


class CreateConversationRequest(BaseModel):
    movie_id: str | None = None
    title: str | None = None


class PublishRequest(BaseModel):
    message_id: str
    movie_id: str


@router.post("/conversations")
async def create_conversation(
    body: CreateConversationRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    conversation = ChatConversation(
        user_id=current_user.id,
        movie_id=body.movie_id,
        title=body.title or "New Conversation",
    )
    db.add(conversation)
    await db.flush()
    return conversation


@router.get("/conversations")
async def list_conversations(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(ChatConversation)
        .where(ChatConversation.user_id == current_user.id)
        .order_by(ChatConversation.updated_at.desc())
    )
    return result.scalars().all()


@router.websocket("/ws/{conversation_id}")
async def chat_websocket(
    websocket: WebSocket,
    conversation_id: str,
):
    """
    WebSocket endpoint for real-time AI chat.

    TODO: Integrate multimodal RAG pipeline:
    1. Embed user query with sentence-transformer
    2. Search Qdrant collections (movies, reviews, chat history)
    3. Assemble context (~2000 tokens)
    4. Generate response with LLM
    5. Stream response tokens
    """
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_json()
            if data.get("type") == "message":
                content = data["content"]

                # TODO: RAG pipeline integration
                # For now, echo a placeholder response
                await websocket.send_json({
                    "type": "response",
                    "content": f"[AI Chat placeholder] You said: {content}",
                    "rag_sources": [],
                })
    except WebSocketDisconnect:
        pass


@router.post("/{conversation_id}/publish")
async def publish_to_feed(
    conversation_id: str,
    body: PublishRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Publish an AI chat message as a review to the Explore feed.

    1. Fetch the chat message
    2. Create a Review with published_from_chat=True
    3. Run spoiler detection on the content
    4. Return the created review
    """
    result = await db.execute(
        select(ChatMessage).where(
            ChatMessage.id == body.message_id,
            ChatMessage.conversation_id == conversation_id,
        )
    )
    message = result.scalar_one_or_none()
    if not message:
        from app.core.exceptions import NotFoundError
        raise NotFoundError("Chat message not found")

    from app.models.review import Review
    review = Review(
        user_id=current_user.id,
        movie_id=body.movie_id,
        content_text=message.content,
        published_from_chat=True,
        chat_message_id=message.id,
    )
    db.add(review)
    await db.flush()

    # Link the message to the published review
    message.published_review_id = review.id

    return review
