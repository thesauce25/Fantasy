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
        self.team_name = os.getenv('YAHOO_TEAM_NAME', '')

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
            # Let YFPY auto-determine the game_id based on current season
            # This avoids issues with incorrect game_id calculations
            self.yahoo_query = YahooFantasySportsQuery(
                league_id=self.league_id,
                game_code=self.game_code,
                game_id=None,  # Auto-determined by YFPY
                yahoo_consumer_key=self.client_id,
                yahoo_consumer_secret=self.client_secret,
                env_file_location=Path.cwd(),
                browser_callback=True
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

            def decode_if_bytes(val):
                return val.decode('utf-8') if isinstance(val, bytes) else val

            return {
                'name': decode_if_bytes(league.name),
                'season': league.season,
                'num_teams': league.num_teams,
                'current_week': league.current_week,
                'start_week': league.start_week,
                'end_week': league.end_week,
                'game_code': decode_if_bytes(league.game_code) if hasattr(league, 'game_code') else 'nfl',
                'scoring_type': decode_if_bytes(league.scoring_type) if hasattr(league, 'scoring_type') else 'head',
                'league_type': decode_if_bytes(league.league_type) if hasattr(league, 'league_type') else 'private',
            }
        except Exception as e:
            print(f"Error fetching league info: {e}")
            import traceback
            traceback.print_exc()
            return None

    def get_my_team(self) -> Optional[Dict[str, Any]]:
        """Get the user's fantasy team information."""
        try:
            # Get all league teams with standings
            teams = self.yahoo_query.get_league_teams()
            if not teams:
                return None

            # Decode bytes to string if necessary
            def decode_if_bytes(val):
                return val.decode('utf-8') if isinstance(val, bytes) else val

            # Find the user's team
            my_team = None

            # If team name is specified in config, use it to find the team
            if self.team_name:
                for team in teams:
                    team_name_decoded = decode_if_bytes(team.name)
                    if team_name_decoded.lower() == self.team_name.lower():
                        my_team = team
                        print(f"✓ Found your team: {team_name_decoded}")
                        break

                if not my_team:
                    print(f"⚠ Warning: Could not find team '{self.team_name}' in league")
                    print(f"Available teams: {[decode_if_bytes(t.name) for t in teams[:5]]}")
                    print("Using first team as fallback")

            # If no team name specified or not found, use first team
            if not my_team:
                my_team = teams[0]

            team_info = {
                'team_key': my_team.team_key,
                'team_id': my_team.team_id,
                'name': decode_if_bytes(my_team.name),
                'managers': [decode_if_bytes(m.nickname) for m in my_team.managers] if hasattr(my_team, 'managers') and my_team.managers else [],
                'wins': my_team.team_standings.outcome_totals.wins if hasattr(my_team, 'team_standings') and my_team.team_standings else 0,
                'losses': my_team.team_standings.outcome_totals.losses if hasattr(my_team, 'team_standings') and my_team.team_standings else 0,
                'ties': my_team.team_standings.outcome_totals.ties if hasattr(my_team, 'team_standings') and my_team.team_standings else 0,
                'points_for': float(my_team.team_standings.points_for) if hasattr(my_team, 'team_standings') and my_team.team_standings else 0.0,
                'points_against': float(my_team.team_standings.points_against) if hasattr(my_team, 'team_standings') and my_team.team_standings else 0.0,
            }
            return team_info

        except Exception as e:
            print(f"Error fetching team: {e}")
            import traceback
            traceback.print_exc()
            return None

    def get_roster(self, team_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get the roster for a team."""
        try:
            if not team_id:
                my_team = self.get_my_team()
                if not my_team:
                    return []
                team_id = my_team['team_id']

            roster_obj = self.yahoo_query.get_team_roster_by_week(
                team_id=team_id,
                chosen_week='current'
            )

            # Roster is an object with a .players attribute
            if not hasattr(roster_obj, 'players') or not roster_obj.players:
                return []

            def decode_if_bytes(val):
                return val.decode('utf-8') if isinstance(val, bytes) else val

            players = []
            for player in roster_obj.players:
                player_info = {
                    'name': decode_if_bytes(player.name.full) if hasattr(player.name, 'full') else decode_if_bytes(str(player.name)),
                    'player_id': player.player_id,
                    'position': player.primary_position if hasattr(player, 'primary_position') else 'N/A',
                    'status': player.status if hasattr(player, 'status') and player.status else 'Healthy',
                    'selected_position': player.selected_position.position if hasattr(player, 'selected_position') and player.selected_position else 'BN',
                    'team': decode_if_bytes(player.editorial_team_abbr) if hasattr(player, 'editorial_team_abbr') else '',
                    'bye_week': player.bye_weeks.week if hasattr(player, 'bye_weeks') and player.bye_weeks else None,
                }

                # Add stats if available
                if hasattr(player, 'player_stats') and player.player_stats:
                    if hasattr(player.player_stats, 'stats'):
                        player_info['stats'] = {
                            stat.stat_id: stat.value for stat in player.player_stats.stats
                        }

                players.append(player_info)

            return players
        except Exception as e:
            print(f"Error fetching roster: {e}")
            import traceback
            traceback.print_exc()
            return []

    def get_standings(self) -> List[Dict[str, Any]]:
        """Get league standings."""
        try:
            standings_obj = self.yahoo_query.get_league_standings()

            # Standings is an object with a .teams attribute
            if not hasattr(standings_obj, 'teams') or not standings_obj.teams:
                return []

            def decode_if_bytes(val):
                return val.decode('utf-8') if isinstance(val, bytes) else val

            teams = []
            for team in standings_obj.teams:
                team_info = {
                    'rank': team.team_standings.rank if hasattr(team, 'team_standings') and team.team_standings else 0,
                    'name': decode_if_bytes(team.name),
                    'wins': team.team_standings.outcome_totals.wins if hasattr(team, 'team_standings') and team.team_standings else 0,
                    'losses': team.team_standings.outcome_totals.losses if hasattr(team, 'team_standings') and team.team_standings else 0,
                    'ties': team.team_standings.outcome_totals.ties if hasattr(team, 'team_standings') and team.team_standings else 0,
                    'points_for': float(team.team_standings.points_for) if hasattr(team, 'team_standings') and team.team_standings else 0.0,
                    'points_against': float(team.team_standings.points_against) if hasattr(team, 'team_standings') and team.team_standings else 0.0,
                }
                teams.append(team_info)

            # Sort by rank
            teams.sort(key=lambda x: x['rank'])
            return teams
        except Exception as e:
            print(f"Error fetching standings: {e}")
            import traceback
            traceback.print_exc()
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

            # get_team_matchups returns a list of matchups
            matchups = self.yahoo_query.get_team_matchups(team_id=my_team['team_id'])

            if not matchups:
                return None

            def decode_if_bytes(val):
                return val.decode('utf-8') if isinstance(val, bytes) else val

            # Find the matchup for the specified week
            current_matchup = None
            for matchup in matchups:
                if hasattr(matchup, 'week') and int(matchup.week) == int(week):
                    current_matchup = matchup
                    break

            # If no specific week matchup found, use the most recent one
            if not current_matchup and len(matchups) > 0:
                current_matchup = matchups[-1]  # Most recent

            if not current_matchup:
                return None

            # Get both teams in the matchup
            teams = []
            if hasattr(current_matchup, 'teams') and current_matchup.teams:
                for team in current_matchup.teams:
                    team_data = {
                        'name': decode_if_bytes(team.name) if hasattr(team, 'name') else 'Unknown',
                        'points': float(team.team_points.total) if hasattr(team, 'team_points') and team.team_points else 0.0,
                        'projected_points': float(team.team_projected_points.total) if hasattr(team, 'team_projected_points') and team.team_projected_points else 0.0,
                    }
                    teams.append(team_data)

            return {
                'week': week,
                'teams': teams,
            }
        except Exception as e:
            print(f"Error fetching matchup: {e}")
            import traceback
            traceback.print_exc()
            return None

    def get_free_agents(self, position: Optional[str] = None, count: int = 25) -> List[Dict[str, Any]]:
        """Get top available free agents."""
        try:
            def decode_if_bytes(val):
                return val.decode('utf-8') if isinstance(val, bytes) else val

            # YFPY get_league_players accepts 'limit' not 'player_count'
            # and uses 'status' for filtering (A = available)
            free_agents = self.yahoo_query.get_league_players(
                limit=count,
                status='A'  # Available players only
            )

            players = []
            if not free_agents:
                return []

            for player in free_agents:
                # Filter by position if specified
                if position:
                    player_pos = player.primary_position if hasattr(player, 'primary_position') else ''
                    if isinstance(player_pos, bytes):
                        player_pos = player_pos.decode('utf-8')
                    if player_pos != position:
                        continue

                player_info = {
                    'name': decode_if_bytes(player.name.full) if hasattr(player.name, 'full') else decode_if_bytes(str(player.name)),
                    'player_id': player.player_id,
                    'position': decode_if_bytes(player.primary_position) if hasattr(player, 'primary_position') else '',
                    'team': decode_if_bytes(player.editorial_team_abbr) if hasattr(player, 'editorial_team_abbr') else '',
                    'percent_owned': float(player.percent_owned.value) if hasattr(player, 'percent_owned') and player.percent_owned else 0.0,
                }
                players.append(player_info)

                # Stop after getting enough players
                if len(players) >= count:
                    break

            return players
        except Exception as e:
            print(f"Error fetching free agents: {e}")
            import traceback
            traceback.print_exc()
            return []

    def format_team_summary(self) -> str:
        """Format a summary of the user's team and league."""
        try:
            league_info = self.get_league_info()
            my_team = self.get_my_team()
            roster = self.get_roster()
            standings = self.get_standings()
            matchup = self.get_matchup()
            # Get top 50 available free agents
            free_agents = self.get_free_agents(count=50)

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
                summary.append("")

            if free_agents:
                summary.append("=== TOP AVAILABLE FREE AGENTS ===")
                # Group by position
                qbs = [p for p in free_agents if p['position'] == 'QB'][:5]
                rbs = [p for p in free_agents if p['position'] == 'RB'][:5]
                wrs = [p for p in free_agents if p['position'] == 'WR'][:5]
                tes = [p for p in free_agents if p['position'] == 'TE'][:5]

                if qbs:
                    summary.append("QBs:")
                    for player in qbs:
                        summary.append(f"  {player['name']} - {player['team']} ({player['percent_owned']:.0f}% owned)")

                if rbs:
                    summary.append("\nRBs:")
                    for player in rbs:
                        summary.append(f"  {player['name']} - {player['team']} ({player['percent_owned']:.0f}% owned)")

                if wrs:
                    summary.append("\nWRs:")
                    for player in wrs:
                        summary.append(f"  {player['name']} - {player['team']} ({player['percent_owned']:.0f}% owned)")

                if tes:
                    summary.append("\nTEs:")
                    for player in tes:
                        summary.append(f"  {player['name']} - {player['team']} ({player['percent_owned']:.0f}% owned)")

            return "\n".join(summary)
        except Exception as e:
            return f"Error generating team summary: {e}"
