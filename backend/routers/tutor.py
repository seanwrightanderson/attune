import json
import uuid
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel

from database import get_db
from models import User, Session as TutorSession, Message, MessageRole, SkillLevel
from services.tutor_agent import stream_tutor_response

router = APIRouter(prefix="/tutor", tags=["tutor"])


# ── Topic Detection ───────────────────────────────────────────────────────────

TOPIC_KEYWORDS: dict = {
    "Intervals": ["interval", "half step", "whole step", "semitone", "unison", "octave",
                  "third", "fifth", "fourth", "second", "sixth", "seventh", "tritone"],
    "Scales & Modes": ["scale", "mode", "dorian", "mixolydian", "phrygian", "lydian",
                       "locrian", "aeolian", "pentatonic", "blues scale", "major scale",
                       "minor scale", "chromatic", "whole tone"],
    "Chords": ["chord", "triad", "seventh", "diminished", "augmented", "major chord",
               "minor chord", "suspended", "sus2", "sus4", "power chord", "voicing"],
    "Harmony": ["harmony", "harmonic", "voice leading", "tension", "resolution",
                "progression", "diatonic", "borrowed chord", "modal interchange",
                "secondary dominant"],
    "ii-V-I": ["ii-v-i", "ii v i", "two five one", "two-five-one", "iim7", "dominant seventh"],
    "Jazz Theory": ["jazz", "bebop", "swing", "tritone substitution", "reharmonization",
                    "coltrane", "altered scale", "lydian dominant", "chord substitution"],
    "Blues": ["blues", "12-bar", "twelve bar", "shuffle", "bent note", "blue note",
              "turnaround", "call and response"],
    "Song Examples": ["song", "artist", "album", "for example", "like in", "similar to",
                      "listen to", "check out", "reminds me"],
}


def detect_topics(text: str, existing: List[str]) -> List[str]:
    """Detect which theory topics appear in a block of text."""
    lower = text.lower()
    found = set(existing)
    for topic, keywords in TOPIC_KEYWORDS.items():
        if any(kw in lower for kw in keywords):
            found.add(topic)
    return list(found)


# ── Schemas ──────────────────────────────────────────────────────────────────

class StartSessionRequest(BaseModel):
    skill_level: SkillLevel = SkillLevel.beginner
    user_id: Optional[str] = None  # Optional: link to existing user


class StartSessionResponse(BaseModel):
    session_id: str
    skill_level: str
    message: str


class ChatRequest(BaseModel):
    session_id: str
    message: str
    mode: str = "tutor"   # "tutor" | "practice"


class SessionSummaryResponse(BaseModel):
    session_id: str
    skill_level: str
    topics_covered: List[str]
    message_count: int


class ExportMessage(BaseModel):
    role: str
    content: str


class SessionExportResponse(BaseModel):
    session_id: str
    skill_level: str
    topics_covered: List[str]
    message_count: int
    messages: List[ExportMessage]


# ── Helpers ───────────────────────────────────────────────────────────────────

async def get_or_create_user(user_id: Optional[str], db: AsyncSession) -> User:
    if user_id:
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if user:
            return user
    user = User(id=str(uuid.uuid4()))
    db.add(user)
    await db.flush()
    return user


async def get_session_or_404(session_id: str, db: AsyncSession) -> TutorSession:
    result = await db.execute(
        select(TutorSession).where(TutorSession.id == session_id)
    )
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session


# ── Routes ────────────────────────────────────────────────────────────────────

@router.post("/session/start", response_model=StartSessionResponse)
async def start_session(
    body: StartSessionRequest,
    db: AsyncSession = Depends(get_db),
):
    """Create a new tutor session. Returns a session_id for all subsequent calls."""
    user = await get_or_create_user(body.user_id, db)

    session = TutorSession(
        id=str(uuid.uuid4()),
        user_id=user.id,
        skill_level=body.skill_level,
        topics_covered="[]",
    )
    db.add(session)
    await db.commit()

    level_intros = {
        SkillLevel.beginner: "Welcome to Attune! I'm here to help you understand music theory in a way that actually makes sense. We'll take it step by step and use real songs along the way. What would you like to explore first?",
        SkillLevel.intermediate: "Welcome back to theory! You've got the basics down — let's dig deeper. What are you working on or curious about?",
        SkillLevel.advanced: "Hey! Ready to nerd out on some theory? What's on your mind — reharmonization, modal stuff, voice leading?",
    }

    return StartSessionResponse(
        session_id=session.id,
        skill_level=session.skill_level.value,
        message=level_intros[body.skill_level],
    )


@router.post("/chat")
async def chat(
    body: ChatRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Send a message and stream back the tutor's response.
    Uses Server-Sent Events (SSE) for streaming.
    Supports mode: "tutor" (default) or "practice" (quiz mode).
    """
    session = await get_session_or_404(body.session_id, db)

    # Load conversation history
    result = await db.execute(
        select(Message)
        .where(Message.session_id == session.id)
        .order_by(Message.created_at)
    )
    db_messages = result.scalars().all()
    history = [{"role": m.role.value, "content": m.content} for m in db_messages]

    # Parse topics covered
    try:
        topics_covered = json.loads(session.topics_covered)
    except Exception:
        topics_covered = []

    # Save user message
    user_msg = Message(
        session_id=session.id,
        role=MessageRole.user,
        content=body.message,
    )
    db.add(user_msg)
    await db.flush()

    async def event_stream():
        full_response = ""
        tokens_used = 0

        async for chunk in stream_tutor_response(
            user_message=body.message,
            conversation_history=history,
            skill_level=session.skill_level.value,
            topics_covered=topics_covered,
            mode=body.mode,
        ):
            if isinstance(chunk, dict) and chunk.get("__done__"):
                full_response = chunk["full_response"]
                tokens_used = chunk["tokens_used"]

                # Detect new topics from the combined exchange
                combined_text = body.message + " " + full_response
                updated_topics = detect_topics(combined_text, topics_covered)

                # Save assistant message to DB
                assistant_msg = Message(
                    session_id=session.id,
                    role=MessageRole.assistant,
                    content=full_response,
                    tokens_used=tokens_used,
                )
                db.add(assistant_msg)

                # Update topics on session
                session.topics_covered = json.dumps(updated_topics)
                await db.commit()

                # Send done event with updated topics
                yield f"data: {json.dumps({'done': True, 'topics_covered': updated_topics})}\n\n"
            else:
                # Stream text chunk to client
                yield f"data: {json.dumps({'text': chunk})}\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


@router.get("/session/{session_id}/messages")
async def get_session_messages(
    session_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Fetch all messages for a session — used to rehydrate chat on page load."""
    session = await get_session_or_404(session_id, db)

    result = await db.execute(
        select(Message)
        .where(Message.session_id == session_id)
        .order_by(Message.created_at)
    )
    messages = result.scalars().all()

    try:
        topics_covered = json.loads(session.topics_covered)
    except Exception:
        topics_covered = []

    return {
        "session_id": session_id,
        "skill_level": session.skill_level.value,
        "topics_covered": topics_covered,
        "messages": [{"role": m.role.value, "content": m.content} for m in messages],
    }


@router.get("/session/{session_id}/summary", response_model=SessionSummaryResponse)
async def get_session_summary(
    session_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get a summary of what was covered in a session."""
    session = await get_session_or_404(session_id, db)

    result = await db.execute(
        select(Message).where(Message.session_id == session_id)
    )
    messages = result.scalars().all()

    try:
        topics = json.loads(session.topics_covered)
    except Exception:
        topics = []

    return SessionSummaryResponse(
        session_id=session_id,
        skill_level=session.skill_level.value,
        topics_covered=topics,
        message_count=len(messages),
    )


@router.get("/session/{session_id}/export", response_model=SessionExportResponse)
async def export_session(
    session_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Export full session data for download."""
    session = await get_session_or_404(session_id, db)

    result = await db.execute(
        select(Message)
        .where(Message.session_id == session_id)
        .order_by(Message.created_at)
    )
    messages = result.scalars().all()

    try:
        topics = json.loads(session.topics_covered)
    except Exception:
        topics = []

    return SessionExportResponse(
        session_id=session_id,
        skill_level=session.skill_level.value,
        topics_covered=topics,
        message_count=len(messages),
        messages=[ExportMessage(role=m.role.value, content=m.content) for m in messages],
    )
