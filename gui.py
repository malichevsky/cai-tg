import sys
import os
import json

if len(sys.argv) > 1 and sys.argv[1] == "--bot":
    import asyncio
    import main
    try:
        asyncio.run(main.main())
    except (KeyboardInterrupt, SystemExit):
        pass
    sys.exit(0)

import re
from pathlib import Path
from dotenv import dotenv_values, set_key

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTabWidget, QLabel, QLineEdit, QPushButton, QComboBox,
    QTextEdit, QFormLayout, QMessageBox, QInputDialog, QToolButton,
    QWizard, QWizardPage, QSpinBox, QCheckBox, QSystemTrayIcon, QStyle,
    QFileDialog
)
from PyQt6.QtGui import QTextCursor, QTextCharFormat, QColor, QFont, QIcon, QDesktopServices
from PyQt6.QtCore import QProcess, pyqtSlot, Qt, QProcessEnvironment, QTimer, QThread, pyqtSignal, QUrl
import urllib.request
import json

VERSION = "1.2.0-dev"

def is_newer_version(local, remote):
    l_parts = local.lstrip('v').split('-')[0].split('.')
    r_parts = remote.lstrip('v').split('-')[0].split('.')
    for l, r in zip(l_parts, r_parts):
        try:
           if int(r) > int(l): return True
           if int(r) < int(l): return False
        except ValueError:
           pass
    return len(r_parts) > len(l_parts)

class UpdateCheckerThread(QThread):
    update_available = pyqtSignal(str, str)

    def run(self):
        try:
            req = urllib.request.Request(
                "https://api.github.com/repos/malichevsky/cai-tg/releases/latest", 
                headers={'User-Agent': 'CAI-TG-Updater'}
            )
            with urllib.request.urlopen(req, timeout=5) as response:
                data = json.loads(response.read().decode())
                latest_version = data.get("tag_name", "")
                url = data.get("html_url", "")
                
                if latest_version and is_newer_version(VERSION, latest_version):
                    self.update_available.emit(latest_version, url)
        except Exception:
            pass

PROFILES_DIR = Path("profiles")

MODERN_DARK_THEME = """
QWidget {
    background-color: #1e1e1e;
    color: #cccccc;
    font-family: 'Segoe UI', Inter, Roboto, sans-serif;
    font-size: 10pt;
}
QTabWidget::pane {
    border: 1px solid #3c3c3c;
    background-color: #252526;
    border-radius: 4px;
}
QTabBar::tab {
    background: #2d2d2d;
    color: #9d9d9d;
    padding: 8px 20px;
    margin-right: 2px;
    border-top-left-radius: 4px;
    border-top-right-radius: 4px;
    border: 1px solid #3c3c3c;
    border-bottom: none;
}
QTabBar::tab:selected {
    background: #252526;
    color: #ffffff;
    font-weight: bold;
    border-top: 2px solid #007acc;
}
QTabBar::tab:hover:!selected {
    background: #333333;
    color: #cccccc;
}
QPushButton {
    background-color: #0e639c;
    color: #ffffff;
    border: none;
    border-radius: 4px;
    padding: 8px 16px;
    font-weight: bold;
}
QPushButton:hover {
    background-color: #1177bb;
}
QPushButton:pressed {
    background-color: #094771;
}
QPushButton:disabled {
    background-color: #4d4d4d;
    color: #888888;
}
QPushButton#newProfileBtn { background-color: #4CAF50; }
QPushButton#newProfileBtn:hover { background-color: #388E3C; }
QPushButton#deleteBtn { background-color: #f44336; }
QPushButton#deleteBtn:hover { background-color: #d32f2f; }
QPushButton#startBtn { background-color: #2196F3; padding: 10px 16px; font-size: 11pt; }
QPushButton#startBtn:hover { background-color: #1976D2; }
QPushButton#stopBtn { background-color: #f44336; padding: 10px 16px; font-size: 11pt; }
QPushButton#stopBtn:hover { background-color: #d32f2f; }
QPushButton#harBtn { background-color: #673AB7; padding: 8px; }
QPushButton#harBtn:hover { background-color: #512DA8; }
QPushButton#saveBtn { background-color: #FF9800; padding: 8px; }
QPushButton#saveBtn:hover { background-color: #F57C00; }
QToolButton {
    background-color: #333333;
    color: #ffffff;
    border-radius: 4px;
    padding: 4px;
    border: 1px solid #3c3c3c;
}
QToolButton:hover {
    background-color: #444444;
}
QToolButton#helpBtn {
    border-radius: 10px;
}
QLineEdit, QTextEdit, QSpinBox, QComboBox {
    background-color: #3c3c3c;
    color: #cccccc;
    border: 1px solid #555555;
    border-radius: 4px;
    padding: 6px;
}
QLineEdit:focus, QTextEdit:focus, QSpinBox:focus, QComboBox:focus {
    border: 1px solid #007acc;
    background-color: #444444;
}
QComboBox::drop-down {
    border: none;
    width: 20px;
}
QComboBox QAbstractItemView {
    background-color: #3c3c3c;
    color: #cccccc;
    selection-background-color: #007acc;
}
QCheckBox {
    spacing: 5px;
    color: white;
}
QCheckBox::indicator {
    width: 18px;
    height: 18px;
    background-color: #3c3c3c;
    border: 1px solid #555555;
    border-radius: 2px;
}
QCheckBox::indicator:checked {
    background-color: #007acc;
    border: 1px solid #007acc;
}
QScrollArea, QWizard {
    background-color: #1e1e1e;
}
QLabel#requiredLabel {
    color: #ffeb3b;
    font-weight: bold;
}
QLabel#boldLabel {
    font-weight: bold;
}
QScrollBar:vertical {
    border: none;
    background: #1e1e1e;
    width: 14px;
    margin: 0px 0px 0px 0px;
}
QScrollBar::handle:vertical {
    background: #424242;
    min-height: 20px;
    border-radius: 7px;
    margin: 2px;
}
QScrollBar::handle:vertical:hover {
    background: #4f4f4f;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    border: none;
    background: none;
    height: 0px;
}
"""

ENV_KEYS = {
    "TG_TOKEN": {"help": "Telegram Bot Token. Get this by chatting with @BotFather on Telegram and creating a new bot.\n\nREQUIRED", "type": "password"},
    "CAI_TOKEN": {"help": "Character.AI Token. Required for authentication. You can extract this from your browser's local storage or cookies when logged into Character.AI.\n\nREQUIRED", "type": "password"},
    "NEXT_AUTH": {"help": "Next Auth Token. Extra authentication string. Extract via cookies similar to CAI_TOKEN.\n\nREQUIRED", "type": "password"},
    "CHAR_ID": {"help": "Character ID. Found in the URL of the character you want to chat with on Character.AI.\n\nREQUIRED", "type": "text"},
    "OWNER_ID": {"help": "Your numerical Telegram User ID. Strictly prevents unauthorized access.\n\nREQUIRED", "type": "password"},
    "VOICE_ID": {"help": "(Optional) Voice ID. If you want the character to reply with voice notes, put a valid CAI Voice ID here.", "type": "text"},
    "VOICE_PROBABILITY": {"help": "(Optional) Chance of sending a voice reply (0-100%). Default is 25%.", "type": "number"},
    "PERSONA_ID": {"help": "(Optional) Persona ID. Used to set who YOU are to the character.", "type": "text"},
    "STREAMER_MODE": {"help": "(Optional) Toggle this on to hide sensitive IDs and message content in the console.", "type": "bool"}
}

def extract_tokens_from_har(har_path):
    try:
        with open(har_path, "r", encoding="utf-8") as f:
            har_data = json.load(f)
            
        cai_token = None
        next_auth = None
        
        entries = har_data.get("log", {}).get("entries", [])
        for entry in entries:
            request = entry.get("request", {})
            url = request.get("url", "")
            if "character.ai" in url.lower() or "neo.character.ai" in url.lower():
                headers = request.get("headers", [])
                for header in headers:
                    name = header.get("name", "").lower()
                    value = header.get("value", "")
                    if name == "authorization" and value.startswith("Token "):
                        cai_token = value[6:]
                    
                    if name == "cookie":
                        if "web_next_auth=" in value:
                            parts = value.split(";")
                            for p in parts:
                                p = p.strip()
                                if p.startswith("web_next_auth="):
                                    next_auth = p[len("web_next_auth="):]
                                    
                cookies = request.get("cookies", [])
                for cookie in cookies:
                    if cookie.get("name") == "web_next_auth":
                        next_auth = cookie.get("value")
                
            if cai_token and next_auth:
                break
                
        return cai_token, next_auth
    except Exception:
        return None, None

class PasswordInput(QWidget):
    def __init__(self, is_password=True):
        super().__init__()
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.line_edit = QLineEdit()
        
        self.is_password = is_password
        if self.is_password:
            self.line_edit.setEchoMode(QLineEdit.EchoMode.Password)

        self.btn_eye = QToolButton()
        self.btn_eye.setText("👁")
        
        if self.is_password:
            self.btn_eye.pressed.connect(self.show_text)
            self.btn_eye.released.connect(self.hide_text)
        else:
            self.btn_eye.hide()
            
        layout.addWidget(self.line_edit)
        layout.addWidget(self.btn_eye)

    def show_text(self):
        self.line_edit.setEchoMode(QLineEdit.EchoMode.Normal)

    def hide_text(self):
        self.line_edit.setEchoMode(QLineEdit.EchoMode.Password)
        
    def text(self):
        return self.line_edit.text()
        
    def setText(self, val):
        self.line_edit.setText(val)
        
    def clear(self):
        self.line_edit.clear()

class PageWelcome(QWizardPage):
    def __init__(self):
        super().__init__()
        self.setTitle("Welcome to CAI-TG")
        self.setSubTitle("A native bridge between Telegram and Character.AI")
        
        layout = QVBoxLayout(self)
        inst = QLabel(
            "<b>CAI-TG</b> runs a local bot on your machine that connects your Telegram account to Character.AI, allowing you to chat directly from Telegram.<br><br>"
            "<b>SECURITY WARNING:</b><br>"
            "This application handles highly sensitive session tokens that give full access to your Character.AI and Telegram accounts, especially if you pay for Character.AI Plus or any paid subscriptions. Using modified or unofficial versions can result in your accounts being compromised by malicious actors.<br><br>"
            "You must ensure that you downloaded this program from the <b>only reputable source</b>:<br>"
            "<b>github.com/malichevsky/cai-tg</b>"
        )
        inst.setWordWrap(True)
        layout.addWidget(inst)
        
        ban_warning = QLabel(
            "<br><b>TERMS OF USAGE WARNING:</b><br>"
            "Even though no one has reported being banned for using this script, it is still against Character.AI's Terms of Service to use any third-party tools to interact with unofficial APIs we use. Use it at your own risk. Please, do not make any complaints to us if you get banned, because once you pressed \"Continue\" button in First Time Setup Wizard you automatically agree that you are using this script at your own risk and we are not responsible for any consequences. Note that we are not affiliated with Character.AI in any way, neither the original author of PyCharacterAI. We do not condone the use of this script for any malicious or for any other purposes that may violate Character.AI's Terms of Service, such as bypassing NSFW filters, etc. If you fear that your account may get banned, we recommend you to use a different account specifically for this script, otherwise press \"Cancel\" button and do not use this script."
        )
        ban_warning.setWordWrap(True)
        layout.addWidget(ban_warning)
        
        self.confirm_cb = QCheckBox("I confirm I installed this from malichevsky/cai-tg")
        self.confirm_cb.setEnabled(False)
        self.confirm_cb.stateChanged.connect(self.completeChanged)
        layout.addWidget(self.confirm_cb)
        
        self.terms_cb = QCheckBox("I willingly agree to such terms of usage and use it at my own risk")
        self.terms_cb.setEnabled(False)
        self.terms_cb.stateChanged.connect(self.completeChanged)
        layout.addWidget(self.terms_cb)
        
        self.timer_label = QLabel("Please carefully read the warning. You can proceed in 30 seconds.")
        self.timer_label.setStyleSheet("color: #ffb74d; font-weight: bold;")
        layout.addWidget(self.timer_label)
        
        self.counter = 30
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_timer)
        self.timer.start(1000)

    def isComplete(self):
        return self.confirm_cb.isChecked() and self.terms_cb.isChecked()

    def update_timer(self):
        self.counter -= 1
        if self.counter > 0:
            self.timer_label.setText(f"Please carefully read the warning. You can proceed in {self.counter} seconds.")
        else:
            self.timer.stop()
            self.timer_label.setText("You may now proceed.")
            self.timer_label.setStyleSheet("color: #81c784; font-weight: bold;")
            self.confirm_cb.setEnabled(True)
            self.terms_cb.setEnabled(True)

class PageTelegram(QWizardPage):
    def __init__(self):
        super().__init__()
        self.setTitle("Step 1: Telegram Configuration")
        self.setSubTitle("We need to connect your local app to Telegram first.")
        
        layout = QVBoxLayout(self)
        inst = QLabel(
            "1. Open Telegram and search for <b>@BotFather</b>.<br>"
            "2. Send the <code>/newbot</code> command and follow the instructions.<br>"
            "3. BotFather will output a <b>HTTP API Token</b>. Copy it into the field below.<br><br>"
            "4. Search for <b>@userinfobot</b> on Telegram to retrieve your numerical <b>User ID</b>. We use this strictly to lock the bot to your account so no one else can talk to your character."
        )
        inst.setWordWrap(True)
        layout.addWidget(inst)
        
        form = QFormLayout()
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("e.g. MyWife (Don't use spaces)")
        self.registerField("profile_name*", self.name_edit)
        form.addRow("Profile Name:", self.name_edit)
        
        self.tg_edit = PasswordInput()
        self.registerField("tg_token*", self.tg_edit.line_edit)
        form.addRow("TG_TOKEN:", self.tg_edit)

        self.owner_edit = PasswordInput()
        self.registerField("owner_id*", self.owner_edit.line_edit)
        form.addRow("OWNER_ID:", self.owner_edit)

        layout.addLayout(form)

class PageCAI(QWizardPage):
    def __init__(self):
        super().__init__()
        self.setTitle("Step 2: Character.AI Tokens")
        self.setSubTitle("We need to grab your browser tokens so the bot behaves as you.")
        
        layout = QVBoxLayout(self)
        inst = QLabel(
            "<b>Option A: Automatic (Recommended)</b><br>"
            "1. Open <b>character.ai</b> and log in.<br>"
            "2. Open Developer Tools (<code>F12</code>), go to the <b>Network</b> tab, and refresh.<br>"
            "3. Right-click any request and select <b>Save all as HAR with content</b>.<br>"
            "4. Click the button below.<br>"
            "<i>(Disclaimer: The .HAR file is processed entirely locally on your computer. Your files and data are not sent anywhere, and your account remains perfectly safe.)</i><br><br>"
            "<b>Option B: Manual</b><br>"
            "1. Find a request like <code>chat/user</code>, copy the <code>Authorization</code> token for <b>CAI_TOKEN</b>.<br>"
            "2. Under the Application/Storage tab, find the <code>web_next_auth</code> cookie for <b>NEXT_AUTH</b>."
        )
        inst.setWordWrap(True)
        layout.addWidget(inst)
        
        self.btn_har = QPushButton("🔍 Auto-Detect from .HAR File")
        self.btn_har.setObjectName("harBtn")
        self.btn_har.clicked.connect(self.load_from_har)
        layout.addWidget(self.btn_har)
        
        form = QFormLayout()
        self.cai_edit = PasswordInput()
        self.registerField("cai_token*", self.cai_edit.line_edit)
        form.addRow("CAI_TOKEN:", self.cai_edit)

        self.next_edit = PasswordInput()
        self.registerField("next_auth*", self.next_edit.line_edit)
        form.addRow("NEXT_AUTH:", self.next_edit)

        layout.addLayout(form)

    def load_from_har(self):
        reply = QMessageBox.warning(self, "Security Warning",
            "HAR files contain highly sensitive session tokens that give full access to your Character.AI account.\n\n"
            "NEVER share a HAR file with anyone else!\n\n"
            "By continuing, you confirm you are using a legitimate copy of CAI-TG downloaded from the official source.\n\n"
            "Do you want to proceed and select a HAR file?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No)
            
        if reply != QMessageBox.StandardButton.Yes:
            return

        path, _ = QFileDialog.getOpenFileName(self, "Select HAR File", "", "HAR Files (*.har);;JSON Files (*.json);;All Files (*)")
        if not path:
            return
            
        cai, nxt = extract_tokens_from_har(path)
        if cai or nxt:
            if cai: self.cai_edit.setText(cai)
            if nxt: self.next_edit.setText(nxt)
            QMessageBox.information(self, "Success", "Tokens extracted successfully!")
            
            del_reply = QMessageBox.question(self, "Delete HAR File?",
                "It's highly recommended to delete the .har file from your computer now to protect your session tokens.\n\n"
                "Would you like to securely delete the file now?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.Yes)
                
            if del_reply == QMessageBox.StandardButton.Yes:
                import os
                try:
                    os.remove(path)
                    QMessageBox.information(self, "Deleted", "The HAR file has been securely deleted from your system.")
                except Exception as e:
                    QMessageBox.warning(self, "Error", f"Failed to delete file: {e}\n\nPlease delete it manually!")
        else:
            QMessageBox.warning(self, "Error", "Could not find Character.AI tokens in this file. Make sure you were logged in and refreshed the page.")

class PageChar(QWizardPage):
    def __init__(self):
        super().__init__()
        self.setTitle("Step 3: Character Selection")
        self.setSubTitle("Which character do you want to talk to?")
        
        layout = QVBoxLayout(self)
        inst = QLabel(
            "1. On Character.AI, open the chat for the character you want to connect to.<br>"
            "2. Look at the URL in your browser's address bar (e.g., <code>character.ai/chat/SOME_LONG_ID</code>).<br>"
            "3. Copy that long ID string after <code>/chat/</code> and paste it below."
        )
        inst.setWordWrap(True)
        layout.addWidget(inst)
        
        form = QFormLayout()
        self.char_edit = PasswordInput(is_password=False)
        self.registerField("char_id*", self.char_edit.line_edit)
        form.addRow("CHAR_ID:", self.char_edit)
        layout.addLayout(form)

class OOBEWizard(QWizard):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("CAI-TG First-Time Setup")
        self.resize(800, 650)
        self.setWizardStyle(QWizard.WizardStyle.ModernStyle)
        self.setButtonText(QWizard.WizardButton.NextButton, "Continue")
        
        self.addPage(PageWelcome())
        self.addPage(PageTelegram())
        self.addPage(PageCAI())
        self.addPage(PageChar())

    def create_env_file(self):
        name = self.field("profile_name")
        if not name: return ""
        
        name = re.sub(r'[^a-zA-Z0-9_\-]', '', name)
        env_path = PROFILES_DIR / f"{name}.env"
        env_path.write_text("")
        
        set_key(str(env_path), "TG_TOKEN", self.field("tg_token"))
        set_key(str(env_path), "OWNER_ID", self.field("owner_id"))
        set_key(str(env_path), "CAI_TOKEN", self.field("cai_token"))
        set_key(str(env_path), "NEXT_AUTH", self.field("next_auth"))
        set_key(str(env_path), "CHAR_ID", self.field("char_id"))
        
        return name

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("CAI-TG Bot Manager")
        self.resize(850, 650)

        PROFILES_DIR.mkdir(parents=True, exist_ok=True)

        self.bot_process = QProcess(self)
        self.bot_process.readyReadStandardOutput.connect(self.handle_stdout)
        self.bot_process.readyReadStandardError.connect(self.handle_stderr)
        self.bot_process.stateChanged.connect(self.handle_state_changed)
        self.bot_process.finished.connect(self.handle_finished)

        self.init_tray()
        self.init_ui()
        self.load_profiles()

        self.update_thread = UpdateCheckerThread(self)
        self.update_thread.update_available.connect(self.show_update_button)
        self.update_thread.start()

    def show_update_button(self, version, url):
        self.btn_update.setText(f"🎁 Update Available! ({version})")
        
        # Disconnect any previously connected signals to avoid multiple tabs opening if somehow called multiple times
        try: self.btn_update.clicked.disconnect() 
        except TypeError: pass
        
        self.btn_update.clicked.connect(lambda: QDesktopServices.openUrl(QUrl(url)))
        self.btn_update.show()

    def init_tray(self):
        self.tray_icon = QSystemTrayIcon(self)
        icon = self.style().standardIcon(QStyle.StandardPixmap.SP_ComputerIcon)
        self.tray_icon.setIcon(icon)
        self.tray_icon.show()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # --- Top Bar for Profiles & Controls ---
        top_layout = QHBoxLayout()
        
        top_layout.addWidget(QLabel("Profile:"))
        self.profile_combo = QComboBox()
        self.profile_combo.currentTextChanged.connect(self.on_profile_changed)
        top_layout.addWidget(self.profile_combo)

        self.btn_new_profile = QPushButton("New Profile")
        self.btn_new_profile.setObjectName("newProfileBtn")
        self.btn_new_profile.clicked.connect(self.create_profile)
        top_layout.addWidget(self.btn_new_profile)

        self.btn_delete_profile = QPushButton("Delete")
        self.btn_delete_profile.setObjectName("deleteBtn")
        self.btn_delete_profile.clicked.connect(self.delete_profile)
        top_layout.addWidget(self.btn_delete_profile)

        top_layout.addStretch()

        self.btn_start = QPushButton("▶ Start Bot")
        self.btn_start.setObjectName("startBtn")
        self.btn_start.clicked.connect(self.start_bot)
        top_layout.addWidget(self.btn_start)

        self.btn_stop = QPushButton("⏹ Stop Bot")
        self.btn_stop.setObjectName("stopBtn")
        self.btn_stop.setEnabled(False)
        self.btn_stop.clicked.connect(self.stop_bot)
        top_layout.addWidget(self.btn_stop)

        self.btn_update = QPushButton("🎁 Update Available!")
        self.btn_update.setObjectName("updateBtn")
        self.btn_update.setStyleSheet("background-color: #9C27B0; font-weight: bold; color: white; padding: 10px 16px; font-size: 11pt; border-radius: 4px;")
        self.btn_update.hide()
        top_layout.addWidget(self.btn_update)

        main_layout.addLayout(top_layout)

        # --- Tabs ---
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)

        self.init_console_tab()
        self.init_settings_tab()
        self.init_about_tab()

    def init_console_tab(self):
        console_widget = QWidget()
        layout = QVBoxLayout(console_widget)

        self.console_output = QTextEdit()
        self.console_output.setReadOnly(True)
        font = QFont("Consolas", 10)
        font.setStyleHint(QFont.StyleHint.Monospace)
        self.console_output.setFont(font)

        layout.addWidget(self.console_output)
        self.tabs.addTab(console_widget, "Console")

    def init_settings_tab(self):
        settings_widget = QWidget()
        layout = QVBoxLayout(settings_widget)

        form_layout = QFormLayout()
        self.settings_fields = {}

        for key, config in ENV_KEYS.items():
            help_text = config["help"]
            field_type = config["type"]
            
            field_layout = QHBoxLayout()
            
            if field_type == "bool":
                widget = QCheckBox()
            elif field_type == "number":
                widget = QSpinBox()
                widget.setRange(0, 100)
                widget.setSuffix("%")
                widget.setValue(25)
            else:
                widget = PasswordInput(is_password=(field_type == "password"))
                
            help_btn = QToolButton()
            help_btn.setText("?")
            help_btn.setToolTip(help_text)
            help_btn.setObjectName("helpBtn")
            help_btn.clicked.connect(lambda checked, text=help_text, k=key: QMessageBox.information(self, f"Help: {k}", text))
            
            field_layout.addWidget(widget)
            field_layout.addWidget(help_btn)

            label = QLabel(key)
            if "REQUIRED" in help_text:
                label.setObjectName("requiredLabel")
            else:
                label.setObjectName("boldLabel")
                
            form_layout.addRow(label, field_layout)
            self.settings_fields[key] = widget

        layout.addLayout(form_layout)

        self.btn_har = QPushButton("🔍 Extract Tokens from .HAR File (Safe & Local)")
        self.btn_har.setObjectName("harBtn")
        self.btn_har.clicked.connect(self.load_from_har_settings)
        layout.addWidget(self.btn_har)

        self.btn_save = QPushButton("Save Settings")
        self.btn_save.setObjectName("saveBtn")
        self.btn_save.clicked.connect(self.save_settings)
        layout.addWidget(self.btn_save)

        layout.addStretch()
        self.tabs.addTab(settings_widget, "Settings")

    def init_about_tab(self):
        about_widget = QWidget()
        layout = QVBoxLayout(about_widget)

        credits_label = QLabel(
            "<h2>CAI-TG Bot Manager</h2>"
            "<p>A native cross-platform GUI for bridging Telegram bots to Character.AI.</p>"
            "<h3>Credits</h3>"
            "<p>This project uses the following amazing open-source libraries, without them, it wouldn't be possible to create this project. We thank the authors of these libraries for their great work:</p>"
            "<ul>"
            "<li><b>aiogram</b>: <a href='https://github.com/aiogram/aiogram' style='color: #4dd0e1;'>https://github.com/aiogram/aiogram</a></li>"
            "<li><b>PyCharacterAI</b>: <a href='https://github.com/Xtr4F/PyCharacterAI' style='color: #4dd0e1;'>https://github.com/Xtr4F/PyCharacterAI</a></li>"
            "<li><b>PyQt6</b>: <a href='https://github.com/PyQt6/PyQt6' style='color: #4dd0e1;'>https://github.com/PyQt6/PyQt6</a></li>"
            "<li><b>rich</b>: <a href='https://github.com/Textualize/rich' style='color: #4dd0e1;'>https://github.com/Textualize/rich</a></li>"
            "</ul>"
        )
        credits_label.setOpenExternalLinks(True)
        credits_label.setWordWrap(True)
        
        layout.addWidget(credits_label)
        layout.addStretch()

        self.tabs.addTab(about_widget, "About")

    def load_profiles(self):
        self.profile_combo.blockSignals(True)
        self.profile_combo.clear()
        
        env_files = list(PROFILES_DIR.glob("*.env"))
        
        if not env_files:
            root_env = Path(".env")
            if root_env.exists():
                import shutil
                shutil.copy(root_env, PROFILES_DIR / "default.env")
                env_files = [PROFILES_DIR / "default.env"]
            else:
                self.oobe_wizard()
                env_files = list(PROFILES_DIR.glob("*.env"))

        for file in env_files:
            self.profile_combo.addItem(file.stem)

        self.profile_combo.blockSignals(False)
        
        if self.profile_combo.count() > 0:
            self.on_profile_changed(self.profile_combo.currentText())

    def oobe_wizard(self):
        wizard = OOBEWizard(self)
        # Block until finished
        if wizard.exec() == QWizard.DialogCode.Accepted:
            new_prof = wizard.create_env_file()
            if new_prof:
                QMessageBox.information(self, "Setup Complete", f"Profile '{new_prof}' was created successfully!")
        else:
            QMessageBox.warning(self, "Setup Cancelled", "You bypassed the setup wizard. You will need to click 'New Profile' to get started later.")

    def create_profile(self):
        wizard = OOBEWizard(self)
        if wizard.exec() == QWizard.DialogCode.Accepted:
            new_prof = wizard.create_env_file()
            if new_prof:
                self.load_profiles()
                self.profile_combo.setCurrentText(new_prof)
                QMessageBox.information(self, "Success", f"Profile '{new_prof}' created!")

    def delete_profile(self):
        current = self.profile_combo.currentText()
        if not current:
            return
            
        reply = QMessageBox.question(self, "Confirm Delete", 
                             f"Are you sure you want to delete profile '{current}'?",
                             QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
                             
        if reply == QMessageBox.StandardButton.Yes:
            env_path = PROFILES_DIR / f"{current}.env"
            if env_path.exists():
                env_path.unlink()
            self.load_profiles()

    def get_field_value(self, key, widget):
        if isinstance(widget, QCheckBox):
            return "True" if widget.isChecked() else "False"
        elif isinstance(widget, QSpinBox):
            return str(widget.value())
        elif isinstance(widget, PasswordInput):
            return widget.text()
        return ""

    def set_field_value(self, key, widget, value):
        if isinstance(widget, QCheckBox):
            widget.setChecked(str(value).lower() == "true")
        elif isinstance(widget, QSpinBox):
            try:
                widget.setValue(int(value) if value else 25)
            except ValueError:
                widget.setValue(25)
        elif isinstance(widget, PasswordInput):
            widget.setText(value)

    @pyqtSlot(str)
    def on_profile_changed(self, profile_name):
        if not profile_name:
            for key, field in self.settings_fields.items():
                self.set_field_value(key, field, "")
            return
            
        env_path = PROFILES_DIR / f"{profile_name}.env"
        if not env_path.exists():
            return
            
        values = dotenv_values(env_path)
        for key, field in self.settings_fields.items():
            self.set_field_value(key, field, values.get(key, ""))

    def save_settings(self):
        current = self.profile_combo.currentText()
        if not current:
            QMessageBox.warning(self, "Error", "No profile selected.")
            return

        env_path = PROFILES_DIR / f"{current}.env"
        if not env_path.exists():
            env_path.write_text("")
            
        for key, field in self.settings_fields.items():
            value = self.get_field_value(key, field)
            set_key(str(env_path), key, value)
            
        QMessageBox.information(self, "Success", "Settings saved successfully!")

    def load_from_har_settings(self):
        reply = QMessageBox.warning(self, "Security Warning",
            "HAR files contain highly sensitive session tokens that give full access to your Character.AI account.\n\n"
            "NEVER share a HAR file with anyone else!\n\n"
            "By continuing, you confirm you are using a legitimate copy of CAI-TG downloaded from the official source.\n\n"
            "Do you want to proceed and select a HAR file?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No)
            
        if reply != QMessageBox.StandardButton.Yes:
            return

        path, _ = QFileDialog.getOpenFileName(self, "Select HAR File", "", "HAR Files (*.har);;JSON Files (*.json);;All Files (*)")
        if not path:
            return
            
        cai, nxt = extract_tokens_from_har(path)
        updated = False
        if cai and "CAI_TOKEN" in self.settings_fields:
            self.settings_fields["CAI_TOKEN"].setText(cai)
            updated = True
        if nxt and "NEXT_AUTH" in self.settings_fields:
            self.settings_fields["NEXT_AUTH"].setText(nxt)
            updated = True
            
        if updated:
            QMessageBox.information(self, "Success", "Tokens extracted successfully! Remember to click 'Save Settings'.")
            
            del_reply = QMessageBox.question(self, "Delete HAR File?",
                "It's highly recommended to delete the .har file from your computer now to protect your session tokens.\n\n"
                "Would you like to securely delete the file now?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.Yes)
                
            if del_reply == QMessageBox.StandardButton.Yes:
                import os
                try:
                    os.remove(path)
                    QMessageBox.information(self, "Deleted", "The HAR file has been securely deleted from your system.")
                except Exception as e:
                    QMessageBox.warning(self, "Error", f"Failed to delete file: {e}\n\nPlease delete it manually!")
        else:
            QMessageBox.warning(self, "Error", "Could not find Character.AI tokens in this file.")

    def start_bot(self):
        current = self.profile_combo.currentText()
        if not current:
            QMessageBox.warning(self, "Error", "No profile selected.")
            return

        env_path = PROFILES_DIR / f"{current}.env"
        
        self.console_output.clear()
        self.append_log(f"--- Starting bot using profile: {current} ---\n", color="yellow")

        process_env = QProcessEnvironment.systemEnvironment()
        process_env.insert("PROFILE_ENV_PATH", str(env_path.absolute()))
        self.bot_process.setProcessEnvironment(process_env)

        if getattr(sys, 'frozen', False):
            # Running within PyInstaller bundle
            python_exec = sys.executable
            args = ["--bot"]
        else:
            python_exec = sys.executable
            args = ["main.py"]

        self.bot_process.start(python_exec, args)

    def stop_bot(self):
        if self.bot_process.state() == QProcess.ProcessState.Running:
            self.append_log("--- Stopping bot... ---\n", color="yellow")
            if os.name == 'nt':
                # On Windows, terminate() sends a hard kill which bypasses Python's shutdown hooks.
                # So we manually trigger the shutdown notification in the GUI.
                # That is why we all hate Microslop Windows...
                self.tray_icon.showMessage("CAI-TG Offline", "The bot is shutting down.", QSystemTrayIcon.MessageIcon.Information, 5000)
            self.bot_process.terminate() # Graceful exit

    # --- QProcess Handlers ---
    def handle_finished(self, exit_code, exit_status):
        self.append_log(f"--- Bot stopped (Exit code: {exit_code}) ---\n", color="orange")
        
    def handle_state_changed(self, state):
        if state == QProcess.ProcessState.Running:
            self.btn_start.setEnabled(False)
            self.btn_stop.setEnabled(True)
            self.profile_combo.setEnabled(False)
        else:
            self.btn_start.setEnabled(True)
            self.btn_stop.setEnabled(False)
            self.profile_combo.setEnabled(True)

    def handle_stdout(self):
        data = self.bot_process.readAllStandardOutput().data().decode("utf-8", errors="replace")
        
        # Intercept and display system notifications
        for line in data.splitlines():
            if line.startswith("[SYSTEM_NOTIFY:"):
                try:
                    tag_end = line.index("]")
                    title = line[15:tag_end]
                    message = line[tag_end+1:].strip()
                    self.tray_icon.showMessage(title, message, QSystemTrayIcon.MessageIcon.Information, 5000)
                except ValueError:
                    pass
                    
        self.colorize_and_append(data)

    def handle_stderr(self):
        data = self.bot_process.readAllStandardError().data().decode("utf-8", errors="replace")
        self.colorize_and_append(data, True)

    def colorize_and_append(self, text, is_err=False):
        cursor = self.console_output.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        
        for line in text.strip('\r').split('\n'):
            if not line:
                continue
                
            fmt = QTextCharFormat()
            if is_err or "[ERROR]" in line or "[CRITICAL]" in line or "Traceback" in line:
                fmt.setForeground(QColor("#ef5350")) # Red
            elif "-> CAI:" in line:
                fmt.setForeground(QColor("#4dd0e1")) # Cyan
            elif "<- CAI" in line or "<- retry" in line:
                fmt.setForeground(QColor("#81c784")) # Light Green
            elif "[WARNING]" in line:
                fmt.setForeground(QColor("#ffb74d")) # Orange
            else:
                fmt.setForeground(QColor("#e0e0e0")) # Default text
                
            cursor.setCharFormat(fmt)
            cursor.insertText(line + "\n")
            
        self.console_output.setTextCursor(cursor)
        self.console_output.ensureCursorVisible()

    def append_log(self, text, color="white"):
        cursor = self.console_output.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        fmt = QTextCharFormat()
        fmt.setForeground(QColor(color))
        cursor.setCharFormat(fmt)
        cursor.insertText(text)
        self.console_output.setTextCursor(cursor)
        self.console_output.ensureCursorVisible()

    def closeEvent(self, event):
        self.stop_bot()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(MODERN_DARK_THEME)
    
    try:
        import aiogram
        import PyCharacterAI
    except ImportError:
        QMessageBox.critical(None, "Dependencies Missing", 
            "Required packages are missing.\nPlease run: pip install -r requirements.txt")
            
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
