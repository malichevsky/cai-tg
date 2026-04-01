# CAI-TG (Character.AI Telegram Bridge)

This script acts as a functional bridge connecting a Telegram bot to a [Character.AI](https://character.ai/) persona. Built using Python, `aiogram`, and `PyCharacterAI`, it allows you to communicate seamlessly with your favorite CAI characters straight from Telegram text and voice messages.

It features a **native cross-platform GUI** built with PyQt6 that lets you manage multiple character profiles, edit tokens easily, and monitor the bot's live standard output with syntax highlighting!

## Features

- **Profile Manager GUI**: Easily switch between multiple character configurations (saved in the `profiles/` directory) without touching code.
- **Universal Bootstrapper**: One script magically hooks up the entire environment across Windows, MacOS, and Linux.
- **Text & Voice Chat**: Send your Character messages and receive text responses with occasional voice replies, if the voice ID is provided (you also can set the probability of voice replies in the GUI).
- **Chat Management**: Use straightforward Telegram commands to manage your ongoing CAI session.
- **Persistent State**: The bot dynamically creates or resumes chat sessions.
- **Persona Context**: Apply optional user Persona IDs to provide context directly to the Character.
- **Secured Access**: The bot is strictly locked to your personal Telegram User ID to prevent unauthorized users from chatting with it or leaking your session keys.
- **Enhanced privacy**: Toggle streamer mode to hide sensitive information from logs (tokens, chat IDs, etc.) and restrict access to the bot to only the owner by default.

## Setup & Launching

You do **NOT** need to manually install dependencies or manually create `.env` files. The project includes a universal `start.py` bootstrapper that handles everything automatically.

**Install the script:**

You have a few ways to install this script:

1. **Git**: Run this command in your terminal or command prompt (requires Git installed)

   ```bash
   git clone https://github.com/malichevsky/cai-tg.git
   ```

2. **Download**: Download the script by pressing the Code button on the GitHub page and selecting Download ZIP.

**Run the Universal Launcher:**

```bash
python3 start.py
```

*(Use `python start.py` on Windows)*

This script will:

1. Automatically create an isolated virtual environment (`.venv`)
2. Install all required dependencies from `requirements.txt` quietly
3. Launch the native Desktop Interface

## Using the GUI

Once the GUI opens:

1. **First Launch**: It will prompt you to create your first `Profile`. Pick a recognizable name for your character.
2. **Settings**: Switch to the **Settings** tab. Fill in your tokens. You can click the `[?]` help icons next to each field to get a detailed tutorial on where to find your *Telegram Token*, *Character.AI Token*, etc.
3. Hit **Save Settings**.
4. Click **▶ Start Bot**. Switch to the **Console** tab to watch the live colorized event logs!

## Reporting an Issue?

If you encounter any issues while using the script, feel free to report them by creating an issue on the GitHub repository. Make sure to include:

- A detailed description of the problem
- The steps to reproduce the issue
- Any error messages or logs (screenshots are welcome)
- Your operating system and Python version

Any other suggestions, help, discussions or feature requests are also welcome, we are open to any feedback!

## Useful Telegram Commands

While chatting with your bot on Telegram, you can use these commands to manage the CAI connection:

- `/start` — Retrieve the character's initial greeting or resume message.
- `/retry` — Re-roll the character's last reply 🔄
- `/undo` — Delete the last exchange 🗑
- `/pin` — Pin the character's last reply 📌
- `/pins` — List all pinned messages in the current CAI chat.
- `/history` — Display the last 10 messages.
- `/persona` — Display your active persona ID 🎭
- `/reset` — Forcefully start a brand-new chat.
- `/help` — Display the list of all commands.

## How to get tokens

To make the script and the bot work you need to get the following tokens, here is how to get them:

1. **Character.AI Token (`CAI_TOKEN`) and `web_next_auth` Token (`NEXT_AUTH`)**:

   This is the most important part, without it the bot will not work because it uses these tokens to authenticate with the Character.AI API.
   - Open the [Character.AI](https://character.ai/) website in your browser and log in.
   - Open your browser's Developer Tools (usually `F12` or Right-Click -> Inspect).
   - Go to the **Network** tab.
   - Refresh the page or interact with the site, then search the network requests for `https://character.ai/chat/user/`.
   - Click on the request and look at the **Headers** tab. Scroll down to *Request Headers* and find the Authentication header — this is your `CAI_TOKEN`.
   - Next, go to the **Storage** (or **Application**) tab in the Developer Tools.
   - Expand **Cookies** for `https://character.ai` and look for the `web_next_auth` cookie. The value of this cookie is your `NEXT_AUTH` token.

2. **Telegram Bot Token (`TG_TOKEN`)**:

   A token that allows the bot to connect to the Telegram API. Without it the bot will not work because it uses this token to send messages to the Telegram API.
   - Open Telegram and search for the [@BotFather](https://t.me/BotFather).
   - Send the `/newbot` command and follow the instructions to create a new bot.
   - BotFather will provide you with an HTTP API Token. This is your `TG_TOKEN`.

3. **Character ID (`CHAR_ID`)**:

   This is the ID of the character you want to talk to. This script needs this ID to send messages from the character to the Telegram bot.
   - On Character.AI, open the chat for the character you want your bot to connect to.
   - Look at the URL in your browser's address bar (e.g., `https://character.ai/chat/<CHAR_ID>`).
   - The string of characters directly after `/chat/` is your `CHAR_ID`.

4. **Owner ID (`OWNER_ID`)**:

   A strictly required field. It is used to lock the bot to your personal Telegram User ID to prevent unauthorized users from chatting with it or leaking your session keys.
   - Open Telegram and search for the [@userinfobot](https://t.me/userinfobot).
   - Send the `/start` command and userinfobot will provide you with your numerical User ID. This is your `OWNER_ID`.

5. **Voice ID (`VOICE_ID`)**:

   (Optional) If you want the character to reply with voice notes, put a valid CAI Voice ID here, otherwise leave it empty.
   - Open [Character.AI](https://character.ai/) and navigate to the character you want to use.
   - Click the **three dots** menu in the top-right corner of the chat window.
   - Select **Edit Character**.
   - In the character settings, look for the **Voice** option. Click on it to see a list of available voices.
   - Select the voice you want to use. The Voice ID will be displayed in the URL of the voice selection page or in the browser's developer tools when the voice is selected.

6. **Persona ID (`PERSONA_ID`)**:

   (Optional) If you want to provide context to the character, put a valid CAI Persona ID here, otherwise leave it empty.
   - Open [Character.AI](https://character.ai/) and navigate to the character you want to use.
   - Click the **three dots** menu in the top-right corner of the chat window.
   - Select **Edit Character**.
   - In the character settings, look for the **Persona** option. Click on it to see a list of available personas.
   - Select the persona you want to use. The Persona ID will be displayed in the URL of the persona selection page or in the browser's developer tools when the persona is selected.

## Credits

`cai-tg` is built using the following amazing open-source libraries, without them, it wouldn't be possible to create this project. We thank the authors of these libraries for their great work:

- [aiogram](https://github.com/aiogram/aiogram)
- [PyCharacterAI](https://github.com/Xtr4F/PyCharacterAI)
- [PyQt6](https://github.com/PyQt6/PyQt6)
- [rich](https://github.com/Textualize/rich)
