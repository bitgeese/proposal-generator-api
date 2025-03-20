"""Common fixtures for service tests."""

import pytest
from unittest.mock import AsyncMock, MagicMock

from app.models import ProposalGeneratorInput


@pytest.fixture
def mock_llm():
    """Fixture for a mocked LLM."""
    mock = MagicMock()
    mock.ainvoke = AsyncMock(return_value={"text": "This is a generated proposal."})
    return mock


@pytest.fixture
def mock_prompt():
    """Fixture for a mocked PromptTemplate."""
    mock = MagicMock()
    return mock


@pytest.fixture
def mock_chain():
    """Fixture for a mocked LLMChain."""
    mock = MagicMock()
    mock.ainvoke = AsyncMock(return_value={"text": "This is a generated proposal."})
    return mock


@pytest.fixture
def proposal_input():
    """Fixture for a sample proposal input."""
    return ProposalGeneratorInput(
        job_title="Python Developer",
        job_description="Looking for a Python developer for a web scraping project",
        skills=["Python", "Scrapy", "FastAPI"]
    )


@pytest.fixture
def proposal_input_with_context():
    """Fixture for a sample proposal input with additional context."""
    return ProposalGeneratorInput(
        job_title="Python Developer",
        job_description="Looking for a Python developer for a web scraping project",
        skills=["Python", "Scrapy", "FastAPI"],
        additional_context="5 years of experience"
    ) 