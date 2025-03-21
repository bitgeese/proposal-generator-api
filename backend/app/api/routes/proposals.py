from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse

from app.api.deps import CurrentUser
from app.models import ProposalGeneratorInput, ProposalGeneratorOutput, Message
from app.services.proposal_generator import generate_proposal, ProposalGenerationError

router = APIRouter(prefix="/proposals", tags=["proposals"])


@router.post(
    "/generate", 
    response_model=ProposalGeneratorOutput,
    status_code=status.HTTP_200_OK,
    responses={
        200: {
            "description": "Successfully generated proposal",
            "content": {
                "application/json": {
                    "example": {
                        "proposal_text": "Hi there, I noticed your job posting for a Python Developer and I'm excited about the opportunity to build a robust web scraper for your project. With 5+ years of Python experience and expertise in BeautifulSoup and Scrapy, I've successfully delivered similar web scraping solutions for clients in various industries.\n\nI'd approach your project by first understanding the specific data points you need to extract, then designing a scalable scraper that respects website policies and handles different edge cases gracefully. My implementations typically include proper error handling, rate limiting, and data cleaning to ensure you get high-quality results.\n\nI'm particularly interested in learning more about your specific use case - are you looking to scrape data on a recurring schedule or as a one-time extraction? This would help me recommend the most appropriate architecture for your needs.\n\nI'm available to start immediately and can deliver an initial working prototype within the first week. Let me know if you'd like to discuss your requirements in more detail.\n\nLooking forward to potentially working together!\n\nBest regards,\n[Your Name]",
                        "generation_time": "2023-03-20T12:34:56.789Z"
                    }
                }
            }
        },
        401: {
            "description": "Unauthorized",
            "content": {"application/json": {"example": {"detail": "Not authenticated"}}}
        },
        422: {
            "description": "Validation Error",
            "content": {
                "application/json": {
                    "example": {
                        "detail": [
                            {
                                "loc": ["body", "job_title"],
                                "msg": "field required",
                                "type": "value_error.missing"
                            }
                        ]
                    }
                }
            }
        },
        500: {
            "description": "Internal Server Error",
            "content": {
                "application/json": {
                    "example": {"detail": "Error generating proposal: Failed to connect to AI service provider"}
                }
            }
        }
    }
)
async def generate_proposal_endpoint(
    *,
    current_user: CurrentUser,
    proposal_input: ProposalGeneratorInput,
) -> Any:
    """
    Generate a personalized Upwork proposal based on job details.
    
    This endpoint uses AI to create a customized proposal for a job posting based on:
    - The job title and description 
    - Your relevant skills
    - Optional additional context about your experience
    
    The generated proposal will:
    - Be professionally written and personalized to match the job requirements
    - Highlight your skills relevant to the specific job
    - Include engagement elements to increase response rates
    - Be properly formatted and ready to submit
    
    **Rate limits may apply** depending on your subscription level.
    
    **Authentication required**: Only authenticated users can access this endpoint.
    """
    try:
        result = await generate_proposal(proposal_input)
        return result
    except ProposalGenerationError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating proposal: {str(e)}"
        ) 