"""Service for generating Upwork proposal texts using LangChain."""

import json
import logging
import time
from datetime import datetime
from typing import Any, Dict, List, Optional

from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI
from pydantic import ValidationError

from app.core.config import settings
from app.models import ProposalGeneratorInput, ProposalGeneratorOutput

# Set up logging with structured format
logger = logging.getLogger("proposal_generator")

# Default prompt template
DEFAULT_TEMPLATE = """
You are an expert freelancer who specializes in writing effective Upwork proposals. 
Your task is to create a high-quality, personalized proposal for a job posting based on the information provided.

Job Title: {job_title}

Job Description: 
{job_description}

Skills Required: {skills}

{additional_context_prompt}

Create a professional, personalized proposal that:
1. Shows understanding of the client's needs and project requirements
2. Highlights relevant experience and skills without overwhelming
3. Demonstrates enthusiasm for the project
4. Includes a specific question about the project to engage the client
5. Is concise (250-300 words) and well-structured

PROPOSAL:
"""

class ProposalGenerationError(Exception):
    """Exception raised for errors in the proposal generation process."""
    pass


class ProposalGenerator:
    """Service for generating Upwork proposals using LangChain."""
    
    def __init__(
        self,
        model_name: Optional[str] = None,
        temperature: float = 0.7,
        prompt_template: Optional[str] = None,
    ):
        """
        Initialize the proposal generator with LangChain components.
        
        Args:
            model_name: The name of the model to use (defaults to config or "claude-3-haiku-20240307")
            temperature: Controls randomness in generation (0.0 to 1.0)
            prompt_template: Custom prompt template (if None, uses default template)
        """
        self.model_name = model_name or settings.DEFAULT_LLM_MODEL or "claude-3-haiku-20240307"
        self.temperature = temperature
        self.prompt_template = prompt_template or DEFAULT_TEMPLATE
        
        logger.info(
            "Initializing ProposalGenerator",
            extra={
                "model_name": self.model_name,
                "temperature": self.temperature,
                "prompt_template_size": len(self.prompt_template),
            }
        )
        
        # Determine which provider to use based on model name
        if "claude" in self.model_name.lower():
            if not settings.ANTHROPIC_API_KEY:
                logger.error("Missing ANTHROPIC_API_KEY for Claude model")
                raise ProposalGenerationError("ANTHROPIC_API_KEY is required for Claude models")
            self.llm = ChatAnthropic(
                model=self.model_name,
                temperature=self.temperature,
                anthropic_api_key=settings.ANTHROPIC_API_KEY,
            )
            logger.debug("Using Anthropic Claude model")
        else:  # Default to OpenAI
            if not settings.OPENAI_API_KEY:
                logger.error("Missing OPENAI_API_KEY for OpenAI model")
                raise ProposalGenerationError("OPENAI_API_KEY is required for OpenAI models")
            self.llm = ChatOpenAI(
                model=self.model_name,
                temperature=self.temperature,
                openai_api_key=settings.OPENAI_API_KEY,
            )
            logger.debug("Using OpenAI ChatGPT model")
        
        # Set up the LangChain
        self._setup_chain()
    
    def _setup_chain(self) -> None:
        """Set up the LangChain for proposal generation."""
        self.prompt = PromptTemplate(
            template=self.prompt_template,
            input_variables=["job_title", "job_description", "skills", "additional_context_prompt"],
        )
        self.chain = LLMChain(llm=self.llm, prompt=self.prompt)
        logger.debug("LangChain setup complete")
    
    async def generate_proposal(self, input_data: ProposalGeneratorInput) -> ProposalGeneratorOutput:
        """
        Generate a proposal based on the input data.
        
        Args:
            input_data: The proposal generation input data
            
        Returns:
            A ProposalGeneratorOutput with the generated proposal text and timestamp
            
        Raises:
            ProposalGenerationError: If there's an error during generation
        """
        generation_id = f"gen_{int(time.time())}"
        
        # Log the start of proposal generation
        logger.info(
            "Starting proposal generation",
            extra={
                "generation_id": generation_id,
                "job_title": input_data.job_title,
                "job_description_length": len(input_data.job_description),
                "skills_count": len(input_data.skills),
                "has_additional_context": input_data.additional_context is not None,
                "model_used": self.model_name,
            }
        )
        
        start_time = time.time()
        
        try:
            # Prepare additional context
            additional_context_prompt = ""
            if input_data.additional_context:
                additional_context_prompt = f"Additional Context: {input_data.additional_context}"
            
            # Format skills as a comma-separated list
            skills_str = ", ".join(input_data.skills)
            
            # Generate proposal
            logger.debug(
                "Invoking AI model",
                extra={
                    "generation_id": generation_id,
                    "model": self.model_name,
                }
            )
            
            result = await self.chain.ainvoke({
                "job_title": input_data.job_title,
                "job_description": input_data.job_description,
                "skills": skills_str,
                "additional_context_prompt": additional_context_prompt,
            })
            
            proposal_text = result.get("text", "").strip()
            processing_time = time.time() - start_time
            
            # Log successful generation
            logger.info(
                "Proposal generation successful",
                extra={
                    "generation_id": generation_id,
                    "processing_time_seconds": processing_time,
                    "proposal_length": len(proposal_text),
                }
            )
            
            # Create output model
            return ProposalGeneratorOutput(
                proposal_text=proposal_text,
                generation_time=datetime.utcnow(),
            )
            
        except Exception as e:
            processing_time = time.time() - start_time
            logger.error(
                f"Error generating proposal: {str(e)}",
                extra={
                    "generation_id": generation_id,
                    "error": str(e),
                    "error_type": type(e).__name__,
                    "processing_time_seconds": processing_time,
                },
                exc_info=True
            )
            raise ProposalGenerationError(f"Failed to generate proposal: {str(e)}")


# Singleton instance for reuse
default_generator: Optional[ProposalGenerator] = None


def get_proposal_generator() -> ProposalGenerator:
    """
    Get or create the proposal generator singleton.
    
    This function is suitable for FastAPI dependency injection.
    
    Returns:
        A ProposalGenerator instance
    """
    global default_generator
    if default_generator is None:
        logger.info("Creating new ProposalGenerator instance")
        default_generator = ProposalGenerator()
    return default_generator


async def generate_proposal(input_data: ProposalGeneratorInput) -> ProposalGeneratorOutput:
    """
    Generate a proposal using the default generator.
    
    Args:
        input_data: The proposal generation input data
        
    Returns:
        A ProposalGeneratorOutput with the generated proposal text and timestamp
    """
    logger.info("Generating proposal with default generator")
    generator = get_proposal_generator()
    return await generator.generate_proposal(input_data) 