// Popup script for the Upwork Proposal Generator extension

// API URL
const API_BASE_URL = 'http://localhost:8000/api/v1';

// Check auth status when the popup is opened
document.addEventListener('DOMContentLoaded', async () => {
  await checkAuthStatus();
  await checkCurrentPage();
});

// Function to check if the user is authenticated
async function checkAuthStatus() {
  try {
    // Get stored token
    const authData = await chrome.storage.local.get(['authToken', 'userEmail']);
    const hasAuth = authData.authToken && authData.userEmail;
    
    // Get DOM elements
    const authStatus = document.getElementById('auth-status');
    const loginForm = document.getElementById('login-form');
    const loggedInActions = document.getElementById('logged-in-actions');
    
    if (hasAuth) {
      // User is logged in
      authStatus.textContent = `Logged in as ${authData.userEmail}`;
      authStatus.classList.remove('logged-out');
      authStatus.classList.add('logged-in');
      
      // Show logged in actions, hide login form
      loginForm.classList.add('hidden');
      loggedInActions.classList.remove('hidden');
    } else {
      // User is not logged in
      authStatus.textContent = 'Not logged in';
      authStatus.classList.remove('logged-in');
      authStatus.classList.add('logged-out');
      
      // Show login form, hide logged in actions
      loginForm.classList.remove('hidden');
      loggedInActions.classList.add('hidden');
    }
    
    // Add event listeners for login/logout
    setupAuthEventListeners();
    
  } catch (error) {
    console.error('Error checking auth status:', error);
  }
}

// Set up event listeners for login and logout
function setupAuthEventListeners() {
  // Login button
  const loginButton = document.getElementById('login-button');
  if (loginButton) {
    loginButton.addEventListener('click', handleLogin);
  }
  
  // Logout button
  const logoutButton = document.getElementById('logout-button');
  if (logoutButton) {
    logoutButton.addEventListener('click', handleLogout);
  }
}

// Handle login form submission
async function handleLogin() {
  try {
    // Get login form data
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    
    // Validate form
    if (!email || !password) {
      showLoginError('Please enter both email and password');
      return;
    }
    
    // Show loading state
    const loginButton = document.getElementById('login-button');
    loginButton.textContent = 'Logging in...';
    loginButton.disabled = true;
    
    // Make login request to backend
    const response = await fetch(`${API_BASE_URL}/login/access-token`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: new URLSearchParams({
        username: email,
        password: password,
      }),
    });
    
    // Handle response
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || 'Login failed');
    }
    
    // Parse response data
    const authData = await response.json();
    
    // Store auth token and user email
    await chrome.storage.local.set({
      authToken: authData.access_token,
      userEmail: email,
    });
    
    // Also store the token in the background script for API requests
    chrome.runtime.sendMessage({ 
      action: 'setAuthToken', 
      token: authData.access_token 
    });
    
    // Update UI
    await checkAuthStatus();
    
    // Reset form
    document.getElementById('email').value = '';
    document.getElementById('password').value = '';
    
  } catch (error) {
    console.error('Login error:', error);
    showLoginError(error.message || 'Login failed');
    
  } finally {
    // Reset button state
    const loginButton = document.getElementById('login-button');
    loginButton.textContent = 'Log In';
    loginButton.disabled = false;
  }
}

// Handle logout
async function handleLogout() {
  try {
    // Clear stored auth data
    await chrome.storage.local.remove(['authToken', 'userEmail']);
    
    // Notify background script
    chrome.runtime.sendMessage({ action: 'clearAuthToken' });
    
    // Update UI
    await checkAuthStatus();
    
  } catch (error) {
    console.error('Logout error:', error);
  }
}

// Show login error message
function showLoginError(message) {
  const errorElement = document.getElementById('login-error');
  errorElement.textContent = message;
  errorElement.classList.remove('hidden');
  
  // Hide error after 5 seconds
  setTimeout(() => {
    errorElement.classList.add('hidden');
  }, 5000);
}

// Function to check if the current tab is an Upwork job application page
async function checkCurrentPage() {
  try {
    // Get the active tab
    const tabs = await chrome.tabs.query({ active: true, currentWindow: true });
    const currentTab = tabs[0];

    // Get the status element
    const statusElement = document.getElementById('status');
    
    // Check if URL matches an Upwork job application page
    if (currentTab.url && currentTab.url.match(/upwork\.com\/nx\/proposals\/job\/.*\/apply/)) {
      statusElement.textContent = 'Active on this page';
      statusElement.classList.add('active');
      statusElement.classList.remove('inactive');
    } else {
      statusElement.textContent = 'Not on an Upwork job application page';
      statusElement.classList.add('inactive');
      statusElement.classList.remove('active');
    }
  } catch (error) {
    console.error('Error checking current page:', error);
    
    // Update status with error
    const statusElement = document.getElementById('status');
    statusElement.textContent = 'Error checking page status';
    statusElement.classList.add('inactive');
    statusElement.classList.remove('active');
  }
} 