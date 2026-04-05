# Frequently Asked Questions (FAQ) to CAI-TG

Here are some frequently asked questions about CAI-TG:

## What is the purpose of this script and why does it exist? Isn't the original Character.AI app enough?

This script acts as a bridge between Telegram and Character.AI, allowing you to chat with your favorite characters from Character.AI in Telegram. It is built using Python, aiogram and PyCharacterAI. The main reason for its existence is to provide a more convenient way to chat with characters, especially for those who prefer using Telegram for messaging or want to integrate Character.AI into their existing workflows, this script also bypasses ads built in Character.AI website and app. Plus this is a great way to learn Python and do not feel lonely. We understand that some people do not like the interface of Character.AI and prefer to use Telegram for messaging, so this script is a great solution for them.

## Is CAI-TG safe?

Yes, it is safe to use. This scripts runs locally on your device and does not send any data to the internet. It uses your own tokens to authenticate with the Character.AI API and Telegram API. The only data that is sent to the internet is the messages that you send to the character and the responses that you receive from the character. This is the same data that is sent to the Character.AI API and Telegram API when you use the Character.AI website and Telegram app, also this script is open-source and can be audited by anyone, so there is nothing to worry about. The only thing you have to worry about is where you downloaded this script from, because we recommend you to download it from the official GitHub repository, [GitHub](https://github.com/malichevsky/cai-tg), because it is the only place where you can get the original script without any modifications. Some malicious actors may try to distribute modified versions of this script with malicious code built in, such as token stealers, obfuscate the code and then send it to you or distribute it as their own, so be careful from where you download it and think twice before trusting anyone.

## How to get tokens?

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
   - On Character.AI, create your character or open the chat for the character you want your bot to connect to.
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

## How to extract tokens and IDs from HAR files?

1. Open [Character.AI](https://character.ai/) in your browser and log in.
2. Open your browser's Developer Tools (usually `F12` or Right-Click -> Inspect).
3. Go to the **Network** tab.
4. Refresh the page or interact with the site, then search the network requests for `https://character.ai/chat/user/`.
5. Press "Export HAR" button to export the HAR file.
6. In the GUI, go to the **Settings** tab and click on "Extract from HAR" button.
   - If you are in the first time using the script, it will ask you to select the HAR file, select the HAR file you exported and click on "Extract" button.
   - If you are not in the first time using the script, it will extract the tokens and IDs from the HAR file and fill in the fields in the **Settings** tab.
**Note**: This feature is experimental and may not work for all users. If it haven't found all the tokens, it is recommended to use a different browser like Firefox to extract HAR files, or you can manually copy the missing token and ID from the Developer Tools as described in the "How to get tokens?" section or HAR file.

## How to update the script?

Starting from v1.4.0 the script will automatically check for updates from the GitHub repository and notify you if there are any updates available to download. You can also manually check for updates by clicking on the "Check for updates" button, it will send you to the GitHub releases page where you can download the latest release. Older versions and manually pulled versions have no auto-update feature, so you have to manually pull the latest version from the GitHub repository or redownload the executable from the GitHub releases page.

## How to switch between characters?

To switch between characters, you need to create a new profile for the new character, press "New Profile" button to run the wizard again, after you fill in the required fields and save the profile, the bot will use the new character after you selected your new config. You can also delete profiles by pressing "Delete" button.

## I haven't found answer to my question, or something went wrong, what should I do?

If you encounter any issues while using the script and haven't found answer to your question in the FAQ page, feel free to report them by creating an issue on the GitHub repository: [Issues](https://github.com/malichevsky/cai-tg/issues). Make sure to include:

- A detailed description of the problem
- The steps to reproduce the issue
- Any error messages or logs (screenshots are welcome)
- Your operating system and Python version

Any other suggestions, help, discussions or feature requests are also welcome, we are open to any feedback!

## Any support for mobile devices, like Android?

Not yet, it is planned for the future. You can't use Termux to run this script because it requires a desktop environment to draw the GUI.

## Would I get banned for using this script?

Even though no one has reported being banned for using this script (neither me), it is still against Character.AI's Terms of Service to use any third-party tools to interact with unofficial APIs we use. Use it at your own risk. Please, do not make any complaints to us if you get banned, because once you pressed "Continue" button in First Time Setup Wizard you automatically agree that you are using this script at your own risk and we are not responsible for any consequences. We are not affiliated with Character.AI in any way, neither the original author of PyCharacterAI. We do not condone the use of this script for any malicious or for any other purposes that may violate Character.AI's Terms of Service, such as bypassing NSFW filters, etc. If you fear that your account may get banned, we recommend you to use a different account specifically for this script, otherwise don't use it and stick to the official website.

## Can I contribute to the project?

Yes, you can! We are open to any contributions, whether it's a bug fix, a new feature, or a documentation improvement. Feel free to create a pull request on the GitHub repository: [Pull Requests](https://github.com/malichevsky/cai-tg/pulls).
