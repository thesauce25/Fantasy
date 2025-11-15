# Quick Start Guide

Get your Fantasy Football Chatbot running in 5 minutes!

## Prerequisites

- Python 3.8 or higher
- A Yahoo Fantasy Football account with an active league
- An internet connection

## Installation Steps

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run Setup Script (Recommended)

The easiest way to get started:

```bash
python setup.py
```

This interactive script will guide you through:
- Creating a Yahoo Developer App
- Configuring your API credentials
- Setting up your league ID
- Getting an Anthropic API key
- Testing your configuration

### 3. Manual Setup (Alternative)

If you prefer manual setup:

1. **Copy the environment template:**
   ```bash
   cp .env.example .env
   ```

2. **Get Yahoo API Credentials:**
   - Go to https://developer.yahoo.com/apps/create/
   - Create an app with Fantasy Sports permissions
   - Copy your Client ID and Client Secret to `.env`

3. **Get Your League ID:**
   - Visit your Yahoo Fantasy Football league
   - Copy the league ID from the URL (the number after `/f1/`)
   - Add it to `.env` as `YAHOO_LEAGUE_ID`

4. **Get Anthropic API Key:**
   - Visit https://console.anthropic.com/
   - Create an API key
   - Add it to `.env` as `ANTHROPIC_API_KEY`

### 4. Run the Chatbot

```bash
python chatbot.py
```

On first run, you'll be prompted to authorize the app with Yahoo. Follow the OAuth flow in your browser.

## Usage Examples

Once running, try asking:

- "Who should I start this week?"
- "Show me the best available players"
- "Should I trade [Player A] for [Player B]?"
- "What are my team's weaknesses?"
- "Analyze my matchup this week"

## Commands

While in the chatbot:
- `refresh` - Reload your team data from Yahoo
- `help` - Show available commands
- `quit` or `exit` - Exit the chatbot

## Troubleshooting

### OAuth Token Expired
If you see authentication errors, delete `private.json` and restart the chatbot.

### League Not Found
Make sure your `YAHOO_LEAGUE_ID` in `.env` matches your actual league ID from the Yahoo URL.

### API Rate Limits
Yahoo limits API calls. If you hit limits, wait a few minutes before trying again.

## Need More Help?

See the full [README.md](README.md) for detailed documentation.

## What's Next?

Once you're comfortable with the chatbot, you can:
- Customize the AI prompts in `chatbot.py`
- Add new commands or features
- Integrate with other fantasy platforms
- Share your improvements via pull requests!

Enjoy your fantasy football season! 🏈
