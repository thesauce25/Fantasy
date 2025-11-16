#!/usr/bin/env python3
"""
Fantasy Football Chatbot

An AI-powered chatbot that provides personalized fantasy football advice
using Yahoo Fantasy Football API and Claude AI.
"""

import os
import sys
from typing import List, Dict
from anthropic import Anthropic
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from yahoo_client import YahooFantasyClient


class FantasyFootballChatbot:
    """AI chatbot for fantasy football advice."""

    def __init__(self):
        """Initialize the chatbot."""
        load_dotenv()

        self.console = Console()
        self.anthropic_api_key = os.getenv('ANTHROPIC_API_KEY')

        if not self.anthropic_api_key:
            raise ValueError(
                "Missing Anthropic API key. Please set ANTHROPIC_API_KEY in your .env file."
            )

        # Initialize clients
        self.anthropic = Anthropic(api_key=self.anthropic_api_key)
        self.yahoo_client = None
        self.conversation_history: List[Dict] = []

        # System prompt for Claude
        self.system_prompt = """You are an expert fantasy football advisor with deep knowledge of:
- NFL player performance and statistics
- Fantasy football strategy and best practices
- Start/sit decisions
- Trade evaluation
- Waiver wire pickups
- Roster construction
- Matchup analysis

You have access to the user's real Yahoo Fantasy Football team data including:
- Their current roster and lineup with DETAILED STATS
- Player points scored (current week and projections)
- Individual player statistics (passing yards, rushing yards, TDs, receptions, etc.)
- Player injury status and health information
- Player ownership percentages across leagues
- League standings and settings
- Current week matchup with projected points
- Team records and points for/against

When analyzing players or making recommendations:
1. **Use the actual stats provided** - You have real data on passing yards, rushing yards, TDs, receptions, etc.
2. **Consider current week projections** - Compare projected points vs actual performance
3. **Factor in injury status** - Players marked as Out, Questionable, Doubtful should impact your advice
4. **Analyze ownership data** - Low ownership gems vs high ownership players
5. **Review recent performance trends** - Not just name value, but actual production
6. **Consider matchups** - Compare team's projected points in current matchup
7. **Explain your reasoning clearly** - Reference specific stats when making recommendations
8. **Provide multiple options when appropriate** - Give alternatives with pros/cons

For trade recommendations specifically:
- Analyze both players' actual stats and projections
- Consider positional depth on the roster
- Factor in upcoming schedules and bye weeks
- Evaluate if the trade addresses team weaknesses
- Use the ownership data to assess player value
- Consider recent performance trends (improving vs declining)

Be conversational, enthusiastic, and helpful. ALWAYS reference the specific stats, projections,
and data points you see when making recommendations. This isn't generic advice - you have
real-time data on this specific team and league.

Keep responses concise but informative. Use bullet points and clear formatting when helpful."""

    def initialize_yahoo_client(self):
        """Initialize the Yahoo Fantasy client."""
        try:
            self.console.print("\n[bold cyan]Connecting to Yahoo Fantasy API...[/bold cyan]")
            self.yahoo_client = YahooFantasyClient()
            return True
        except Exception as e:
            self.console.print(f"[bold red]Error connecting to Yahoo API:[/bold red] {e}")
            self.console.print("\n[yellow]Please check your .env file and ensure:[/yellow]")
            self.console.print("[yellow]1. YAHOO_CLIENT_ID and YAHOO_CLIENT_SECRET are set[/yellow]")
            self.console.print("[yellow]2. YAHOO_LEAGUE_ID is set to your league ID[/yellow]")
            self.console.print("[yellow]3. You have a Yahoo Fantasy Football account[/yellow]")
            self.console.print("[yellow]\nSee README.md for detailed setup instructions.[/yellow]")
            return False

    def get_team_context(self, include_trends: bool = False) -> str:
        """Get context about the user's team and league.

        Args:
            include_trends: If True, includes recent weekly performance trends (slower but more detailed)
        """
        if not self.yahoo_client:
            return "No team data available. Please configure Yahoo API access."

        try:
            if include_trends:
                # This is slower but provides richer data for recommendations
                return self._format_team_summary_with_trends()
            else:
                return self.yahoo_client.format_team_summary()
        except Exception as e:
            return f"Unable to fetch team data: {e}"

    def _format_team_summary_with_trends(self) -> str:
        """Get team summary with recent performance trends for deeper analysis."""
        try:
            league_info = self.yahoo_client.get_league_info()
            my_team = self.yahoo_client.get_my_team()
            roster = self.yahoo_client.get_roster_with_recent_performance()
            standings = self.yahoo_client.get_standings()
            matchup = self.yahoo_client.get_matchup()

            summary = []
            summary.append("=== FANTASY FOOTBALL TEAM SUMMARY (WITH TRENDS) ===\n")

            if league_info:
                summary.append(f"League: {league_info['name']}")
                summary.append(f"Season: {league_info['season']}")
                summary.append(f"Current Week: {league_info['current_week']}\n")

            if my_team:
                summary.append(f"Your Team: {my_team['name']}")
                summary.append(f"Record: {my_team['wins']}-{my_team['losses']}-{my_team['ties']}")
                summary.append(f"Points For: {my_team['points_for']}\n")

            if matchup:
                summary.append("=== CURRENT MATCHUP ===")
                for team in matchup['teams']:
                    summary.append(f"{team['name']}: {team['points']} pts (proj: {team['projected_points']})")
                summary.append("")

            if roster:
                summary.append("=== YOUR ROSTER (with detailed stats, projections, and trends) ===")
                starters = [p for p in roster if p['selected_position'] not in ['BN', 'IR']]
                bench = [p for p in roster if p['selected_position'] in ['BN', 'IR']]

                if starters:
                    summary.append("Starters:")
                    for player in starters:
                        summary.append(self._format_player_with_trends(player))

                if bench:
                    summary.append("\nBench:")
                    for player in bench:
                        summary.append(self._format_player_with_trends(player))
                summary.append("")

            if standings:
                summary.append("=== LEAGUE STANDINGS (Top 5) ===")
                for i, team in enumerate(standings[:5], 1):
                    summary.append(
                        f"{i}. {team['name']}: {team['wins']}-{team['losses']}-{team['ties']} "
                        f"({team['points_for']} PF)"
                    )
                summary.append("")

            return "\n".join(summary)
        except Exception as e:
            return f"Error generating detailed team summary: {e}"

    def _format_player_with_trends(self, player: dict) -> str:
        """Format player with recent performance trends."""
        # Use the base formatting from yahoo_client
        base_line = self.yahoo_client._format_player_line(player)

        # Add trend analysis if available
        if 'recent_performance' in player and player['recent_performance']:
            recent = player['recent_performance']
            weeks_str = ", ".join([f"Wk{w['week']}: {w.get('points', 0):.1f}pts" for w in recent[:3]])
            base_line += f"\n      Recent: {weeks_str}"

        if 'avg_recent_points' in player:
            base_line += f" | Avg: {player['avg_recent_points']:.1f}pts"

        return base_line

    def chat(self, user_message: str) -> str:
        """Send a message to Claude and get a response."""
        # Detect if this is a trade or detailed analysis query
        trade_keywords = ['trade', 'swap', 'deal', 'who should i', 'start or sit', 'analyze', 'trends', 'recent performance']
        use_trends = any(keyword in user_message.lower() for keyword in trade_keywords)

        # Get fresh team context for each message
        if use_trends:
            self.console.print("[dim]Fetching detailed stats and trends...[/dim]")
            team_context = self.get_team_context(include_trends=True)
        else:
            team_context = self.get_team_context(include_trends=False)

        # Add user message to conversation history
        self.conversation_history.append({
            "role": "user",
            "content": user_message
        })

        # Prepare messages with team context
        messages = []

        # Add team context as first message if this is the first user message
        if len(self.conversation_history) == 1:
            messages.append({
                "role": "user",
                "content": f"Here's my current team and league information:\n\n{team_context}"
            })
            messages.append({
                "role": "assistant",
                "content": "Thanks! I've reviewed your team. I'm ready to help with any fantasy football questions or advice you need. What would you like to know?"
            })
        elif use_trends:
            # For trade/analysis queries, include fresh detailed context
            messages.append({
                "role": "user",
                "content": f"Here's the latest detailed team data with stats and trends:\n\n{team_context}"
            })

        # Add conversation history
        messages.extend(self.conversation_history)

        try:
            # Call Claude API
            response = self.anthropic.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=2000,
                system=self.system_prompt,
                messages=messages
            )

            # Extract response text
            assistant_message = response.content[0].text

            # Add to conversation history
            self.conversation_history.append({
                "role": "assistant",
                "content": assistant_message
            })

            return assistant_message

        except Exception as e:
            error_msg = f"Error communicating with Claude: {e}"
            self.console.print(f"[bold red]{error_msg}[/bold red]")
            return error_msg

    def run(self):
        """Run the chatbot CLI."""
        # Print welcome banner
        self.console.print(Panel.fit(
            "[bold cyan]Fantasy Football Chatbot[/bold cyan]\n"
            "Powered by Yahoo Fantasy API + Claude AI",
            border_style="cyan"
        ))

        # Initialize Yahoo client
        if not self.initialize_yahoo_client():
            sys.exit(1)

        # Show initial team summary
        self.console.print("\n[bold green]Loading your team data...[/bold green]\n")
        team_summary = self.get_team_context()
        self.console.print(Panel(team_summary, title="Your Team", border_style="green"))

        # Main chat loop
        self.console.print("\n[bold]Ask me anything about your fantasy football team![/bold]")
        self.console.print("[dim]Type 'quit', 'exit', or 'q' to end the conversation.[/dim]\n")

        while True:
            try:
                # Get user input
                user_input = self.console.input("[bold blue]You:[/bold blue] ").strip()

                if not user_input:
                    continue

                # Check for exit commands
                if user_input.lower() in ['quit', 'exit', 'q']:
                    self.console.print("\n[bold cyan]Thanks for using Fantasy Football Chatbot! Good luck this week! 🏈[/bold cyan]\n")
                    break

                # Special commands
                if user_input.lower() == 'refresh':
                    team_summary = self.get_team_context()
                    self.console.print(Panel(team_summary, title="Your Team (Refreshed)", border_style="green"))
                    continue

                if user_input.lower() == 'help':
                    help_text = """
**Available Commands:**
- `refresh` - Refresh your team data from Yahoo
- `help` - Show this help message
- `quit`/`exit`/`q` - Exit the chatbot

**What data I have access to:**
- Player stats (passing/rushing/receiving yards, TDs, receptions, etc.)
- Current week points and projections
- Recent performance trends (last 3 weeks)
- Injury status and health updates
- Player ownership percentages
- League standings and matchup data
- Team records and scoring

**Example Questions:**
- "Should I start [Player A] or [Player B] this week?"
- "What trades should I consider based on my team's weaknesses?"
- "Analyze my recent performance trends"
- "Who on my bench is performing well?"
- "What's my chances of winning this week?"
- "Which players are underperforming vs their projections?"

**Smart Features:**
- Automatically fetches detailed stats when you ask about trades or player analysis
- Considers recent trends (not just season averages)
- Uses actual stats from your Yahoo league
"""
                    self.console.print(Markdown(help_text))
                    continue

                # Get response from Claude
                self.console.print()  # Blank line
                with self.console.status("[bold green]Thinking...[/bold green]"):
                    response = self.chat(user_input)

                # Display response
                self.console.print(f"[bold green]Assistant:[/bold green]")
                self.console.print(Markdown(response))
                self.console.print()  # Blank line

            except KeyboardInterrupt:
                self.console.print("\n\n[bold cyan]Goodbye! 🏈[/bold cyan]\n")
                break
            except Exception as e:
                self.console.print(f"\n[bold red]Error:[/bold red] {e}\n")


def main():
    """Main entry point."""
    try:
        chatbot = FantasyFootballChatbot()
        chatbot.run()
    except KeyboardInterrupt:
        print("\n\nGoodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
