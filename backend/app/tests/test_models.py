import pytest
from datetime import datetime
from pydantic import ValidationError

from app.models import ProposalGeneratorInput, ProposalGeneratorOutput


class TestProposalGeneratorModels:
    
    @pytest.mark.parametrize("input_data,expected", [
        (
            {
                "job_title": "Python Developer needed",
                "job_description": "We need a developer",
                "skills": ["Python", "FastAPI"]
            },
            {"additional_context": None}
        ),
        (
            {
                "job_title": "Python Developer needed",
                "job_description": "We need a developer",
                "skills": ["Python", "FastAPI"],
                "additional_context": "5 years experience"
            },
            {"additional_context": "5 years experience"}
        ),
    ])
    def test_proposal_generator_input_valid(self, input_data, expected):
        """Test that valid ProposalGeneratorInput passes validation."""
        proposal_input = ProposalGeneratorInput(**input_data)
        
        # Check all input fields are set correctly
        for key, value in input_data.items():
            assert getattr(proposal_input, key) == value
        
        # Check expected values not in input
        for key, value in expected.items():
            if key not in input_data:
                assert getattr(proposal_input, key) == value
    
    @pytest.mark.parametrize("invalid_input", [
        # Missing required fields
        {"job_description": "Description", "skills": ["Python"]},  # Missing job_title
        {"job_title": "Title", "skills": ["Python"]},             # Missing job_description
        {"job_title": "Title", "job_description": "Description"}, # Missing skills
        
        # Empty strings
        {"job_title": "", "job_description": "Description", "skills": ["Python"]},
        {"job_title": "Title", "job_description": "", "skills": ["Python"]},
        
        # Empty skills list
        {"job_title": "Title", "job_description": "Description", "skills": []},
    ])
    def test_proposal_generator_input_invalid(self, invalid_input):
        """Test that invalid ProposalGeneratorInput fails validation."""
        with pytest.raises(ValidationError):
            ProposalGeneratorInput(**invalid_input)
    
    def test_proposal_generator_output_valid(self):
        """Test that a valid ProposalGeneratorOutput passes validation."""
        output_data = {
            "proposal_text": "This is a proposal text for the job...",
            "generation_time": "2023-03-19T12:34:56.789Z"
        }
        proposal_output = ProposalGeneratorOutput(**output_data)
        assert proposal_output.proposal_text == output_data["proposal_text"]
        assert proposal_output.generation_time.isoformat().startswith("2023-03-19T12:34:56.789")
    
    def test_proposal_generator_output_empty_text(self):
        """Test that a ProposalGeneratorOutput with empty proposal text fails validation."""
        invalid_output = {
            "proposal_text": "",
            "generation_time": "2023-03-19T12:34:56.789Z"
        }
        
        with pytest.raises(ValidationError):
            ProposalGeneratorOutput(**invalid_output) 