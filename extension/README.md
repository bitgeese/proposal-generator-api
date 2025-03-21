# Upwork Proposal Generator Extension

A Chrome extension that helps generate professional proposals for Upwork job applications. The extension parses job information and uses an AI backend to create tailored proposals.

## Features

- Automatically detects Upwork job application pages
- Parses job title, description, and required skills
- Sends job data to a backend API for proposal generation
- Automatically fills in the proposal text area with the generated content

## Installation

### Development Mode

1. Clone this repository
2. Open Chrome and navigate to `chrome://extensions/`
3. Enable "Developer mode" (toggle in the top-right corner)
4. Click "Load unpacked" and select the `extension` directory from this repository

### Prerequisites

- The backend API server must be running at `http://localhost:8000`

## Usage

1. Navigate to an Upwork job application page (`upwork.com/nx/proposals/job/*/apply/`)
2. Look for the "Write Proposal" button that appears above the cover letter textarea
3. Click the button to generate a proposal based on the job details
4. The generated proposal will automatically fill the cover letter textarea

## Development

### File Structure

- `manifest.json` - Extension configuration
- `popup.html` - Extension popup interface
- `js/background.js` - Background service worker script
- `js/content.js` - Content script for interacting with Upwork pages
- `js/popup.js` - Script for the extension popup
- `css/content.css` - Styles for the content script
- `images/` - Extension icons

### Backend API

The extension communicates with a backend API to generate proposals. The API endpoint is:

```
POST http://localhost:8000/api/v1/proposals/generate
```

The request body includes:

```json
{
  "title": "Job title",
  "description": "Job description",
  "skills": ["Skill 1", "Skill 2", "..."]
}
```

## Notes

- Replace the placeholder icons in the `images` directory with your own icons
- Make sure the backend API is running before using the extension 