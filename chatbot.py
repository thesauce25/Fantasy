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
- Their current roster and lineup
- League standings and settings
- Current week matchup
- Available free agents
- League scoring rules

Provide specific, actionable advice based on their actual team and league situation.
Be conversational, enthusiastic, and helpful. Use your knowledge of NFL players and
strategy to give personalized recommendations.

When analyzing players or making recommendations:
1. Consider their current team composition
2. Look at matchups and upcoming schedules
3. Factor in injury status and recent performance
4. Explain your reasoning clearly
5. Provide multiple options when appropriate

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

    def get_team_context(self) -> str:
        """Get context about the user's team and league."""
        if not self.yahoo_client:
            return "No team data available. Please configure Yahoo API access."

        try:
            return self.yahoo_client.format_team_summary()
        except Exception as e:
            return f"Unable to fetch team data: {e}"

    def chat(self, user_message: str) -> str:
        """Send a message to Claude and get a response."""
        # Get fresh team context for each message
        team_context = self.get_team_context()

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

**Example Questions:**
- "Should I start [Player A] or [Player B] this week?"
- "What trades should I consider?"
- "Who are the best players on waivers?"
- "Analyze my team's strengths and weaknesses"
- "What's my chances of winning this week?"
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
