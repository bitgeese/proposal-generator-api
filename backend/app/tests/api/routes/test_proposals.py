import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session
from unittest.mock import patch, AsyncMock

from app.main import app
from app.tests.utils.user import create_random_user
from app.tests.utils.utils import random_email, random_lower_string
from app.api.deps import get_current_user
from app.models import User, ProposalGeneratorOutput


# Mock user for testing
def mock_user():
    return User(
        id=1,
        email="test@example.com",
        is_active=True,
        is_superuser=True,
        full_name="Test User"
    )


@pytest.fixture
def superuser_token_headers(client: TestClient) -> dict[str, str]:
    return {"Authorization": "Bearer testtoken"}


# Override the dependency for testing
@pytest.fixture(autouse=True)
def override_dependencies():
    app.dependency_overrides[get_current_user] = mock_user
    yield
    app.dependency_overrides = {}


# Mock the generate_proposal function
async def mock_generate_proposal(*args, **kwargs):
    return ProposalGeneratorOutput(
        proposal_text="Sample proposal text",
        generation_time=1.5
    )


class TestProposalGeneration:
    
    @pytest.mark.parametrize("input_data", [
        # Basic valid input
        {
            "job_title": "Python Developer needed for web scraping project",
            "job_description": "We need a developer to build a robust web scraper",
            "skills": ["Python", "BeautifulSoup", "Scrapy"]
        },
        # With additional context
        {
            "job_title": "Python Developer needed for web scraping project",
            "job_description": "We need a developer to build a robust web scraper",
            "skills": ["Python", "BeautifulSoup", "Scrapy"],
            "additional_context": "I have 5 years of experience in web scraping"
        }
    ])
    def test_generate_proposal_valid(
        self, monkeypatch, client: TestClient, superuser_token_headers: dict[str, str], input_data
    ) -> None:
        """Test that a proposal can be generated with valid inputs."""
        # Monkeypatch the service function
        monkeypatch.setattr("app.api.routes.proposals.generate_proposal", mock_generate_proposal)
        
        response = client.post(
            "/api/v1/proposals/generate",
            headers=superuser_token_headers,
            json=input_data,
        )
        assert response.status_code == 200
        content = response.json()
        assert "proposal_text" in content
        assert "generation_time" in content
        assert content["proposal_text"]

    @pytest.mark.parametrize("invalid_input,expected_status", [
        # Missing required fields
        (
            {"job_description": "Description", "skills": ["Python"]},
            422  # Missing job_title
        ),
        # Empty strings
        (
            {"job_title": "", "job_description": "Description", "skills": ["Python"]},
            422
        ),
        # Empty skills list
        (
            {"job_title": "Python Developer", "job_description": "Description", "skills": []},
            422
        ),
    ])
    def test_generate_proposal_invalid(
        self, client: TestClient, superuser_token_headers: dict[str, str], 
        invalid_input, expected_status
    ) -> None:
        """Test that appropriate errors are returned for invalid inputs."""
        response = client.post(
            "/api/v1/proposals/generate",
            headers=superuser_token_headers,
            json=invalid_input,
        )
        assert response.status_code == expected_status

    def test_generate_proposal_unauthorized(self, client: TestClient) -> None:
        """Test that an error is returned when the user is not authenticated."""
        # Temporarily remove the dependency override for this test
        original_overrides = app.dependency_overrides.copy()
        app.dependency_overrides = {}
        
        try:
            data = {
                "job_title": "Python Developer needed for web scraping project",
                "job_description": "We need a developer to build a robust web scraper",
                "skills": ["Python", "BeautifulSoup", "Scrapy"]
            }
            response = client.post(
                "/api/v1/proposals/generate",
                json=data,
            )
            assert response.status_code == 401
        finally:
            # Restore the dependency override
            app.dependency_overrides = original_overrides 