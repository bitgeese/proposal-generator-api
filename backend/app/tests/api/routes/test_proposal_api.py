import pytest
import json
import logging
from typing import Dict, Any

from fastapi.testclient import TestClient

from app.main import app
from app.core.config import settings

logger = logging.getLogger("test_proposal_api")

# Test data for different scenarios
TEST_DATA = [
    {
        "name": "Basic Python Developer Job",
        "data": {
            "job_title": "Python Developer needed for web scraping project",
            "job_description": "We need a developer to build a robust web scraper that can extract data from e-commerce websites. The ideal candidate should have experience with Python, BeautifulSoup or Scrapy, and handling anti-scraping measures.",
            "skills": ["Python", "BeautifulSoup", "Scrapy", "Data Processing"]
        }
    },
    {
        "name": "Frontend Developer Job with Context",
        "data": {
            "job_title": "React Developer for E-commerce Dashboard",
            "job_description": "Looking for a React developer to build a responsive dashboard for our e-commerce platform. Must have experience with data visualization, state management, and API integration.",
            "skills": ["React", "TypeScript", "Redux", "REST API"],
            "additional_context": "I have 3 years of experience building React applications and have worked extensively with Redux and TypeScript in e-commerce projects."
        }
    }
]

@pytest.fixture
def superuser_token_headers(client: TestClient) -> Dict[str, str]:
    login_data = {
        "username": settings.FIRST_SUPERUSER,
        "password": settings.FIRST_SUPERUSER_PASSWORD,
    }
    r = client.post("/api/v1/login/access-token", data=login_data)
    tokens = r.json()
    a_token = tokens["access_token"]
    return {"Authorization": f"Bearer {a_token}"}


@pytest.mark.parametrize("test_case", TEST_DATA)
def test_proposal_generation(client: TestClient, superuser_token_headers: Dict[str, str], test_case: Dict[str, Any]):
    """Test the proposal generation API with the given test case."""
    test_name = test_case["name"]
    test_data = test_case["data"]
    
    logger.info(f"Testing: {test_name}")
    
    # Add content type header
    headers = {**superuser_token_headers, "Content-Type": "application/json"}
    
    response = client.post(
        "/api/v1/proposals/generate",
        json=test_data,
        headers=headers,
    )
    
    assert response.status_code == 200
    
    result = response.json()
    assert "proposal_text" in result
    assert "generation_time" in result
    
    proposal_text = result["proposal_text"]
    assert len(proposal_text) > 100  # Ensure we got a substantial proposal 