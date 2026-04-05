import asyncio
import os
import random
import logging
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types, BaseMiddleware
from aiogram.types import BotCommand
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command
from aiogram.utils.chat_action import ChatActionSender
from PyCharacterAI import get_client

import sys
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s", stream=sys.stdout)
logger = logging.getLogger(__name__)

env_path = os.environ.get("PROFILE_ENV_PATH", ".env")
load_dotenv(env_path)
TG_TOKEN   = os.getenv("TG_TOKEN")
CAI_TOKEN  = os.getenv("CAI_TOKEN")
NEXT_AUTH  = os.getenv("NEXT_AUTH")
CHAR_ID    = os.getenv("CHAR_ID")
VOICE_ID   = os.getenv("VOICE_ID")   # optional — needed for voice messages
try:
    VOICE_PROBABILITY = float(os.getenv("VOICE_PROBABILITY", "25")) / 100.0
except ValueError:
    VOICE_PROBABILITY = 0.25
PERSONA_ID = os.getenv("PERSONA_ID") # optional — set who "you" are to the Character
OWNER_ID   = os.getenv("OWNER_ID")   # required — your Telegram user ID to prevent unauthorized access
STREAMER_MODE = os.getenv("STREAMER_MODE", "False").lower() == "true"


for name, val in {"TG_TOKEN": TG_TOKEN, "CAI_TOKEN": CAI_TOKEN, "CHAR_ID": CHAR_ID, "OWNER_ID": OWNER_ID}.items():
    if not val:
        raise EnvironmentError(f"Missing required env variable: {name}")

# --- Middleware ---
class OwnerOnlyMiddleware(BaseMiddleware):
    async def __call__(self, handler, event: types.Message, data: dict):
        # Allow access if OWNER_ID is not set, or if the user matches OWNER_ID
        if not OWNER_ID or event.from_user.id == int(OWNER_ID):
            return await handler(event, data)
        else:
            if STREAMER_MODE:
                logger.warning("Unauthorized access attempt from [HIDDEN]")
            else:
                logger.warning(f"Unauthorized access attempt from {event.from_user.id} (@{event.from_user.username})")
            return

# --- Persistent CAI state ---
cai_client   = None
cai_chat_id  = None
cai_greeting = None   # greeting text shown on /start (only set after create_chat)

# Tracks the last exchange so /retry, /undo, /pin know what to target.
# {"user_turn_id": str, "bot_turn_id": str, "bot_candidate_id": str}
last_turn: dict = {}

try:
    from aiogram.client.default import DefaultBotProperties
    bot = Bot(token=TG_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN))
except ImportError:
    bot = Bot(token=TG_TOKEN, parse_mode=ParseMode.MARKDOWN)

dp  = Dispatcher()


# ---------------------------------------------------------------------------
# CAI session management
# ---------------------------------------------------------------------------

async def init_cai(force_new: bool = False):
    """Authenticate with CAI and resume the newest existing chat, or create one.

    Args:
        force_new: Always create a brand-new chat (used by /reset).
    """
    global cai_client, cai_chat_id, cai_greeting

    logger.info("Connecting to CharacterAI...")
    cai_client = await get_client(token=CAI_TOKEN, web_next_auth=NEXT_AUTH)
    logger.info("CAI client authenticated successfully.")

    # Optionally apply a persona so the character knows who they're talking to.
    if PERSONA_ID:
        try:
            await cai_client.account.set_persona(CHAR_ID, PERSONA_ID)
            logger.info(f"Persona {PERSONA_ID} applied to character {CHAR_ID}.")
        except Exception as e:
            logger.warning(f"Could not set persona: {e}")

    if not force_new:
        logger.info(f"Fetching existing chats for character {CHAR_ID}...")
        try:
            chats = await cai_client.chat.fetch_chats(CHAR_ID)
            if chats:
                cai_chat_id  = chats[0].chat_id
                cai_greeting = None   # no greeting when resuming an existing chat
                if STREAMER_MODE:
                    logger.info(f"Resumed existing chat. ({len(chats)} total chats found)")
                else:
                    logger.info(f"Resumed existing chat. chat_id={cai_chat_id} "
                                f"({len(chats)} total chats found)")
                return
            logger.info("No existing chats found — will create a new one.")
        except Exception as e:
            logger.warning(f"fetch_chats failed ({e}), falling back to create_chat.")

    action = "Forcing new" if force_new else "Creating first"
    logger.info(f"{action} chat for character {CHAR_ID}...")
    chat, greeting_turn = await cai_client.chat.create_chat(CHAR_ID)
    cai_chat_id  = chat.chat_id
    cai_greeting = greeting_turn.get_primary_candidate().text if greeting_turn else None
    if STREAMER_MODE:
        logger.info("New chat created.")
    else:
        logger.info(f"New chat created. chat_id={cai_chat_id}")
    if cai_greeting:
        if STREAMER_MODE:
            logger.info("Greeting: [HIDDEN IN STREAMER MODE]")
        else:
            logger.info(f"Greeting ({len(cai_greeting)} chars): "
                        f"{cai_greeting[:80]}{'...' if len(cai_greeting) > 80 else ''}")


async def ensure_session():
    """Re-initialise the session if it was lost after an error."""
    if cai_client is None or cai_chat_id is None:
        logger.warning("CAI session missing — reinitialising (will resume existing chat)...")
        await init_cai()


# ---------------------------------------------------------------------------
# Core CAI helpers
# ---------------------------------------------------------------------------

async def get_bot_reply(text: str) -> tuple[str, str | None, str | None]:
    """Send a message and return (reply_text, bot_turn_id, bot_candidate_id)."""
    await ensure_session()
    if STREAMER_MODE:
        logger.info("-> CAI: [HIDDEN IN STREAMER MODE]")
    else:
        logger.info(f"-> CAI: {text[:60]}{'...' if len(text) > 60 else ''}")
    try:
        answer         = await cai_client.chat.send_message(CHAR_ID, cai_chat_id, text)
        candidate      = answer.get_primary_candidate()
        reply          = candidate.text
        bot_turn_id = answer.turn_id
        candidate_id   = candidate.candidate_id
        if STREAMER_MODE:
            logger.info("<- CAI: [HIDDEN IN STREAMER MODE]")
        else:
            logger.info(f"<- CAI ({len(reply)} chars): {reply[:80]}{'...' if len(reply) > 80 else ''}")
        return reply, bot_turn_id, candidate_id
    except Exception as e:
        logger.error(f"send_message failed: {e}", exc_info=True)
        # Avoid dropping the session so we don't have to fully re-authenticate on random CAI timeouts
        return "The character's brain stalled for a sec... try again?", None, None


async def maybe_send_voice(tg_message: types.Message, 
                           bot_turn_id: str | None,
                           candidate_id: str | None) -> bool:
    """Occasionally send a voice message (25% chance per reply).
    Returns True if a voice was sent successfully.
    Requires VOICE_ID to be set in .env.
    """
    # by default it is 25% but you can change it directly in the GUI or turn it off completely by setting 0%
    if not VOICE_ID or not bot_turn_id or not candidate_id:
        return False
    if random.random() > VOICE_PROBABILITY:
        return False

    logger.info(f"Generating voice for turn {bot_turn_id}...")
    try:
        speech_bytes = await cai_client.utils.generate_speech(
            cai_chat_id, bot_turn_id, candidate_id, VOICE_ID
        )
        audio = types.BufferedInputFile(speech_bytes, filename="voice.mp3")
        await tg_message.answer_voice(audio)
        logger.info("Voice message sent successfully.")
        return True
    except Exception as e:
        logger.warning(f"generate_speech failed: {e}")
        return False


# ---------------------------------------------------------------------------
# Command handlers
# ---------------------------------------------------------------------------

@dp.message(Command("start"))
async def start_handler(message: types.Message):
    logger.info(f"/start from {message.from_user.id} (@{message.from_user.username})")
    # cai_greeting is only set after create_chat (fresh or /reset).
    # On a resumed session it's None — no greeting object exists, so just say we're back. It is not the best solution, I know.
    text = cai_greeting or "hey, i'm back."
    await message.answer(text)


@dp.message(Command("reset"))
async def reset_handler(message: types.Message):
    """Force a brand-new chat with the Character (/reset)."""
    global cai_client, cai_chat_id, cai_greeting, last_turn
    logger.info(f"/reset from {message.from_user.id} (@{message.from_user.username})")
    status_msg = await message.answer("🔄 Resetting chat, please wait...")
    cai_client = cai_chat_id = cai_greeting = None
    last_turn  = {}
    await init_cai(force_new=True)
    logger.info("CAI session reset to a new chat.")
    await status_msg.edit_text(cai_greeting or "✅ chat reset — fresh start!")


@dp.message(Command("retry"))
async def retry_handler(message: types.Message):
    """Re-roll the character's last reply (/retry)."""
    logger.info(f"/retry from {message.from_user.id} (@{message.from_user.username})")
    if not last_turn.get("bot_turn_id"):
        await message.answer("nothing to retry yet — send a message first!")
        return

    await ensure_session()
    status_msg = await message.answer("🔄 Re-rolling response...")
    logger.info(f"Calling another_response for turn {last_turn['bot_turn_id']}...")
    try:
        async with ChatActionSender.typing(bot=bot, chat_id=message.chat.id):
            answer    = await cai_client.chat.another_response(
                CHAR_ID, cai_chat_id, last_turn["bot_turn_id"]
            )
        candidate = answer.get_primary_candidate()
        reply     = candidate.text

        # Update so the next /retry re-rolls this new response, not the old one.
        last_turn["bot_turn_id"]      = answer.turn_id
        last_turn["bot_candidate_id"] = candidate.candidate_id

        if STREAMER_MODE:
            logger.info("<- retry: [HIDDEN IN STREAMER MODE]")
        else:
            logger.info(f"<- retry ({len(reply)} chars): {reply[:80]}")
        try:
            await status_msg.edit_text(f"🔄 {reply}")
        except TelegramBadRequest:
            logger.warning("Markdown parse error on retry. Resending as plain text.")
            await status_msg.edit_text(f"🔄 {reply}", parse_mode=None)
            
        await maybe_send_voice(message, answer.turn_id, candidate.candidate_id)
    except Exception as e:
        logger.error(f"another_response failed: {e}", exc_info=True)
        await status_msg.edit_text("❌ couldn't re-roll that one... try again?")


@dp.message(Command("undo"))
async def undo_handler(message: types.Message):
    """Delete the last user message + the character's reply from the CAI chat (/undo)."""
    logger.info(f"/undo from {message.from_user.id} (@{message.from_user.username})")
    if not last_turn.get("bot_turn_id"):
        await message.answer("nothing to undo yet!")
        return

    await ensure_session()
    status_msg = await message.answer("🔄 Undoing last exchange...")
    try:
        # Fetch recent messages to find bot turn and user turn
        turns, _ = await cai_client.chat.fetch_messages(cai_chat_id)
        if not turns:
            await status_msg.edit_text("❌ nothing to undo yet!")
            return
            
        # Select the up to 2 most recent messages (bot reply + user prompt)
        turn_ids_to_delete = [turn.turn_id for turn in turns[:2]]

        await cai_client.chat.delete_messages(cai_chat_id, turn_ids_to_delete)
        logger.info(f"Deleted turns: {turn_ids_to_delete}")
        last_turn.clear()
        await status_msg.edit_text("✅ 🗑 last exchange deleted.")
    except Exception as e:
        logger.error(f"delete_messages failed: {e}", exc_info=True)
        await status_msg.edit_text("❌ couldn't undo that... try again?")


@dp.message(Command("pin"))
async def pin_handler(message: types.Message):
    """Pin the character's last reply in the CAI chat (/pin)."""
    logger.info(f"/pin from {message.from_user.id} (@{message.from_user.username})")
    if not last_turn.get("bot_turn_id"):
        await message.answer("no message to pin yet!")
        return

    await ensure_session()
    try:
        await cai_client.chat.pin_message(cai_chat_id, last_turn["bot_turn_id"])
        logger.info(f"Pinned turn {last_turn['bot_turn_id']}.")
        await message.answer("📌 message pinned.")
    except Exception as e:
        logger.error(f"pin_message failed: {e}", exc_info=True)
        await message.answer("couldn't pin that... try again?")


@dp.message(Command("pins"))
async def pins_handler(message: types.Message):
    """List all pinned messages in the current CAI chat (/pins)."""
    logger.info(f"/pins from {message.from_user.id} (@{message.from_user.username})")
    await ensure_session()
    try:
        pinned = await cai_client.chat.fetch_all_pinned_messages(cai_chat_id)
        if not pinned:
            await message.answer("no pinned messages yet.")
            return
        lines = []
        for i, turn in enumerate(pinned, 1):
            text    = turn.get_primary_candidate().text
            preview = text[:120] + ("..." if len(text) > 120 else "")
            lines.append(f"📌 {i}. {preview}")
        logger.info(f"Returning {len(pinned)} pinned messages.")
        await message.answer("\n\n".join(lines))
    except Exception as e:
        logger.error(f"fetch_all_pinned_messages failed: {e}", exc_info=True)
        await message.answer("couldn't fetch pinned messages... try again?")


@dp.message(Command("history"))
async def history_handler(message: types.Message):
    """Show the last 10 messages from the current CAI chat (/history)."""
    logger.info(f"/history from {message.from_user.id} (@{message.from_user.username})")
    await ensure_session()
    try:
        # fetch_messages returns one page (newest-first) plus a next_token for pagination.
        turns, _ = await cai_client.chat.fetch_messages(cai_chat_id)
        if not turns:
            await message.answer("no messages yet.")
            return
        # Last 10, reversed to oldest-first for readability.
        recent = turns[:10][::-1]
        lines  = []
        for turn in recent:
            candidate = turn.get_primary_candidate()
            if not candidate:
                continue
            author  = turn.author_name or "?"
            preview = candidate.text[:120] + ("..." if len(candidate.text) > 120 else "")
            lines.append(f"[{author}]: {preview}")
        logger.info(f"Returning {len(lines)} history entries.")
        await message.answer("\n\n".join(lines) if lines else "nothing to show.")
    except Exception as e:
        logger.error(f"fetch_messages failed: {e}", exc_info=True)
        await message.answer("couldn't fetch history... try again?")


@dp.message(Command("persona"))
async def persona_handler(message: types.Message):
    """Show or change the currently active persona (/persona [new_id])."""
    global PERSONA_ID
    # this shit does not work how am i supposed to fix this :sob:
    # it throws a 400 bad request error or something when i want to show the current persona
    # oh dear benjamin netanyahu please find us the way to fetch a current persona
    
    args = message.text.split(maxsplit=1)
    if len(args) > 1:
        new_persona = args[1].strip()
        if new_persona.lower() in ("none", "clear", "remove"):
            new_persona = None
            
        PERSONA_ID = new_persona
        await ensure_session()
        try:
            await cai_client.account.set_persona(CHAR_ID, PERSONA_ID)
            if PERSONA_ID:
                await message.answer(f"✅ Persona successfully changed to: {PERSONA_ID}")
            else:
                await message.answer("✅ Persona removed.")
        except Exception as e:
            logger.error(f"Failed to set persona: {e}", exc_info=True)
            await message.answer("❌ Couldn't change persona. Is the ID correct?")
        return

    if PERSONA_ID:
        await message.answer(
            f"🎭 active persona ID: {PERSONA_ID}\n"
            f"to change it, send `/persona <new_id>` (or `/persona none` to remove)"
        )
    else:
        await message.answer(
            "no persona set. to set one, send `/persona <id>`"
        )


@dp.message(Command("help"))
async def help_handler(message: types.Message):
    await message.answer(
        "📋 *commands*\n\n"
        "/start — show the character's greeting\n"
        "/retry — re-roll their last reply 🔄\n"
        "/undo — delete the last exchange 🗑\n"
        "/pin — pin their last reply 📌\n"
        "/pins — list all pinned messages\n"
        "/history — last 10 messages\n"
        "/persona — show active persona 🎭\n"
        "/reset — start a brand-new chat\n"
        "/help — this list",
        parse_mode="Markdown"
    )


# ---------------------------------------------------------------------------
# Main message handler
# ---------------------------------------------------------------------------

@dp.message()
async def chat_handler(message: types.Message):
    if not message.text:
        logger.debug(f"Ignored non-text update from {message.from_user.id} "
                     f"(type: {message.content_type})")
        return

    if STREAMER_MODE:
        logger.info("^ [HIDDEN USER]: [HIDDEN IN STREAMER MODE]")
    else:
        logger.info(f"^ {message.from_user.id} (@{message.from_user.username}): "
                    f"{message.text[:60]}{'...' if len(message.text) > 60 else ''}")

    async with ChatActionSender.typing(bot=bot, chat_id=message.chat.id):
        reply, bot_turn_id, candidate_id = await get_bot_reply(message.text)

    if bot_turn_id:
        last_turn["bot_turn_id"]      = bot_turn_id
        last_turn["bot_candidate_id"] = candidate_id
        # user_turn_id isn't returned by send_message; fetch it if /undo needs it.
        # For now we delete the character's turn only — that's enough to clean up the exchange.

    try:
        await message.answer(reply)
    except TelegramBadRequest:
        logger.warning("Markdown parse error. Resending as plain text.")
        await message.answer(reply, parse_mode=None)
        
    await maybe_send_voice(message, bot_turn_id, candidate_id)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

async def on_startup(bot: Bot):
    logger.info("The bot is waking up...")
    await init_cai()
    
    # Register commands so they appear in Telegram's menu (it does not work anyway, why bother? but I still added this, who knows, might work for you? x)
    await bot.set_my_commands([
        BotCommand(command="start",   description="Show the character's greeting"),
        BotCommand(command="retry",   description="Re-roll their last reply 🔄"),
        BotCommand(command="undo",    description="Delete the last exchange 🗑"),
        BotCommand(command="pin",     description="Pin their last reply 📌"),
        BotCommand(command="pins",    description="List all pinned messages"),
        BotCommand(command="history", description="Show last 10 messages"),
        BotCommand(command="persona", description="Show active persona 🎭"),
        BotCommand(command="reset",   description="Start a brand-new chat"),
        BotCommand(command="help",    description="Show all commands"),
    ])
    logger.info("Bot commands registered with Telegram.")

    # Notify desktop that the bot is online (intercepted by gui.py)
    startup_text = cai_greeting or "Ready to chat!"
    # Ensure this prints immediately so gui.py can intercept it
    print(f"[SYSTEM_NOTIFY:CAI-TG Online] {startup_text}", flush=True)
    if STREAMER_MODE:
        logger.info("Startup notification sent.")
    else:
        logger.info(f"Startup notification sent: {startup_text[:40]}...")

async def on_shutdown(bot: Bot):
    """Notify when the bot is shutting down."""
    print("[SYSTEM_NOTIFY:CAI-TG Offline] The bot is shutting down.", flush=True)
    logger.info("Shutdown notification sent.")
    await bot.session.close()


async def main():
    # Register the middleware to block unauthorized users
    dp.message.middleware(OwnerOnlyMiddleware())
    
    # Register lifecycle events
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("The bot is going to sleep. Bye!")
    except Exception as e:
        print(f"[SYSTEM_NOTIFY:Critical Error] {str(e)}", flush=True)
        logger.error(f"Critical Error: {e}", exc_info=True)
