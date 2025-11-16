# Fantasy Football Chatbot

An AI-powered chatbot that provides personalized fantasy football advice using the Yahoo Fantasy Football API and Claude AI.

## Features

- **Real-time Team Analysis**: Get insights on your current roster, lineup decisions, and player performance
- **Trade Advice**: Analyze potential trades and get AI-powered recommendations
- **Waiver Wire Intelligence**:
  - View top available free agents by position
  - See ownership percentages across Yahoo leagues
  - Track recently dropped players (🔥 indicators)
  - Get personalized pickup/drop recommendations
  - Smart player ranking based on availability and recent activity
- **Matchup Analysis**: Get weekly matchup insights and start/sit recommendations
- **League Insights**: Understand your league standings and competition

## Prerequisites

1. **Yahoo Fantasy Football Account**: You need an active Yahoo Fantasy Football league
2. **Yahoo Developer Account**: Register your app at [Yahoo Developer Network](https://developer.yahoo.com/apps/create/)
3. **Anthropic API Key**: Get your API key from [Anthropic Console](https://console.anthropic.com/)

## Setup Instructions

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd Fantasy
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Set Up Yahoo Developer App

1. Go to [Yahoo Developer Network](https://developer.yahoo.com/apps/create/)
2. Click "Create an App"
3. Fill in the app details:
   - **Application Name**: Fantasy Football Chatbot (or your choice)
   - **Application Type**: Web Application
   - **Homepage URL**: `http://localhost:8000`
   - **Redirect URI(s)**: `http://localhost:8000`
   - **API Permissions**: Select "Fantasy Sports" with Read access
4. Save your **Client ID** and **Client Secret**

### 4. Configure Environment Variables

```bash
cp .env.example .env
```

Edit `.env` and add your credentials:
- `YAHOO_CLIENT_ID`: Your Yahoo app Client ID
- `YAHOO_CLIENT_SECRET`: Your Yahoo app Client Secret
- `ANTHROPIC_API_KEY`: Your Anthropic API key
- `YAHOO_LEAGUE_ID`: Your Yahoo Fantasy league ID (found in your league URL)

### 5. First Time Authentication

Run the chatbot for the first time to authenticate with Yahoo:

```bash
python chatbot.py
```

You'll be prompted to:
1. Visit a Yahoo authorization URL
2. Grant permissions to your app
3. Copy the authorization code back to the terminal

Your OAuth tokens will be saved in `private.json` for future use.

## Usage

Simply run the chatbot:

```bash
python chatbot.py
```

### Example Questions

**Start/Sit Decisions:**
- "Should I start Player X or Player Y this week?"
- "Who should I stream at QB/TE/DEF this week?"

**Waiver Wire:**
- "Who should I pick up from waivers this week?"
- "Give me your top 3 waiver wire pickups with drop recommendations"
- "Who are the best available RBs I should target?"
- "Which players should I drop from my bench?"
- "Should I pick up [Player Name]? Who should I drop?"

**Team Analysis:**
- "Analyze my team's strengths and weaknesses"
- "What's my chances of winning this week?"
- "Show me my current roster"

**Trade Advice:**
- "What trades should I consider?"
- "Should I trade [Player A] for [Player B]?"

Type `quit`, `exit`, or `q` to end the conversation. Type `help` to see available commands.

## Project Structure

```
Fantasy/
├── chatbot.py              # Main chatbot application
├── yahoo_client.py         # Yahoo Fantasy API wrapper
├── requirements.txt        # Python dependencies
├── .env.example           # Environment variables template
├── .gitignore             # Git ignore rules
└── README.md              # This file
```

## How It Works

1. **Data Retrieval**: The chatbot connects to Yahoo Fantasy API to fetch your team, league, and player data
2. **AI Analysis**: Your questions and fantasy data are sent to Claude AI for intelligent analysis
3. **Personalized Advice**: Claude provides contextual advice based on your specific team and league situation

### Waiver Wire Intelligence

The app uses a multi-strategy approach to provide accurate waiver wire information:

1. **Player Data Fetching**: Retrieves available players from Yahoo Fantasy API
2. **Transaction Tracking**: Analyzes recent league transactions to identify:
   - Recently dropped players (marked with 🔥)
   - Recently added players (filtered out as likely unavailable)
3. **Smart Filtering**:
   - Filters by ownership type (waivers, free agents)
   - Validates player data quality
   - Removes injured/suspended players from top recommendations
4. **Intelligent Ranking**:
   - Prioritizes by ownership percentage (higher % = more reliable)
   - Boosts recently dropped players (potential overreactions)
   - Considers injury status and team affiliation

**Note**: The Yahoo Fantasy API has some limitations with player data freshness. The app does its best to filter out stale information, but always cross-reference important decisions with the Yahoo Fantasy website.

## Troubleshooting

### OAuth Token Expired

Yahoo OAuth tokens expire after 1 hour. If you see authentication errors:
1. Delete `private.json`
2. Run the chatbot again to re-authenticate

### League ID Not Found

Find your league ID from your Yahoo Fantasy Football league URL:
- URL format: `https://football.fantasysports.yahoo.com/f1/{LEAGUE_ID}`
- Example: If URL is `https://football.fantasysports.yahoo.com/f1/12345`, your league ID is `12345`

### API Rate Limits

Yahoo has rate limits on API calls. If you hit limits, wait a few minutes before trying again.

## Contributing

Feel free to submit issues or pull requests!

## License

MIT License
