// Content script for the Upwork Proposal Generator

// Run when the page loads
document.addEventListener('DOMContentLoaded', () => {
  console.log("Upwork Proposal Generator: DOM loaded");
  // Try to add the button immediately
  addProposalButton();
  
  // Set up a mutation observer to detect when the textarea appears
  setupMutationObserver();
});

// Listen for messages from the background script
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  console.log("Upwork Proposal Generator: Message received", message);
  
  if (message.action === "enableProposalGenerator") {
    // Add the proposal generator button to the page
    console.log("Upwork Proposal Generator: Enabling proposal generator");
    addProposalButton();
    // Also set up the mutation observer in case the textarea isn't loaded yet
    setupMutationObserver();
  }
  
  if (message.action === "generateProposal") {
    // Parse job information and send to the API
    generateProposal();
  }
  
  // Return true to indicate we'll send a response asynchronously
  return true;
});

// Function to set up a mutation observer to watch for changes in the DOM
function setupMutationObserver() {
  console.log("Upwork Proposal Generator: Setting up mutation observer");
  
  const observer = new MutationObserver((mutations) => {
    // Check if our button exists yet
    if (!document.getElementById('generate-proposal-btn')) {
      console.log("Upwork Proposal Generator: DOM changed, checking for textarea");
      addProposalButton();
    }
  });
  
  // Start observing the document with the configured parameters
  observer.observe(document.body, { childList: true, subtree: true });
  
  // Disconnect after 10 seconds to avoid unnecessary overhead
  setTimeout(() => {
    console.log("Upwork Proposal Generator: Disconnecting observer after timeout");
    observer.disconnect();
  }, 10000);
}

// Function to add the proposal generator button
function addProposalButton() {
  // Check if button already exists
  if (document.getElementById('generate-proposal-btn')) {
    console.log("Upwork Proposal Generator: Button already exists");
    return;
  }

  console.log("Upwork Proposal Generator: Looking for textarea");
  
  // Try multiple selectors to find the cover letter textarea
  let coverLetterTextarea = document.querySelector('textarea[aria-labelledby="cover_letter_label"]');
  
  if (!coverLetterTextarea) {
    // Try alternative selectors
    coverLetterTextarea = document.querySelector('.air3-textarea .inner-textarea');
  }
  
  if (!coverLetterTextarea) {
    // Try another alternative
    coverLetterTextarea = document.querySelector('textarea.inner-textarea');
  }
  
  if (!coverLetterTextarea) {
    // Try a more specific selector matching the structure in example.html
    const textareaWrappers = document.querySelectorAll('.air3-textarea.textarea-wrapper');
    for (const wrapper of textareaWrappers) {
      const textarea = wrapper.querySelector('textarea');
      if (textarea) {
        coverLetterTextarea = textarea;
        break;
      }
    }
  }
  
  if (!coverLetterTextarea) {
    // Try a broader selector
    const textareas = document.querySelectorAll('textarea');
    for (const textarea of textareas) {
      if (textarea.placeholder === '' || 
          textarea.parentElement.querySelector('label')?.textContent.toLowerCase().includes('cover letter')) {
        coverLetterTextarea = textarea;
        break;
      }
    }
  }
  
  if (coverLetterTextarea) {
    console.log("Upwork Proposal Generator: Found textarea, adding button");
    
    // Create the button
    const button = document.createElement('button');
    button.id = 'generate-proposal-btn';
    button.className = 'upg-button';
    button.textContent = 'Write Proposal';
    button.style.marginBottom = '12px';
    button.style.marginTop = '8px';
    button.style.display = 'block';
    
    // Add event listener for button click
    button.addEventListener('click', (e) => {
      e.preventDefault();
      console.log("Upwork Proposal Generator: Button clicked");
      generateProposal();
    });
    
    // Insert button before the textarea
    coverLetterTextarea.parentNode.insertBefore(button, coverLetterTextarea);
    console.log("Upwork Proposal Generator: Button added");
  } else {
    console.log("Upwork Proposal Generator: Textarea not found");
  }
}

// Function to parse job details from the page
function parseJobDetails() {
  const jobDetails = {
    job_title: '',
    job_description: '',
    skills: []
  };

  // Parse job title
  const titleElement = document.querySelector('.air3-card-section h3');
  if (titleElement) {
    jobDetails.job_title = titleElement.textContent.trim();
  }

  // Parse job description
  const descriptionElement = document.querySelector('.air3-truncation');
  if (descriptionElement) {
    jobDetails.job_description = descriptionElement.textContent.trim();
  }

  // Parse skills
  const skillElements = document.querySelectorAll('.air3-token');
  if (skillElements.length > 0) {
    skillElements.forEach(skill => {
      const skillText = skill.textContent.trim();
      if (skillText) {
        jobDetails.skills.push(skillText);
      }
    });
  }

  console.log("Upwork Proposal Generator: Parsed job details", jobDetails);
  return jobDetails;
}

// Function to generate the proposal
async function generateProposal() {
  try {
    // Get the job details from the page
    const jobDetails = parseJobDetails();
    
    // Show loading state
    const button = document.getElementById('generate-proposal-btn');
    if (button) {
      button.textContent = 'Generating...';
      button.disabled = true;
    }
    
    console.log("Upwork Proposal Generator: Sending request to API", jobDetails);
    
    // Instead of making the request directly from the content script,
    // send a message to the background script to make the request
    const response = await new Promise((resolve, reject) => {
      chrome.runtime.sendMessage(
        { 
          action: "makeApiRequest", 
          data: jobDetails 
        },
        (response) => {
          if (chrome.runtime.lastError) {
            reject(new Error(chrome.runtime.lastError.message));
          } else if (!response.success) {
            reject(new Error(response.error));
          } else {
            resolve(response.data);
          }
        }
      );
    });
    
    console.log("Upwork Proposal Generator: Received API response", response);
    
    // Find the cover letter textarea again (in case the DOM has changed)
    let coverLetterTextarea = document.querySelector('textarea[aria-labelledby="cover_letter_label"]');
    
    if (!coverLetterTextarea) {
      coverLetterTextarea = document.querySelector('.air3-textarea .inner-textarea');
    }
    
    if (!coverLetterTextarea) {
      coverLetterTextarea = document.querySelector('textarea.inner-textarea');
    }
    
    if (!coverLetterTextarea) {
      // Try a more specific selector matching the structure in example.html
      const textareaWrappers = document.querySelectorAll('.air3-textarea.textarea-wrapper');
      for (const wrapper of textareaWrappers) {
        const textarea = wrapper.querySelector('textarea');
        if (textarea) {
          coverLetterTextarea = textarea;
          break;
        }
      }
    }
    
    if (coverLetterTextarea && response.proposal_text) {
      coverLetterTextarea.value = response.proposal_text;
      
      // Trigger input event to ensure Upwork's form validation recognizes the change
      const inputEvent = new Event('input', { bubbles: true });
      coverLetterTextarea.dispatchEvent(inputEvent);
      
      console.log("Upwork Proposal Generator: Filled textarea with proposal");
    } else {
      console.error("Upwork Proposal Generator: Could not find textarea to fill", { 
        textareaFound: !!coverLetterTextarea, 
        proposalTextExists: !!response.proposal_text 
      });
    }
    
    // Reset button state
    if (button) {
      button.textContent = 'Write Proposal';
      button.disabled = false;
    }
  } catch (error) {
    console.error('Error generating proposal:', error);
    
    // Reset button state and show error
    const button = document.getElementById('generate-proposal-btn');
    if (button) {
      button.textContent = 'Error - Try Again';
      button.disabled = false;
    }
    
    // Display error to user
    const errorMessage = document.createElement('div');
    errorMessage.className = 'upg-error';
    errorMessage.textContent = `Error: ${error.message || 'Could not generate proposal. Check console for details.'}`;
    
    if (button && button.parentNode) {
      button.parentNode.insertBefore(errorMessage, button.nextSibling);
      
      // Remove error message after 5 seconds
      setTimeout(() => {
        if (errorMessage.parentNode) {
          errorMessage.parentNode.removeChild(errorMessage);
        }
      }, 5000);
    }
  }
} 