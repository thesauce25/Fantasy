"""
Yahoo Fantasy Football API Client

This module provides a wrapper around the YFPY library to fetch
fantasy football data from Yahoo Fantasy Sports API.
"""

import os
import json
from pathlib import Path
from typing import Dict, List, Optional, Any
from yfpy.query import YahooFantasySportsQuery
from dotenv import load_dotenv


class YahooFantasyClient:
    """Client for interacting with Yahoo Fantasy Football API."""

    def __init__(self):
        """Initialize the Yahoo Fantasy client."""
        load_dotenv()

        # Load configuration from environment
        self.client_id = os.getenv('YAHOO_CLIENT_ID')
        self.client_secret = os.getenv('YAHOO_CLIENT_SECRET')
        self.league_id = os.getenv('YAHOO_LEAGUE_ID')
        self.game_code = os.getenv('YAHOO_GAME_CODE', 'nfl')
        self.season = os.getenv('YAHOO_SEASON', '2024')

        if not all([self.client_id, self.client_secret]):
            raise ValueError(
                "Missing Yahoo API credentials. Please set YAHOO_CLIENT_ID "
                "and YAHOO_CLIENT_SECRET in your .env file."
            )

        # Initialize YFPY query
        self.yahoo_query = None
        self._initialize_client()

    def _initialize_client(self):
        """Initialize the YFPY client with OAuth."""
        try:
            self.yahoo_query = YahooFantasySportsQuery(
                league_id=self.league_id,
                game_code=self.game_code,
                game_id=None,  # Will be auto-determined
                yahoo_consumer_key=self.client_id,
                yahoo_consumer_secret=self.client_secret,
                env_var_directory=Path.cwd(),
                save_data=False
            )
            print("✓ Successfully connected to Yahoo Fantasy API")
        except Exception as e:
            print(f"✗ Failed to initialize Yahoo API client: {e}")
            raise

    def get_user_teams(self) -> List[Dict[str, Any]]:
        """Get all fantasy teams for the authenticated user."""
        try:
            teams = self.yahoo_query.get_all_yahoo_fantasy_game_keys()
            return teams if teams else []
        except Exception as e:
            print(f"Error fetching user teams: {e}")
            return []

    def get_league_info(self) -> Optional[Dict[str, Any]]:
        """Get information about the league."""
        try:
            league = self.yahoo_query.get_league_info()
            return {
                'name': league.name,
                'season': league.season,
                'num_teams': league.num_teams,
                'current_week': league.current_week,
                'start_week': league.start_week,
                'end_week': league.end_week,
                'game_code': league.game_code,
                'scoring_type': league.scoring_type,
                'league_type': league.league_type,
            }
        except Exception as e:
            print(f"Error fetching league info: {e}")
            return None

    def get_my_team(self) -> Optional[Dict[str, Any]]:
        """Get the user's fantasy team information."""
        try:
            teams = self.yahoo_query.get_league_teams()
            if not teams:
                return None

            # Find the user's team (usually the first one, but let's check)
            for team in teams:
                team_info = {
                    'team_key': team.team_key,
                    'team_id': team.team_id,
                    'name': team.name,
                    'managers': [m.nickname for m in team.managers] if hasattr(team, 'managers') else [],
                    'wins': team.team_standings.outcome_totals.wins if hasattr(team, 'team_standings') else 0,
                    'losses': team.team_standings.outcome_totals.losses if hasattr(team, 'team_standings') else 0,
                    'ties': team.team_standings.outcome_totals.ties if hasattr(team, 'team_standings') else 0,
                    'points_for': team.team_points.total if hasattr(team, 'team_points') else 0,
                    'points_against': team.team_points.total if hasattr(team, 'team_points') else 0,
                }
                # For now, return the first team found
                return team_info

            return None
        except Exception as e:
            print(f"Error fetching team: {e}")
            return None

    def get_roster(self, team_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get the roster for a team."""
        try:
            roster = self.yahoo_query.get_team_roster_by_week(
                team_id=team_id if team_id else self.get_my_team()['team_id'],
                chosen_week='current'
            )

            players = []
            for player in roster:
                player_info = {
                    'name': player.name.full,
                    'player_id': player.player_id,
                    'position': player.primary_position,
                    'status': player.status if hasattr(player, 'status') else 'Healthy',
                    'selected_position': player.selected_position.position if hasattr(player, 'selected_position') else 'BN',
                    'team': player.editorial_team_abbr if hasattr(player, 'editorial_team_abbr') else '',
                    'bye_week': player.bye_weeks.week if hasattr(player, 'bye_weeks') else None,
                }

                # Add stats if available
                if hasattr(player, 'player_stats') and player.player_stats:
                    player_info['stats'] = {
                        stat.stat_id: stat.value for stat in player.player_stats.stats
                    }

                players.append(player_info)

            return players
        except Exception as e:
            print(f"Error fetching roster: {e}")
            return []

    def get_standings(self) -> List[Dict[str, Any]]:
        """Get league standings."""
        try:
            standings = self.yahoo_query.get_league_standings()

            teams = []
            for team in standings:
                team_info = {
                    'rank': team.team_standings.rank if hasattr(team, 'team_standings') else 0,
                    'name': team.name,
                    'wins': team.team_standings.outcome_totals.wins if hasattr(team, 'team_standings') else 0,
                    'losses': team.team_standings.outcome_totals.losses if hasattr(team, 'team_standings') else 0,
                    'ties': team.team_standings.outcome_totals.ties if hasattr(team, 'team_standings') else 0,
                    'points_for': team.team_points.total if hasattr(team, 'team_points') else 0,
                    'points_against': team.team_projected_points.total if hasattr(team, 'team_projected_points') else 0,
                }
                teams.append(team_info)

            # Sort by rank
            teams.sort(key=lambda x: x['rank'])
            return teams
        except Exception as e:
            print(f"Error fetching standings: {e}")
            return []

    def get_matchup(self, week: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """Get matchup information for a specific week."""
        try:
            if week is None:
                league_info = self.get_league_info()
                week = league_info['current_week'] if league_info else 1

            my_team = self.get_my_team()
            if not my_team:
                return None

            matchup = self.yahoo_query.get_team_matchups_by_week(
                team_id=my_team['team_id'],
                chosen_week=str(week)
            )

            if not matchup or not matchup.teams:
                return None

            # Get both teams in the matchup
            teams = []
            for team in matchup.teams:
                team_data = {
                    'name': team.name,
                    'points': team.team_points.total if hasattr(team, 'team_points') else 0,
                    'projected_points': team.team_projected_points.total if hasattr(team, 'team_projected_points') else 0,
                }
                teams.append(team_data)

            return {
                'week': week,
                'teams': teams,
            }
        except Exception as e:
            print(f"Error fetching matchup: {e}")
            return None

    def get_free_agents(self, position: Optional[str] = None, count: int = 25) -> List[Dict[str, Any]]:
        """Get top available free agents."""
        try:
            # YFPY can get free agents
            free_agents = self.yahoo_query.get_league_players(
                player_count=count,
                status='A',  # Available players
                position=position
            )

            players = []
            for player in free_agents:
                player_info = {
                    'name': player.name.full,
                    'player_id': player.player_id,
                    'position': player.primary_position,
                    'team': player.editorial_team_abbr if hasattr(player, 'editorial_team_abbr') else '',
                    'percent_owned': player.percent_owned.value if hasattr(player, 'percent_owned') else 0,
                }
                players.append(player_info)

            return players
        except Exception as e:
            print(f"Error fetching free agents: {e}")
            return []

    def format_team_summary(self) -> str:
        """Format a summary of the user's team and league."""
        try:
            league_info = self.get_league_info()
            my_team = self.get_my_team()
            roster = self.get_roster()
            standings = self.get_standings()
            matchup = self.get_matchup()

            summary = []
            summary.append("=== FANTASY FOOTBALL TEAM SUMMARY ===\n")

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
                summary.append("=== YOUR ROSTER ===")
                # Group by position
                starters = [p for p in roster if p['selected_position'] not in ['BN', 'IR']]
                bench = [p for p in roster if p['selected_position'] in ['BN', 'IR']]

                if starters:
                    summary.append("Starters:")
                    for player in starters:
                        status = f" ({player['status']})" if player['status'] != 'Healthy' else ''
                        summary.append(f"  {player['selected_position']}: {player['name']} - {player['team']}{status}")

                if bench:
                    summary.append("\nBench:")
                    for player in bench:
                        status = f" ({player['status']})" if player['status'] != 'Healthy' else ''
                        summary.append(f"  {player['name']} - {player['position']} - {player['team']}{status}")
                summary.append("")

            if standings:
                summary.append("=== LEAGUE STANDINGS (Top 5) ===")
                for i, team in enumerate(standings[:5], 1):
                    summary.append(
                        f"{i}. {team['name']}: {team['wins']}-{team['losses']}-{team['ties']} "
                        f"({team['points_for']} PF)"
                    )

            return "\n".join(summary)
        except Exception as e:
            return f"Error generating team summary: {e}"
