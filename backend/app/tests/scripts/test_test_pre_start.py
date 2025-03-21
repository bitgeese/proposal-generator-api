import logging
import pytest
from sqlmodel import select
from unittest.mock import MagicMock, patch

from app.tests_pre_start import init
from app.core.db import engine as db_engine
from app.tests_pre_start import main as tests_main

logger = logging.getLogger("app.tests_pre_start")


def test_init_successful_connection() -> None:
    engine_mock = MagicMock()
    session_mock = MagicMock()
    
    with patch("app.tests_pre_start.Session", return_value=session_mock) as mock_session:
        try:
            init(engine_mock)
            connection_successful = True
        except Exception:
            connection_successful = False

        assert connection_successful, "The database connection should be successful"
        mock_session.assert_called_once_with(engine_mock)
        # In a with statement, __enter__ is called to get the context manager value
        session_mock.__enter__.assert_called_once()
        # __exit__ is called when leaving the with block, which should close the session
        session_mock.__exit__.assert_called_once()


def test_init_executes_query():
    """Test that init executes a query to check DB connection."""
    engine_mock = MagicMock()
    session_mock = MagicMock()
    
    with patch("app.tests_pre_start.Session", return_value=session_mock) as mock_session:
        init(engine_mock)
        
        # Verify the session was created and used
        mock_session.assert_called_once_with(engine_mock)
        session_mock.__enter__.assert_called_once()
        session_mock.__exit__.assert_called_once()
        
        # Verify query execution
        session_enter_mock = session_mock.__enter__.return_value
        session_enter_mock.exec.assert_called_once()


def test_main_success():
    """Test that main successfully initializes the database."""
    with patch("app.tests_pre_start.init", return_value=None) as mock_init:
        tests_main()
        mock_init.assert_called_once_with(db_engine)
