# Automated Test Credentials

This document provides comprehensive instructions for setting up and maintaining Gmail API testing credentials without manual refresh token management.

## Table of Contents

1. [Quick Start Guide](#quick-start-guide)
2. [Detailed Setup Instructions](#detailed-setup-instructions)
3. [Maintenance & Troubleshooting](#maintenance--troubleshooting)
4. [Strategy Comparison](#strategy-comparison)
5. [Advanced Configuration](#advanced-configuration)

## Quick Start Guide

### For New Developers (Recommended)

```bash
# 1. Set up mock credentials (no real Gmail API access needed)
python backend/scripts/setup_test_credentials.py mock

# 2. Run tests
python -m pytest backend/tests/
```

### For Integration Testing (Real Gmail API)

```bash
# 1. Set up environment tokens (one-time setup)
python backend/scripts/setup_test_credentials.py environment

# 2. Follow the detailed setup instructions below
# 3. Run tests
python -m pytest backend/tests/
```

## Detailed Setup Instructions

### Prerequisites

1. **Google Cloud Project** with OAuth 2.0 credentials
2. **Test Gmail Account** (e.g., `emailagenttester@gmail.com`)
3. **Backend environment** with Python dependencies installed

### Step 1: Google Cloud Console Setup

#### 1.1 Create/Configure OAuth 2.0 Client

1. Go to [Google Cloud Console - Credentials](https://console.cloud.google.com/apis/credentials)
2. Select your project or create a new one
3. Click **"Create Credentials"** → **"OAuth 2.0 Client IDs"**
4. Configure the OAuth client:
   - **Application type**: Web application
   - **Name**: Email Agent Test Client
   - **Authorized redirect URIs**: 
     - `http://localhost:8000/auth/callback` (for local development)
     - `https://developers.google.com/oauthplayground` (for token generation)

#### 1.2 Enable Gmail API

1. Go to [Google Cloud Console - APIs](https://console.cloud.google.com/apis)
2. Search for **"Gmail API"**
3. Click **"Enable"**
4. Wait 1-5 minutes for the change to propagate

#### 1.3 Configure OAuth Consent Screen

1. Go to [OAuth Consent Screen](https://console.cloud.google.com/apis/credentials/consent)
2. Configure the consent screen:
   - **User Type**: External (for testing)
   - **App name**: Email Agent Test
   - **User support email**: Your email
   - **Developer contact information**: Your email
3. Add scopes:
   - `https://www.googleapis.com/auth/gmail.readonly`
   - `https://www.googleapis.com/auth/gmail.modify`
4. Add test users:
   - Add your test Gmail account (e.g., `emailagenttester@gmail.com`)
5. **Publish** the consent screen (even in testing mode)

### Step 2: Generate Refresh Token

#### Option A: Using OAuth Playground (Recommended)

1. Go to [Google OAuth 2.0 Playground](https://developers.google.com/oauthplayground/)
2. Click the **settings icon** (⚙️) in the top right
3. Check **"Use your own OAuth credentials"**
4. Enter your OAuth client details:
   - **OAuth Client ID**: `YOUR_CLIENT_ID_HERE`
   - **OAuth Client Secret**: `YOUR_CLIENT_SECRET_HERE`
5. Click **"Close"**
6. In the left panel, scroll to **"Gmail API v1"**
7. Select:
   - `https://www.googleapis.com/auth/gmail.readonly`
   - `https://www.googleapis.com/auth/gmail.modify`
8. Click **"Authorize APIs"**
9. Sign in with your test Gmail account (`emailagenttester@gmail.com`)
10. Click **"Exchange authorization code for tokens"**
11. Copy the **Refresh token** (not the access token)

#### Option B: Using Your Application

1. Start your backend server: `uvicorn app.main:app --reload`
2. Visit: `http://localhost:8000/auth/login`
3. Sign in with your test Gmail account
4. Check the logs for the refresh token or use the callback endpoint

### Step 3: Configure Environment Variables

1. Open `backend/.env.test`
2. Update with your credentials:

```env
# Google OAuth Configuration
GOOGLE_CLIENT_ID=YOUR_CLIENT_ID_HERE
GOOGLE_CLIENT_SECRET=YOUR_CLIENT_SECRET_HERE
GOOGLE_REFRESH_TOKEN=YOUR_REFRESH_TOKEN_HERE
GOOGLE_ACCESS_TOKEN=  # Leave empty, will be generated automatically

# Test Gmail Account
TEST_GMAIL=emailagenttester@gmail.com
```

### Step 4: Verify Setup

```bash
# Run the Gmail integration tests
python -m pytest tests/test_gmail_integration.py::TestGmailAPIIntegration::test_gmail_api_connection_and_auth -v

# Run all tests
python -m pytest tests/ -v
```

## Maintenance & Troubleshooting

### When Refresh Tokens Expire

Refresh tokens can expire for several reasons:
- **Inactivity**: Not used for 6+ months
- **Security**: Google revoked due to suspicious activity
- **Scope changes**: OAuth consent screen scopes were modified
- **User action**: User revoked access

#### Symptoms of Expired Refresh Token

```bash
# Error messages you might see:
# - "invalid_grant"
# - "Token has been expired or revoked"
# - "401 Unauthorized"
```

#### How to Fix Expired Refresh Tokens

1. **Regenerate the refresh token** using the same process as Step 2 above
2. **Update your `.env.test`** with the new refresh token
3. **Re-run tests** to verify the fix

```bash
# Quick verification
python -m pytest tests/test_gmail_integration.py::TestGmailAPIIntegration::test_gmail_api_connection_and_auth -v
```

### Common Issues & Solutions

#### Issue: "Gmail API has not been used in project before or it is disabled"

**Solution**: Enable the Gmail API in Google Cloud Console
1. Go to [Gmail API Console](https://console.developers.google.com/apis/api/gmail.googleapis.com/overview)
2. Click **"Enable"**
3. Wait 1-5 minutes for propagation

#### Issue: "redirect_uri_mismatch"

**Solution**: Add the redirect URI to your OAuth client
1. Go to [Google Cloud Console - Credentials](https://console.cloud.google.com/apis/credentials)
2. Edit your OAuth 2.0 Client ID
3. Add the missing redirect URI to "Authorized redirect URIs"

#### Issue: "Access blocked: This app hasn't been verified"

**Solution**: Add test users to OAuth consent screen
1. Go to [OAuth Consent Screen](https://console.cloud.google.com/apis/credentials/consent)
2. Add your test Gmail account as a test user
3. Make sure the consent screen is published

#### Issue: "KeyError: 'token'"

**Solution**: Ensure `.env.test` has all required fields
```env
GOOGLE_ACCESS_TOKEN=  # Can be empty, but must be present
```

### Regular Maintenance Schedule

| Task | Frequency | Description |
|------|-----------|-------------|
| Test token validity | Weekly | Run integration tests to verify tokens work |
| Check API quotas | Monthly | Monitor Gmail API usage in Google Cloud Console |
| Update test users | As needed | Add new test users to OAuth consent screen |
| Review scopes | Quarterly | Ensure OAuth scopes match application needs |

## Strategy Comparison

| Strategy | Setup Time | Maintenance | Real API Access | Best For |
|----------|------------|-------------|-----------------|----------|
| **Mock** | 0 minutes | None | ❌ | Unit tests, development |
| **Environment** | 15 minutes | Monthly | ✅ | Integration tests, CI/CD |
| **Service Account** | 30 minutes | None | ✅ | Enterprise, production testing |

### When to Use Each Strategy

#### Mock Strategy
- **Use when**: Writing unit tests, developing features
- **Pros**: No setup required, fast execution
- **Cons**: No real API validation

#### Environment Strategy
- **Use when**: Testing Gmail integration, CI/CD pipelines
- **Pros**: Real API access, reliable
- **Cons**: Manual token management

#### Service Account Strategy
- **Use when**: Enterprise environments, automated testing
- **Pros**: Fully automated, no token management
- **Cons**: Complex setup, requires domain admin

## Advanced Configuration

### Custom Test Scenarios

```python
# Example: Test with specific Gmail labels
def test_sync_specific_labels(self, test_user_with_credentials):
    user = test_user_with_credentials
    # Test sync with specific label filters
    result = await sync_emails_since_last_fetch(
        db, user, label_ids=['INBOX', 'IMPORTANT']
    )
    assert result['status'] == 'success'
```

### CI/CD Integration

```yaml
# Example GitHub Actions workflow
name: Test Gmail Integration
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.10
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run tests
        env:
          GOOGLE_CLIENT_ID: ${{ secrets.GOOGLE_CLIENT_ID }}
          GOOGLE_CLIENT_SECRET: ${{ secrets.GOOGLE_CLIENT_SECRET }}
          GOOGLE_REFRESH_TOKEN: ${{ secrets.GOOGLE_REFRESH_TOKEN }}
        run: python -m pytest tests/
```

### Environment-Specific Configuration

```bash
# Development
cp backend/.env.test backend/.env.dev

# Staging
cp backend/.env.test backend/.env.staging

# Production (use service accounts)
cp backend/.env.test backend/.env.prod
```

## Security Best Practices

1. **Never commit tokens to version control**
   - Use `.env.test` (already in `.gitignore`)
   - Use environment variables in CI/CD

2. **Rotate tokens regularly**
   - Refresh tokens every 6 months
   - Monitor for suspicious activity

3. **Limit test account permissions**
   - Use dedicated test Gmail accounts
   - Don't use personal accounts for testing

4. **Monitor API usage**
   - Check Google Cloud Console quotas
   - Set up alerts for unusual usage

## Support & Troubleshooting

### Getting Help

1. **Check logs**: `tail -f backend/logs/email_agent.log`
2. **Run tests with verbose output**: `python -m pytest -v -s`
3. **Check Google Cloud Console**: Monitor API usage and errors
4. **Review this documentation**: Most issues are covered above

### Useful Commands

```bash
# Test Gmail API connection only
python -m pytest tests/test_gmail_integration.py::TestGmailAPIIntegration::test_gmail_api_connection_and_auth -v

# Test email sync functionality
python -m pytest tests/test_gmail_integration.py::TestEmailSyncIntegration -v

# Run all tests with coverage
python -m pytest tests/ --cov=app --cov-report=html

# Check environment variables
python -c "import os; from dotenv import load_dotenv; load_dotenv('.env.test'); print('GOOGLE_CLIENT_ID:', os.getenv('GOOGLE_CLIENT_ID')); print('GOOGLE_REFRESH_TOKEN:', 'SET' if os.getenv('GOOGLE_REFRESH_TOKEN') else 'NOT SET')"
```

---

**Last Updated**: December 2024  
**Maintainer**: Development Team  
**Version**: 2.0 