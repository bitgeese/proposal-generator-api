#!/bin/bash
# Script to test the proposal generation API using curl

set -e

# Configuration
API_URL=${API_URL:-"http://localhost:8000/api/v1"}
AUTH_ENDPOINT="${API_URL}/login/access-token"
PROPOSAL_ENDPOINT="${API_URL}/proposals/generate"

# Default credentials - replace with your actual credentials
USERNAME=${USERNAME:-"admin@example.com"}
PASSWORD=${PASSWORD:-"admin"}

echo "🔑 Getting authentication token..."
AUTH_RESPONSE=$(curl -s -X POST \
  "${AUTH_ENDPOINT}" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=${USERNAME}&password=${PASSWORD}")

# Extract token and handle error
if [[ "$AUTH_RESPONSE" == *"access_token"* ]]; then
  TOKEN=$(echo $AUTH_RESPONSE | sed 's/.*"access_token":"\([^"]*\)".*/\1/')
  echo "✅ Authentication successful"
else
  echo "❌ Authentication failed: $AUTH_RESPONSE"
  exit 1
fi

echo "🚀 Testing proposal generation API..."

# Test job data
read -r -d '' JOB_DATA << EOM
{
  "job_title": "Python Developer needed for web scraping project",
  "job_description": "We need a developer to build a robust web scraper that can extract data from multiple e-commerce websites. The ideal candidate should have experience with Python, BeautifulSoup or Scrapy, and handling anti-scraping measures. Our project requires daily data collection from various product pages, including prices, availability, and specifications.",
  "skills": ["Python", "BeautifulSoup", "Scrapy", "Data Processing"],
  "additional_context": "I have 5 years of experience building web scrapers for various industries including e-commerce, real estate, and financial services. I'm familiar with handling anti-bot measures and implementing proper rate limiting."
}
EOM

echo "📝 Job Data:"
echo "$JOB_DATA" | jq '.'

echo
echo "⏱️  Sending request to generate proposal (this may take 10-30 seconds)..."
echo

start_time=$(date +%s)

# Make the actual API call
RESPONSE=$(curl -s -X POST "${PROPOSAL_ENDPOINT}" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${TOKEN}" \
  -d "$JOB_DATA")

end_time=$(date +%s)
duration=$((end_time - start_time))

# Check if response is JSON and contains proposal_text
if [[ "$RESPONSE" == *"proposal_text"* ]]; then
  echo "✅ Proposal generated successfully in ${duration} seconds!"
  echo
  echo "📋 Generated Proposal:"
  echo "-------------------------------------------"
  echo "$RESPONSE" | jq -r '.proposal_text'
  echo "-------------------------------------------"
  echo
  echo "⏱️  Generation time: $(echo "$RESPONSE" | jq -r '.generation_time')"
else
  echo "❌ Error generating proposal: $RESPONSE"
  exit 1
fi

echo "✅ Test completed successfully" 