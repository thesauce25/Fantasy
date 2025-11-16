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
            # Calculate game_id based on season year
            # NFL game IDs: 2023=423, 2024=449, 2025=461
            season_year = int(self.season) if self.season else 2024

            # Game ID mapping for NFL
            game_id_map = {
                2023: 423,
                2024: 449,
                2025: 461,
            }

            game_id = game_id_map.get(season_year, 449)  # Default to 2024

            self.yahoo_query = YahooFantasySportsQuery(
                league_id=self.league_id,
                game_code=self.game_code,
                game_id=game_id,
                yahoo_consumer_key=self.client_id,
                yahoo_consumer_secret=self.client_secret,
                env_file_location=Path.cwd(),
                browser_callback=True
            )
            print(f"✓ Successfully connected to Yahoo Fantasy API (Season: {season_year}, Game ID: {game_id})")
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
            # Get standings which includes full team data with records
            standings_obj = self.yahoo_query.get_league_standings()
            if not hasattr(standings_obj, 'teams') or not standings_obj.teams:
                return None

            teams = standings_obj.teams

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
                'wins': my_team.team_standings.outcome_totals.wins if hasattr(my_team, 'team_standings') and my_team.team_standings and hasattr(my_team.team_standings, 'outcome_totals') else 0,
                'losses': my_team.team_standings.outcome_totals.losses if hasattr(my_team, 'team_standings') and my_team.team_standings and hasattr(my_team.team_standings, 'outcome_totals') else 0,
                'ties': my_team.team_standings.outcome_totals.ties if hasattr(my_team, 'team_standings') and my_team.team_standings and hasattr(my_team.team_standings, 'outcome_totals') else 0,
                'points_for': float(my_team.team_standings.points_for) if hasattr(my_team, 'team_standings') and my_team.team_standings and hasattr(my_team.team_standings, 'points_for') else 0.0,
                'points_against': float(my_team.team_standings.points_against) if hasattr(my_team, 'team_standings') and my_team.team_standings and hasattr(my_team.team_standings, 'points_against') else 0.0,
            }
            return team_info

        except Exception as e:
            print(f"Error fetching team: {e}")
            import traceback
            traceback.print_exc()
            return None

    def get_roster(self, team_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get the roster for a team with enhanced stats."""
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

                # Add current week stats if available
                if hasattr(player, 'player_stats') and player.player_stats:
                    if hasattr(player.player_stats, 'stats'):
                        player_info['current_stats'] = self._format_player_stats(player.player_stats.stats)

                # Add player points if available
                if hasattr(player, 'player_points') and player.player_points:
                    if hasattr(player.player_points, 'total'):
                        player_info['points_current_week'] = float(player.player_points.total)

                # Add projected points if available
                if hasattr(player, 'player_projected_points') and player.player_projected_points:
                    if hasattr(player.player_projected_points, 'total'):
                        player_info['projected_points'] = float(player.player_projected_points.total)

                # Add ownership data if available
                if hasattr(player, 'percent_owned'):
                    player_info['percent_owned'] = player.percent_owned

                players.append(player_info)

            return players
        except Exception as e:
            print(f"Error fetching roster: {e}")
            import traceback
            traceback.print_exc()
            return []

    def _format_player_stats(self, stats) -> Dict[str, Any]:
        """Format player stats into a readable dictionary.

        Common Yahoo Fantasy Football stat IDs:
        4: Passing Yards, 5: Passing TDs, 6: Interceptions
        9: Rushing Yards, 10: Rushing TDs
        11: Receptions, 12: Receiving Yards, 13: Receiving TDs
        15: Return TDs, 16: 2-Point Conversions
        18: Fumbles Lost, 57: Offensive Fumble Return TD
        """
        if not stats:
            return {}

        # Mapping of common stat IDs to readable names
        stat_mapping = {
            '4': 'passing_yards',
            '5': 'passing_tds',
            '6': 'interceptions',
            '9': 'rushing_yards',
            '10': 'rushing_tds',
            '11': 'receptions',
            '12': 'receiving_yards',
            '13': 'receiving_tds',
            '15': 'return_tds',
            '16': 'two_point_conversions',
            '18': 'fumbles_lost',
            '57': 'fumble_return_tds',
        }

        formatted_stats = {}
        for stat in stats:
            stat_id = str(stat.stat_id)
            stat_name = stat_mapping.get(stat_id, f'stat_{stat_id}')
            try:
                formatted_stats[stat_name] = float(stat.value) if stat.value else 0
            except (ValueError, AttributeError):
                formatted_stats[stat_name] = stat.value

        return formatted_stats

    def get_player_season_stats(self, player_key: str) -> Optional[Dict[str, Any]]:
        """Get season-long stats for a specific player."""
        try:
            stats_obj = self.yahoo_query.get_player_stats_for_season(
                player_key=player_key
            )

            if not stats_obj:
                return None

            stats_data = {
                'player_key': player_key,
            }

            # Extract stats
            if hasattr(stats_obj, 'player_stats') and stats_obj.player_stats:
                if hasattr(stats_obj.player_stats, 'stats'):
                    stats_data['season_stats'] = self._format_player_stats(stats_obj.player_stats.stats)

            # Extract points
            if hasattr(stats_obj, 'player_points') and stats_obj.player_points:
                if hasattr(stats_obj.player_points, 'total'):
                    stats_data['season_points'] = float(stats_obj.player_points.total)

            return stats_data
        except Exception as e:
            print(f"Error fetching season stats for player {player_key}: {e}")
            return None

    def get_player_weekly_stats(self, player_key: str, week: int) -> Optional[Dict[str, Any]]:
        """Get stats for a specific player for a specific week."""
        try:
            stats_obj = self.yahoo_query.get_player_stats_by_week(
                player_key=player_key,
                week=week
            )

            if not stats_obj:
                return None

            stats_data = {
                'player_key': player_key,
                'week': week,
            }

            # Extract stats
            if hasattr(stats_obj, 'player_stats') and stats_obj.player_stats:
                if hasattr(stats_obj.player_stats, 'stats'):
                    stats_data['stats'] = self._format_player_stats(stats_obj.player_stats.stats)

            # Extract points
            if hasattr(stats_obj, 'player_points') and stats_obj.player_points:
                if hasattr(stats_obj.player_points, 'total'):
                    stats_data['points'] = float(stats_obj.player_points.total)

            return stats_data
        except Exception as e:
            print(f"Error fetching week {week} stats for player {player_key}: {e}")
            return None

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
        """Get top available free agents.

        NOTE: This feature is currently disabled due to Yahoo API limitations.
        The get_league_players() endpoint returns outdated player data (wrong teams, old rosters).
        Users should check the Yahoo Fantasy website directly for accurate waiver wire information.
        """
        # Disabled - Yahoo API returns outdated player data
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
                summary.append("=== YOUR ROSTER (with stats and projections) ===")
                # Group by position
                starters = [p for p in roster if p['selected_position'] not in ['BN', 'IR']]
                bench = [p for p in roster if p['selected_position'] in ['BN', 'IR']]

                if starters:
                    summary.append("Starters:")
                    for player in starters:
                        summary.append(self._format_player_line(player))

                if bench:
                    summary.append("\nBench:")
                    for player in bench:
                        summary.append(self._format_player_line(player))
                summary.append("")

            if standings:
                summary.append("=== LEAGUE STANDINGS (Top 5) ===")
                for i, team in enumerate(standings[:5], 1):
                    summary.append(
                        f"{i}. {team['name']}: {team['wins']}-{team['losses']}-{team['ties']} "
                        f"({team['points_for']} PF)"
                    )
                summary.append("")

            # Note about waiver wire
            summary.append("=== WAIVER WIRE / FREE AGENTS ===")
            summary.append("Note: Please check your Yahoo Fantasy league page directly for")
            summary.append("accurate waiver wire information (Yahoo API has limitations).")
            summary.append("")

            return "\n".join(summary)
        except Exception as e:
            return f"Error generating team summary: {e}"

    def get_roster_with_recent_performance(self, team_id: Optional[str] = None, weeks_back: int = 3) -> List[Dict[str, Any]]:
        """Get roster with recent weekly performance data for trend analysis."""
        try:
            roster = self.get_roster(team_id)
            league_info = self.get_league_info()

            if not league_info or not roster:
                return roster

            current_week = league_info.get('current_week', 1)

            # Add recent weekly stats for each player
            for player in roster:
                player_key = player.get('player_id')
                if not player_key:
                    continue

                # Get stats for the last N weeks
                recent_weeks = []
                for week_offset in range(1, weeks_back + 1):
                    week = current_week - week_offset
                    if week > 0:
                        weekly_stats = self.get_player_weekly_stats(player_key, week)
                        if weekly_stats:
                            recent_weeks.append(weekly_stats)

                if recent_weeks:
                    player['recent_performance'] = recent_weeks

                    # Calculate average points over recent weeks
                    points_list = [w.get('points', 0) for w in recent_weeks if 'points' in w]
                    if points_list:
                        player['avg_recent_points'] = sum(points_list) / len(points_list)

            return roster
        except Exception as e:
            print(f"Error fetching roster with recent performance: {e}")
            return self.get_roster(team_id)  # Fallback to regular roster

    def _format_player_line(self, player: Dict[str, Any]) -> str:
        """Format a single player line with stats and projections."""
        status = f" ({player['status']})" if player.get('status') and player['status'] != 'Healthy' else ''
        position = player.get('selected_position', player.get('position', 'N/A'))
        name = player.get('name', 'Unknown')
        team = player.get('team', '')

        # Build the base line
        line = f"  {position}: {name} - {team}{status}"

        # Add current week points if available
        if 'points_current_week' in player:
            line += f" | Points: {player['points_current_week']:.1f}"

        # Add projected points if available
        if 'projected_points' in player:
            line += f" (Proj: {player['projected_points']:.1f})"

        # Add key stats summary if available
        if 'current_stats' in player and player['current_stats']:
            stats = player['current_stats']
            stat_parts = []

            # For QBs
            if 'passing_yards' in stats and stats['passing_yards'] > 0:
                stat_parts.append(f"{int(stats['passing_yards'])} pass yds")
            if 'passing_tds' in stats and stats['passing_tds'] > 0:
                stat_parts.append(f"{int(stats['passing_tds'])} pass TD")

            # For RBs/WRs/TEs
            if 'rushing_yards' in stats and stats['rushing_yards'] > 0:
                stat_parts.append(f"{int(stats['rushing_yards'])} rush yds")
            if 'rushing_tds' in stats and stats['rushing_tds'] > 0:
                stat_parts.append(f"{int(stats['rushing_tds'])} rush TD")
            if 'receptions' in stats and stats['receptions'] > 0:
                stat_parts.append(f"{int(stats['receptions'])} rec")
            if 'receiving_yards' in stats and stats['receiving_yards'] > 0:
                stat_parts.append(f"{int(stats['receiving_yards'])} rec yds")
            if 'receiving_tds' in stats and stats['receiving_tds'] > 0:
                stat_parts.append(f"{int(stats['receiving_tds'])} rec TD")

            # Negative stats
            if 'interceptions' in stats and stats['interceptions'] > 0:
                stat_parts.append(f"{int(stats['interceptions'])} INT")
            if 'fumbles_lost' in stats and stats['fumbles_lost'] > 0:
                stat_parts.append(f"{int(stats['fumbles_lost'])} FUM")

            if stat_parts:
                line += f"\n      Stats: {', '.join(stat_parts)}"

        # Add ownership percentage if available
        if 'percent_owned' in player and player['percent_owned']:
            try:
                ownership = float(player['percent_owned'])
                line += f"\n      Ownership: {ownership:.1f}%"
            except (ValueError, TypeError):
                pass

        return line
