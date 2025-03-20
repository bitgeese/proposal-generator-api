import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session

from app.main import app
from app.tests.utils.user import create_random_user
from app.tests.utils.utils import random_email, random_lower_string


@pytest.fixture
def superuser_token_headers(client: TestClient) -> dict[str, str]:
    return {"Authorization": "Bearer testtoken"}


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
        self, client: TestClient, superuser_token_headers: dict[str, str], input_data
    ) -> None:
        """Test that a proposal can be generated with valid inputs."""
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