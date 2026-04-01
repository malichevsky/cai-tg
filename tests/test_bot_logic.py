import os
import asyncio
import pytest
from unittest.mock import AsyncMock, patch

# Configure fake environment BEFORE importing main
os.environ["TG_TOKEN"] = "123456789:ABCDEFGHIJKLMNOPQRSTUVWXYZ123456789"
os.environ["CAI_TOKEN"] = "dummy_cai_token"
os.environ["NEXT_AUTH"] = "dummy_next_auth"
os.environ["CHAR_ID"] = "dummy_char_id"
os.environ["OWNER_ID"] = "123456"

# Now safely import main
import main

class DummyUser:
    def __init__(self, user_id, username="test_user"):
        self.id = user_id
        self.username = username

class DummyEvent:
    def __init__(self, user_id):
        self.from_user = DummyUser(user_id)

@pytest.mark.asyncio
async def test_owner_middleware_allows_owner():
    mw = main.OwnerOnlyMiddleware()
    event = DummyEvent(123456)
    
    async def dummy_handler(ev, data):
        return "allowed"
        
    result = await mw(dummy_handler, event, {})
    assert result == "allowed"

@pytest.mark.asyncio
async def test_owner_middleware_blocks_others():
    mw = main.OwnerOnlyMiddleware()
    
    # Random unknown user ID
    event = DummyEvent(999999) 
    
    async def dummy_handler(ev, data):
        return "allowed"
        
    result = await mw(dummy_handler, event, {})
    assert result is None  # Middleware returns None on blocked access

@pytest.mark.asyncio
@patch('main.init_cai', new_callable=AsyncMock)
async def test_ensure_session_reinitializes(mock_init_cai):
    main.cai_client = None
    main.cai_chat_id = None
    
    await main.ensure_session()
    
    # Fast-check that ensure_session triggers init_cai when variables are null
    mock_init_cai.assert_called_once()
