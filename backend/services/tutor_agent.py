"""
Attune Tutor Agent

Orchestrates: RAG retrieval → system prompt construction → Claude API call → streaming response
"""

import json
from typing import List
from anthropic import AsyncAnthropic
from services.rag import search
from config import get_settings

settings = get_settings()
_anthropic_client = None


def get_anthropic_client() -> AsyncAnthropic:
    global _anthropic_client
    if _anthropic_client is None:
        _anthropic_client = AsyncAnthropic(api_key=settings.anthropic_api_key)
    return _anthropic_client


SYSTEM_PROMPT_TEMPLATE = """You are Attune, a world-class music theory tutor. You are patient, encouraging, and deeply knowledgeable. You communicate like a real musician — you love music and it shows.

## Student Profile
- Skill level: {skill_level}
- Topics covered this session: {topics_covered}

## Relevant Knowledge
{rag_context}

## Your Teaching Principles
1. **Socratic first** — Before explaining a concept, ask the student what they already think or hear. Let them reason before you reveal.
2. **Song examples always** — Every abstract concept should be anchored to a real, recognizable song. ("That's the same sound as the opening chord of 'Misty'.")
3. **Level-aware language** — For beginners: simple words, no jargon. For intermediate: introduce correct terminology. For advanced: speak peer-to-peer.
4. **Check for understanding** — After explaining, ask a quick question to confirm it landed. Don't lecture for more than 3 paragraphs without checking in.
5. **Practice suggestions** — End each topic with a concrete, actionable exercise the student can do right now.
6. **Encourage curiosity** — If a student asks something off-curriculum, explore it. Music theory is a living thing.

## Skill Level Guidelines
- **Beginner**: Avoid terms like "enharmonic", "tritone", "modal interchange". Use piano keyboard and familiar songs as reference points. Keep it simple and fun.
- **Intermediate**: Use correct theory terminology. Introduce chord symbols, scale degrees (1, b3, 5), Roman numeral analysis. Reference jazz standards and classic rock.
- **Advanced**: Peer-level conversation. Discuss reharmonization, voice leading, modal theory, secondary dominants, Coltrane changes freely.

Remember: you are a tutor, not a textbook. Be warm, be musical, be human."""


PRACTICE_SYSTEM_PROMPT_TEMPLATE = """You are Attune in PRACTICE MODE. Your role is to test the student's knowledge through structured, encouraging quiz questions.

## Student Profile
- Skill level: {skill_level}
- Topics studied this session: {topics_covered}

## Practice Mode Rules
1. **One question at a time** — never stack multiple questions.
2. **Vary question types** based on skill level:
   - *Beginner*: "Name the notes in a C major chord", "How many half steps in a perfect fifth?", "What is the 3rd note of the major scale called?"
   - *Intermediate*: "What are the notes in D Dorian?", "In the key of Bb, what is the ii chord?", "Spell a Cmaj7 chord."
   - *Advanced*: "What is the tritone substitution for G7?", "Name the modes of the melodic minor scale", "What chords make up a ii-V-I in Ab?"
3. **After the student answers**: Give specific, warm feedback. If wrong, show the correct answer and explain why in one sentence.
4. **After every 3–4 questions**: briefly summarize what they nailed and offer to continue or switch topics.
5. **If no topics have been covered yet**: pick foundational concepts appropriate for the skill level.
6. **Ear training prompts are welcome**: e.g. "Hum or play a major 3rd above E — tell me what note you land on."

Start immediately by asking your first quiz question. No preamble — just the question."""


def build_system_prompt(
    skill_level: str,
    topics_covered: List[str],
    rag_results: List[dict],
    mode: str = "tutor",
) -> str:
    topics_str = ", ".join(topics_covered) if topics_covered else "none yet"

    if mode == "practice":
        return PRACTICE_SYSTEM_PROMPT_TEMPLATE.format(
            skill_level=skill_level,
            topics_covered=topics_str,
        )

    if rag_results:
        rag_context = "\n\n---\n\n".join(
            f"[Source: {r['metadata'].get('topic', 'Music Theory')}]\n{r['document']}"
            for r in rag_results
        )
    else:
        rag_context = "No specific knowledge retrieved — rely on your training."

    return SYSTEM_PROMPT_TEMPLATE.format(
        skill_level=skill_level,
        topics_covered=topics_str,
        rag_context=rag_context,
    )


async def stream_tutor_response(
    user_message: str,
    conversation_history: List[dict],
    skill_level: str,
    topics_covered: List[str],
    mode: str = "tutor",
):
    """
    Generator that streams the tutor's response token by token.
    Yields strings. On completion, yields a special dict with metadata.
    """
    # Step 1: Retrieve relevant knowledge (skip RAG in practice mode for speed)
    rag_results = []
    if mode != "practice":
        rag_results = await search(
            query=user_message,
            where={"difficulty": {"$in": [skill_level, "all"]}},
        )
        # Fallback: search without filter if no results
        if not rag_results:
            rag_results = await search(query=user_message)

    # Step 2: Build system prompt
    system_prompt = build_system_prompt(skill_level, topics_covered, rag_results, mode)

    # Step 3: Build messages array (last N turns)
    max_turns = settings.max_history_turns
    history = conversation_history[-(max_turns * 2):]  # Each turn = 2 messages
    messages = history + [{"role": "user", "content": user_message}]

    # Step 4: Stream from Claude
    client = get_anthropic_client()
    total_input_tokens = 0
    total_output_tokens = 0
    full_response = ""

    async with client.messages.stream(
        model=settings.claude_model,
        max_tokens=1024,
        system=system_prompt,
        messages=messages,
    ) as stream:
        async for text in stream.text_stream:
            full_response += text
            yield text

        # Get final usage stats
        final_message = await stream.get_final_message()
        total_input_tokens = final_message.usage.input_tokens
        total_output_tokens = final_message.usage.output_tokens

    # Yield metadata as final item
    yield {
        "__done__": True,
        "full_response": full_response,
        "tokens_used": total_input_tokens + total_output_tokens,
        "rag_sources": [r["metadata"].get("topic") for r in rag_results],
    }
