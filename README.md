# Fantasy Football Chatbot

An AI-powered chatbot that provides personalized fantasy football advice using the Yahoo Fantasy Football API and Claude AI.

## Features

- **Real-time Team Analysis**: Get insights on your current roster, lineup decisions, and player performance
- **Comprehensive Player Stats**: Access detailed statistics including passing/rushing/receiving yards, touchdowns, receptions, and more
- **Performance Trends**: Analyze recent 3-week performance trends to identify hot/cold streaks
- **Trade Advice**: Get AI-powered recommendations based on actual stats, projections, and recent performance
- **Projections vs Actuals**: Compare projected points with actual performance
- **Injury Status Tracking**: Stay updated on player health and availability
- **Player Ownership Data**: See ownership percentages to identify value picks
- **Matchup Analysis**: Get weekly matchup insights with projected points
- **League Insights**: Understand your league standings and competition

### What Yahoo Data is Used

The chatbot pulls comprehensive data from Yahoo Fantasy Football API:

#### Player Statistics
- **Current Week Stats**: Passing yards, passing TDs, interceptions, rushing yards, rushing TDs, receptions, receiving yards, receiving TDs, fumbles, and more
- **Season Stats**: Full season aggregated statistics for all players
- **Weekly Performance**: Individual game-by-game stats for trend analysis
- **Fantasy Points**: Actual points scored and projected points

#### Team & League Data
- **Roster Information**: Complete roster with starter/bench designations
- **Player Health**: Injury status (Healthy, Questionable, Doubtful, Out, IR)
- **Matchup Data**: Current week opponent and projected scores
- **Standings**: League rankings, records, and points for/against
- **Ownership**: Player ownership percentages across Yahoo leagues

#### Smart Analysis
- **Trend Detection**: Automatically analyzes last 3 weeks when you ask about trades or player comparisons
- **Context-Aware**: Provides different detail levels based on your question
- **Real-time Updates**: Fetches fresh data on every query

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
- "Who should I start at RB based on recent trends?"
- "Which players are underperforming their projections?"

**Trade Analysis:**
- "What trades should I consider based on my team's weaknesses?"
- "Should I trade Player A for Player B?"
- "Who on my bench has the most trade value?"

**Performance Analysis:**
- "Analyze my recent performance trends"
- "Which of my players are trending up?"
- "Who on my bench is performing well?"

**General Team Questions:**
- "What's my chances of winning this week?"
- "Analyze my team's strengths and weaknesses"
- "Show me my current roster"

**Commands:**
- `refresh` - Refresh team data from Yahoo
- `help` - Show help and available commands
- `quit`/`exit`/`q` - Exit the chatbot

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

1. **Data Retrieval**: The chatbot connects to Yahoo Fantasy API to fetch comprehensive data:
   - Player stats (current week, season totals, recent trends)
   - Fantasy points (actual and projected)
   - Team roster, matchups, and league standings
   - Player health status and ownership data

2. **Smart Context Loading**:
   - For general questions: Loads basic team data for fast responses
   - For trade/analysis questions: Automatically fetches detailed stats and 3-week performance trends

3. **AI Analysis**: Your questions and all relevant fantasy data are sent to Claude AI for intelligent analysis:
   - Claude analyzes actual statistics, not just player names
   - Considers recent performance trends and projections
   - Factors in injuries, ownership, and matchup data

4. **Personalized Advice**: Claude provides specific, data-driven advice:
   - References actual stats in recommendations
   - Compares projections vs recent performance
   - Identifies trends (hot/cold streaks)
   - Provides reasoning based on your specific league situation

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
