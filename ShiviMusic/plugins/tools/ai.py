import os

from openai import AsyncOpenAI
from pyrogram import filters
from pyrogram.types import Message

from ShiviMusic import app


OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-6-luna")

client = AsyncOpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None


@app.on_message(filters.command("ai", prefixes=["/", "!", ".", "?"]))
async def ai_command(_, message: Message):
    if not client:
        await message.reply_text(
            "❌ OpenAI API key is not configured.\n"
            "Please add OPENAI_API_KEY in Render Environment."
        )
        return

    if len(message.command) < 2:
        await message.reply_text(
            "🤖 AI Assistant\n\n"
            "Use:\n"
            "/ai your question\n\n"
            "Example:\n"
            "/ai भारत का संविधान कब लागू हुआ?"
        )
        return

    question = message.text.split(maxsplit=1)[1].strip()

    if not question:
        await message.reply_text("❌ Please enter your question.")
        return

    try:
        status = await message.reply_text("🤖 Thinking...")

        response = await client.responses.create(
            model=OPENAI_MODEL,
            instructions=(
                "You are a helpful AI assistant inside a Telegram music bot. "
                "Answer clearly and concisely. "
                "You can understand and respond in Hindi, Hinglish, and English."
            ),
            input=question,
        )

        answer = response.output_text.strip()

        if not answer:
            answer = "❌ AI could not generate a response."

        # Telegram message limit handling
        chunks = [
            answer[i:i + 4000]
            for i in range(0, len(answer), 4000)
        ]

        await status.delete()

        for chunk in chunks:
            await message.reply_text(chunk)

    except Exception as e:
        try:
            await status.edit_text(
                "❌ AI Error\n\n"
                "Please try again later."
            )
        except Exception:
            await message.reply_text(
                "❌ AI Error\n\n"
                "Please try again later."
            )
