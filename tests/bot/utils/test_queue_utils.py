import pytest
from unittest.mock import Mock, patch, PropertyMock
from bot.utils.queue_utils import q_dup_check
from bot.config import _bot

@pytest.fixture(autouse=True)
def reset_queue_status():
    """Reset _bot.queue_status before each test to prevent state leakage."""
    original_status = getattr(_bot, 'queue_status', []).copy()
    yield
    _bot.queue_status = original_status

@pytest.mark.asyncio
async def test_q_dup_check_empty_queue():
    # Setup
    _bot.queue_status = []
    event = Mock()
    event.chat_id = 123
    event.id = 456

    # Execute
    result = await q_dup_check(event)

    # Assert
    assert result == True

@pytest.mark.asyncio
async def test_q_dup_check_no_duplicate():
    # Setup
    _bot.queue_status = ["789 101"]
    event = Mock()
    event.chat_id = 123
    event.id = 456

    # Execute
    result = await q_dup_check(event)

    # Assert
    assert result == True

@pytest.mark.asyncio
async def test_q_dup_check_duplicate_exists():
    # Setup
    _bot.queue_status = ["123 456"]
    event = Mock()
    event.chat_id = 123
    event.id = 456

    # Execute
    result = await q_dup_check(event)

    # Assert
    assert result == False

@pytest.mark.asyncio
async def test_q_dup_check_exception_handling():
    # Setup
    _bot.queue_status = ["123 456"]
    event = Mock()
    # Mocking event to raise exception on attribute access
    type(event).chat_id = PropertyMock(side_effect=Exception("Test Exception"))

    # Execute
    with patch('bot.utils.queue_utils.logger') as mock_logger:
        result = await q_dup_check(event)

    # Assert
    assert result == True
    # The logger is a function: async def logger(exception, *, error=False):
    mock_logger.assert_called_once()
