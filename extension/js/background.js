// Background script for the Upwork Proposal Generator extension

console.log("Upwork Proposal Generator: Background script loaded");

// Store auth token in memory
let authToken = null;

// Listen for changes in the active tab
chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
  // Only proceed if the tab has completed loading
  if (changeInfo.status === 'complete' && tab.url) {
    console.log("Upwork Proposal Generator: Tab updated", tab.url);
    
    // Check if the URL matches an Upwork job application page
    if (tab.url.match(/upwork\.com\/nx\/proposals\/job\/.*\/apply/)) {
      console.log("Upwork Proposal Generator: On Upwork job application page");
      
      // Enable the extension action when on an Upwork job application page
      chrome.action.setIcon({
        path: {
          "16": "images/icon16.png",
          "48": "images/icon48.png",
          "128": "images/icon128.png"
        },
        tabId: tabId
      });
      
      // Send a message to the content script to indicate we're on a proposal page
      chrome.tabs.sendMessage(tabId, { action: "enableProposalGenerator" }, (response) => {
        // Log any error that might occur during messaging
        if (chrome.runtime.lastError) {
          console.error("Upwork Proposal Generator: Error sending message", chrome.runtime.lastError);
        } else {
          console.log("Upwork Proposal Generator: Message sent to content script");
        }
      });
    } else {
      console.log("Upwork Proposal Generator: Not on Upwork job application page");
    }
  }
});

// Initialize auth token from storage
chrome.storage.local.get(['authToken'], (result) => {
  if (result.authToken) {
    authToken = result.authToken;
    console.log("Upwork Proposal Generator: Auth token loaded from storage");
  }
});

// Listen for messages from content script or popup
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  // Handle setting auth token
  if (message.action === 'setAuthToken') {
    authToken = message.token;
    console.log("Upwork Proposal Generator: Auth token set");
    sendResponse({ success: true });
    return true;
  }
  
  // Handle clearing auth token
  if (message.action === 'clearAuthToken') {
    authToken = null;
    console.log("Upwork Proposal Generator: Auth token cleared");
    sendResponse({ success: true });
    return true;
  }
  
  // If the message is to generate a proposal
  if (message.action === "makeApiRequest") {
    console.log("Upwork Proposal Generator: Received API request", message.data);
    
    // Check if we have an auth token
    if (!authToken) {
      console.error("Upwork Proposal Generator: No auth token available");
      sendResponse({ 
        success: false, 
        error: "Authentication required. Please log in using the extension popup." 
      });
      return true;
    }
    
    // Make the API request from the background script to avoid CORS issues
    fetch('http://localhost:8000/api/v1/proposals/generate', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${authToken}`,
      },
      body: JSON.stringify(message.data)
    })
    .then(response => {
      if (response.status === 401) {
        // If unauthorized, clear token and prompt user to log in again
        authToken = null;
        chrome.storage.local.remove(['authToken', 'userEmail']);
        throw new Error('Authentication expired. Please log in again.');
      }
      
      if (response.status === 422) {
        // Handle validation errors more gracefully
        return response.json().then(errorData => {
          console.error("Validation error:", errorData);
          const errorMessages = errorData.detail.map(error => 
            `Field '${error.loc.join('.')}' ${error.msg.toLowerCase()}`
          ).join('; ');
          throw new Error(`Validation error: ${errorMessages}`);
        });
      }
      
      if (!response.ok) {
        return response.text().then(text => {
          console.error("API error response:", text);
          try {
            // Try to parse JSON error
            const jsonError = JSON.parse(text);
            const errorMsg = jsonError.detail || text;
            throw new Error(`API error: ${response.status} - ${errorMsg}`);
          } catch (e) {
            // If not JSON, use plain text
            throw new Error(`API error: ${response.status} - ${text}`);
          }
        });
      }
      return response.json();
    })
    .then(data => {
      console.log("Upwork Proposal Generator: API request successful", data);
      // Send the response back to the content script
      sendResponse({ success: true, data: data });
    })
    .catch(error => {
      console.error("Upwork Proposal Generator: API request failed", error);
      // Send error back to the content script
      sendResponse({ success: false, error: error.message });
    });
    
    // Return true to indicate we'll send a response asynchronously
    return true;
  }
});

// Listen for installation or update
chrome.runtime.onInstalled.addListener((details) => {
  console.log("Upwork Proposal Generator: Extension installed or updated", details.reason);
}); 