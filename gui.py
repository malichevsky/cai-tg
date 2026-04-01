import sys
import os

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
    QWizard, QWizardPage, QSpinBox, QCheckBox, QSystemTrayIcon, QStyle
)
from PyQt6.QtGui import QTextCursor, QTextCharFormat, QColor, QFont, QIcon
from PyQt6.QtCore import QProcess, pyqtSlot, Qt, QProcessEnvironment

PROFILES_DIR = Path("profiles")

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

class PasswordInput(QWidget):
    def __init__(self, is_password=True):
        super().__init__()
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.line_edit = QLineEdit()
        self.line_edit.setStyleSheet("QLineEdit { background-color: #3b3b3b; color: white; padding: 5px; }")
        
        self.is_password = is_password
        if self.is_password:
            self.line_edit.setEchoMode(QLineEdit.EchoMode.Password)

        self.btn_eye = QToolButton()
        self.btn_eye.setText("👁")
        self.btn_eye.setStyleSheet("QToolButton { background-color: #555555; padding: 2px; }")
        
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
            "1. Open <b>character.ai</b> in your browser and log in.<br>"
            "2. Open Developer Tools (<code>F12</code> or Right Click -> Inspect).<br>"
            "3. Go to the <b>Network</b> tab, refresh the page, and search for <code>chat/user</code>.<br>"
            "4. Click the request, look at the <b>Request Headers</b>, and copy the <code>Authorization</code> token. (Paste in <b>CAI_TOKEN</b> below).<br><br>"
            "5. Go to the <b>Storage</b> or <b>Application</b> tab.<br>"
            "6. Expand Cookies for <code>character.ai</code> and find <code>web_next_auth</code>. Copy its value. (Paste in <b>NEXT_AUTH</b> below)."
        )
        inst.setWordWrap(True)
        layout.addWidget(inst)
        
        form = QFormLayout()
        self.cai_edit = PasswordInput()
        self.registerField("cai_token*", self.cai_edit.line_edit)
        form.addRow("CAI_TOKEN:", self.cai_edit)

        self.next_edit = PasswordInput()
        self.registerField("next_auth*", self.next_edit.line_edit)
        form.addRow("NEXT_AUTH:", self.next_edit)

        layout.addLayout(form)

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
        self.resize(700, 500)
        self.setWizardStyle(QWizard.WizardStyle.ModernStyle)
        # Apply dark theme
        self.setStyleSheet("QWizard { background-color: #2b2b2b; color: white; } QLabel { color: white; }")
        
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
        self.setStyleSheet("QMainWindow { background-color: #2b2b2b; } QWidget { color: #ffffff; }")

        PROFILES_DIR.mkdir(parents=True, exist_ok=True)

        self.bot_process = QProcess(self)
        self.bot_process.readyReadStandardOutput.connect(self.handle_stdout)
        self.bot_process.readyReadStandardError.connect(self.handle_stderr)
        self.bot_process.stateChanged.connect(self.handle_state_changed)
        self.bot_process.finished.connect(self.handle_finished)

        self.init_tray()
        self.init_ui()
        self.load_profiles()

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
        self.profile_combo.setStyleSheet("QComboBox { background-color: #3b3b3b; padding: 5px; }")
        self.profile_combo.currentTextChanged.connect(self.on_profile_changed)
        top_layout.addWidget(self.profile_combo)

        self.btn_new_profile = QPushButton("New Profile")
        self.btn_new_profile.setStyleSheet("background-color: #4CAF50; color: white;")
        self.btn_new_profile.clicked.connect(self.create_profile)
        top_layout.addWidget(self.btn_new_profile)

        self.btn_delete_profile = QPushButton("Delete")
        self.btn_delete_profile.setStyleSheet("background-color: #f44336; color: white;")
        self.btn_delete_profile.clicked.connect(self.delete_profile)
        top_layout.addWidget(self.btn_delete_profile)

        top_layout.addStretch()

        self.btn_start = QPushButton("▶ Start Bot")
        self.btn_start.setStyleSheet("background-color: #2196F3; color: white; font-weight: bold; padding: 8px 16px;")
        self.btn_start.clicked.connect(self.start_bot)
        top_layout.addWidget(self.btn_start)

        self.btn_stop = QPushButton("⏹ Stop Bot")
        self.btn_stop.setStyleSheet("background-color: #f44336; color: white; padding: 8px 16px;")
        self.btn_stop.setEnabled(False)
        self.btn_stop.clicked.connect(self.stop_bot)
        top_layout.addWidget(self.btn_stop)

        main_layout.addLayout(top_layout)

        # --- Tabs ---
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("QTabBar::tab { background: #3b3b3b; padding: 8px; margin: 2px; } QTabBar::tab:selected { background: #555555; font-weight: bold; }")
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
        self.console_output.setStyleSheet("QTextEdit { background-color: #1e1e1e; color: #d4d4d4; }")

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
                widget.setStyleSheet("QCheckBox { spacing: 5px; color: white; }")
            elif field_type == "number":
                widget = QSpinBox()
                widget.setRange(0, 100)
                widget.setSuffix("%")
                widget.setStyleSheet("QSpinBox { background-color: #3b3b3b; color: white; padding: 5px; }")
                widget.setValue(25)
            else:
                widget = PasswordInput(is_password=(field_type == "password"))
                
            help_btn = QToolButton()
            help_btn.setText("?")
            help_btn.setToolTip(help_text)
            help_btn.setStyleSheet("QToolButton { background-color: #555555; border-radius: 10px; padding: 4px; }")
            help_btn.clicked.connect(lambda checked, text=help_text, k=key: QMessageBox.information(self, f"Help: {k}", text))
            
            field_layout.addWidget(widget)
            field_layout.addWidget(help_btn)

            label = QLabel(key)
            if "REQUIRED" in help_text:
                label.setStyleSheet("font-weight: bold; color: #ffeb3b;")
            else:
                label.setStyleSheet("font-weight: bold;")
                
            form_layout.addRow(label, field_layout)
            self.settings_fields[key] = widget

        layout.addLayout(form_layout)

        self.btn_save = QPushButton("Save Settings")
        self.btn_save.setStyleSheet("background-color: #FF9800; color: white; padding: 8px;")
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
            elif "→ CAI:" in line:
                fmt.setForeground(QColor("#4dd0e1")) # Cyan
            elif "← CAI" in line:
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
    
    try:
        import aiogram
        import PyCharacterAI
    except ImportError:
        QMessageBox.critical(None, "Dependencies Missing", 
            "Required packages are missing.\nPlease run: pip install -r requirements.txt")
            
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
