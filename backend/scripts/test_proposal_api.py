#!/usr/bin/env python
"""
Test script for the proposal generation API with real API providers.

This script makes real API calls to test the proposal generation functionality
using the actual Anthropic and OpenAI API keys configured in the environment.

Usage:
    docker compose exec backend python scripts/test_proposal_api.py

Requirements:
    - API keys must be set in the .env file
    - The backend server must be running
"""

import argparse
import asyncio
import json
import logging
import sys
import time
from datetime import datetime

import httpx

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("test_proposal_api")

# Set default URL for local testing
DEFAULT_URL = "http://localhost:8000/api/v1/proposals/generate"

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


async def get_auth_token():
    """Get authentication token for API calls."""
    # For testing purposes, we use a dummy auth method (would be replaced in production)
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "http://localhost:8000/api/v1/login/access-token",
                data={
                    "username": "admin@example.com",
                    "password": "admin"
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            response.raise_for_status()
            return response.json().get("access_token")
    except Exception as e:
        logger.error(f"Failed to get auth token: {e}")
        return None


async def test_proposal_generation(url, test_case, auth_token):
    """Test the proposal generation API with the given test case."""
    test_name = test_case["name"]
    test_data = test_case["data"]
    
    logger.info(f"Testing: {test_name}")
    logger.info(f"Input: {json.dumps(test_data, indent=2)}")
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {auth_token}"
    }
    
    start_time = time.time()
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                json=test_data,
                headers=headers,
                timeout=60.0  # Large timeout for AI generation
            )
            
            duration = time.time() - start_time
            status_code = response.status_code
            
            logger.info(f"Status: {status_code} (took {duration:.2f}s)")
            
            if status_code == 200:
                result = response.json()
                proposal_text = result.get("proposal_text", "")
                logger.info(f"Generated proposal ({len(proposal_text)} chars):")
                logger.info("-" * 80)
                logger.info(proposal_text[:500] + "..." if len(proposal_text) > 500 else proposal_text)
                logger.info("-" * 80)
                return True
            else:
                logger.error(f"Error response: {response.text}")
                return False
    except Exception as e:
        duration = time.time() - start_time
        logger.error(f"Request failed after {duration:.2f}s: {str(e)}")
        return False


async def main():
    """Run the test script."""
    parser = argparse.ArgumentParser(description="Test the proposal generation API")
    parser.add_argument("--url", default=DEFAULT_URL, help="URL of the proposal generation API")
    args = parser.parse_args()
    
    logger.info(f"Starting API test against {args.url}")
    
    # Get auth token
    auth_token = await get_auth_token()
    if not auth_token:
        logger.error("Failed to get authentication token. Aborting tests.")
        return
    
    # Run tests
    success_count = 0
    for test_case in TEST_DATA:
        if await test_proposal_generation(args.url, test_case, auth_token):
            success_count += 1
    
    logger.info(f"Tests completed: {success_count}/{len(TEST_DATA)} successful")


if __name__ == "__main__":
    asyncio.run(main()) 