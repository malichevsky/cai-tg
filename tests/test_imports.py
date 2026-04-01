import os
import sys
import pytest

def setup_environ():
    os.environ["TG_TOKEN"] = "123456789:ABCDEFGHIJKLMNOPQRSTUVWXYZ123456789"
    os.environ["CAI_TOKEN"] = "dummy_cai_token"
    os.environ["NEXT_AUTH"] = "dummy_next_auth"
    os.environ["CHAR_ID"] = "dummy_char_id"
    os.environ["OWNER_ID"] = "123456789"

def test_main_import():
    # Setup dummy env variables before importing main to prevent EnvironmentError
    setup_environ()
    
    import main
    assert main.TG_TOKEN == "123456789:ABCDEFGHIJKLMNOPQRSTUVWXYZ123456789"
    assert main.bot is not None

def test_gui_import():
    # Setup offscreen rendering for headless CI environments
    if os.environ.get("GITHUB_ACTIONS"):
        os.environ["QT_QPA_PLATFORM"] = "offscreen"
        
    import gui
    assert gui.MainWindow is not None
