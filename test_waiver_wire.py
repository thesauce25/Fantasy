#!/usr/bin/env python3
"""
Test script to validate waiver wire functionality
"""

from yahoo_client import YahooFantasyClient
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()


def test_waiver_wire():
    """Test the waiver wire retrieval functionality."""
    console.print("\n[bold cyan]Testing Waiver Wire Functionality[/bold cyan]\n")

    try:
        # Initialize client
        console.print("[yellow]Initializing Yahoo Fantasy client...[/yellow]")
        client = YahooFantasyClient()
        console.print("[green]✓ Client initialized successfully[/green]\n")

        # Test 1: Get league info
        console.print("[yellow]Test 1: Fetching league info...[/yellow]")
        league_info = client.get_league_info()
        if league_info:
            console.print(f"[green]✓ League: {league_info['name']}[/green]")
            console.print(f"[green]✓ Season: {league_info['season']}[/green]")
            console.print(f"[green]✓ Current Week: {league_info['current_week']}[/green]\n")
        else:
            console.print("[red]✗ Failed to fetch league info[/red]\n")
            return

        # Test 2: Get free agents (all positions)
        console.print("[yellow]Test 2: Fetching top 15 free agents...[/yellow]")
        free_agents = client.get_free_agents(count=15)

        if free_agents:
            console.print(f"[green]✓ Found {len(free_agents)} free agents[/green]\n")

            # Create a table for display
            table = Table(title="Top Available Free Agents")
            table.add_column("Name", style="cyan", no_wrap=True)
            table.add_column("Pos", style="magenta")
            table.add_column("Team", style="yellow")
            table.add_column("Own %", justify="right", style="green")
            table.add_column("Status", style="blue")
            table.add_column("Recent", style="red")

            for player in free_agents[:10]:  # Show top 10
                table.add_row(
                    player.get('name', 'Unknown'),
                    player.get('position', 'N/A'),
                    player.get('team', ''),
                    f"{player.get('percent_owned', 0):.1f}%",
                    player.get('status', 'Healthy'),
                    "🔥" if player.get('recently_dropped') else ""
                )

            console.print(table)
            console.print()
        else:
            console.print("[red]✗ No free agents found[/red]")
            console.print("[yellow]This could mean:[/yellow]")
            console.print("[yellow]  - Yahoo API is not returning player data[/yellow]")
            console.print("[yellow]  - All players are owned in your league[/yellow]")
            console.print("[yellow]  - API authentication issues[/yellow]\n")
            return

        # Test 3: Get free agents by position
        for position in ['QB', 'RB', 'WR', 'TE']:
            console.print(f"[yellow]Test 3.{position}: Fetching {position}s...[/yellow]")
            pos_players = client.get_free_agents(position=position, count=5)
            if pos_players:
                console.print(f"[green]✓ Found {len(pos_players)} available {position}s[/green]")
                for i, player in enumerate(pos_players[:3], 1):
                    recently_dropped = " 🔥" if player.get('recently_dropped') else ""
                    console.print(
                        f"  {i}. {player['name']} - {player['team']} "
                        f"({player.get('percent_owned', 0):.0f}% owned){recently_dropped}"
                    )
            else:
                console.print(f"[yellow]⚠ No {position}s available[/yellow]")
            console.print()

        # Test 4: Full team summary
        console.print("[yellow]Test 4: Generating full team summary...[/yellow]")
        summary = client.format_team_summary()
        console.print(Panel(summary, title="Team Summary", border_style="green"))

        console.print("\n[bold green]✓ All tests completed successfully![/bold green]\n")

        # Show diagnostic info
        if not free_agents or len(free_agents) == 0:
            console.print("[bold yellow]⚠ IMPORTANT NOTE:[/bold yellow]")
            console.print("[yellow]The Yahoo Fantasy API returned only stale/retired players.[/yellow]")
            console.print("[yellow]This is a known limitation of Yahoo's get_league_players() endpoint.[/yellow]")
            console.print("[yellow]The app has filtered them out to avoid showing bad data.[/yellow]\n")
            console.print("[cyan]For waiver wire decisions, you should:[/cyan]")
            console.print("[cyan]  1. Check your Yahoo Fantasy league website directly[/cyan]")
            console.print("[cyan]  2. Use the chatbot for strategy advice (who to target, who to drop)[/cyan]")
            console.print("[cyan]  3. Ask about specific players you're considering[/cyan]\n")

    except Exception as e:
        console.print(f"\n[bold red]✗ Error during testing: {e}[/bold red]")
        import traceback
        console.print("\n[red]Traceback:[/red]")
        console.print(traceback.format_exc())


if __name__ == "__main__":
    test_waiver_wire()
