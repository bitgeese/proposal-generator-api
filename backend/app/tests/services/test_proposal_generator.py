"""Tests for the proposal generator service."""

import pytest
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

from app.models import ProposalGeneratorInput
from app.services.proposal_generator import (
    ProposalGenerator,
    ProposalGenerationError,
    get_proposal_generator,
    generate_proposal,
)


class TestProposalGenerator:
    """Tests for the ProposalGenerator service."""

    @patch("app.services.proposal_generator.ChatAnthropic")
    @patch("app.services.proposal_generator.PromptTemplate")
    @patch("app.services.proposal_generator.LLMChain")
    def test_init_with_claude_model(self, mock_llm_chain, mock_prompt_template, mock_chat_anthropic, monkeypatch):
        """Test initialization with Claude model."""
        # Set environment variables
        monkeypatch.setattr("app.services.proposal_generator.settings.ANTHROPIC_API_KEY", "test-key")
        monkeypatch.setattr("app.services.proposal_generator.settings.DEFAULT_LLM_MODEL", "claude-3-haiku")
        
        # Create mock instances
        mock_chat_anthropic.return_value = "mock_llm"
        mock_prompt_template.return_value = "mock_prompt"
        mock_llm_chain.return_value = "mock_chain"
        
        # Create generator
        generator = ProposalGenerator()
        
        # Check if correct LLM was instantiated
        mock_chat_anthropic.assert_called_once()
        assert generator.model_name == "claude-3-haiku"
        
        # Check if chain was set up
        mock_prompt_template.assert_called_once()
        mock_llm_chain.assert_called_once()

    @patch("app.services.proposal_generator.ChatOpenAI")
    @patch("app.services.proposal_generator.PromptTemplate")
    @patch("app.services.proposal_generator.LLMChain")
    def test_init_with_openai_model(self, mock_llm_chain, mock_prompt_template, mock_chat_openai, monkeypatch):
        """Test initialization with OpenAI model."""
        # Set environment variables
        monkeypatch.setattr("app.services.proposal_generator.settings.OPENAI_API_KEY", "test-key")
        monkeypatch.setattr("app.services.proposal_generator.settings.DEFAULT_LLM_MODEL", "gpt-4")
        
        # Create mock instances
        mock_chat_openai.return_value = "mock_llm"
        mock_prompt_template.return_value = "mock_prompt"
        mock_llm_chain.return_value = "mock_chain"
        
        # Create generator
        generator = ProposalGenerator()
        
        # Check if correct LLM was instantiated
        mock_chat_openai.assert_called_once()
        assert generator.model_name == "gpt-4"
        
        # Check if chain was set up
        mock_prompt_template.assert_called_once()
        mock_llm_chain.assert_called_once()

    @pytest.mark.asyncio
    @patch("app.services.proposal_generator.ChatAnthropic")
    @patch("app.services.proposal_generator.PromptTemplate")
    @patch("app.services.proposal_generator.LLMChain")
    async def test_generate_proposal(self, mock_llm_chain, mock_prompt_template, mock_chat_anthropic, 
                                    mock_chain, proposal_input_with_context, monkeypatch):
        """Test proposal generation."""
        # Set environment variables to avoid API key error
        monkeypatch.setattr("app.services.proposal_generator.settings.ANTHROPIC_API_KEY", "test-key")
        
        # Create mock instances
        mock_chat_anthropic.return_value = "mock_llm"
        mock_prompt_template.return_value = "mock_prompt"
        mock_llm_chain.return_value = mock_chain
        
        # Create generator
        generator = ProposalGenerator()
        
        # Generate proposal
        result = await generator.generate_proposal(proposal_input_with_context)
        
        # Check if chain was called with correct parameters
        mock_chain.ainvoke.assert_called_once()
        call_args = mock_chain.ainvoke.call_args[0][0]
        assert call_args["job_title"] == "Python Developer"
        assert call_args["job_description"] == "Looking for a Python developer for a web scraping project"
        assert call_args["skills"] == "Python, Scrapy, FastAPI"
        assert "5 years of experience" in call_args["additional_context_prompt"]
        
        # Check result
        assert result.proposal_text == "This is a generated proposal."
        assert isinstance(result.generation_time, datetime)

    @pytest.mark.asyncio
    @patch("app.services.proposal_generator.ChatAnthropic")
    async def test_generate_proposal_error(self, mock_chat_anthropic, mock_chain, proposal_input, monkeypatch):
        """Test error handling during proposal generation."""
        # Set environment variables to avoid API key error
        monkeypatch.setattr("app.services.proposal_generator.settings.ANTHROPIC_API_KEY", "test-key")
        
        # Create generator with mocked dependencies
        with patch("app.services.proposal_generator.PromptTemplate"):
            with patch("app.services.proposal_generator.LLMChain", return_value=mock_chain):
                generator = ProposalGenerator()
                generator.chain = mock_chain
                generator.chain.ainvoke.side_effect = Exception("Test error")
                
                # Generate proposal should raise an exception
                with pytest.raises(ProposalGenerationError):
                    await generator.generate_proposal(proposal_input)

    @patch("app.services.proposal_generator.ProposalGenerator")
    def test_get_proposal_generator(self, mock_generator_class):
        """Test singleton pattern of get_proposal_generator."""
        # Reset the singleton first to ensure test isolation
        import app.services.proposal_generator
        app.services.proposal_generator.default_generator = None
        
        # Set up mock
        mock_generator_class.return_value = "mock_generator_instance"
        
        # Get generator - should create a new one
        result1 = get_proposal_generator()
        assert result1 == "mock_generator_instance"
        mock_generator_class.assert_called_once()
        
        # Get generator again - should reuse the existing one
        mock_generator_class.reset_mock()
        result2 = get_proposal_generator()
        assert result2 == result1
        mock_generator_class.assert_not_called()

    @pytest.mark.asyncio
    @patch("app.services.proposal_generator.get_proposal_generator")
    async def test_generate_proposal_helper(self, mock_get_generator, proposal_input):
        """Test the generate_proposal helper function."""
        # Set up mock
        mock_generator = MagicMock()
        mock_generator.generate_proposal = AsyncMock(return_value="mock_result")
        mock_get_generator.return_value = mock_generator
        
        # Call helper function
        result = await generate_proposal(proposal_input)
        
        # Check if the generator was called correctly
        mock_get_generator.assert_called_once()
        mock_generator.generate_proposal.assert_called_once_with(proposal_input)
        assert result == "mock_result" 