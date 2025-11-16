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
        """Get available free agents using multiple data strategies.

        This method uses a multi-strategy approach:
        1. Fetches league players from Yahoo API
        2. Filters for available players (not on any roster)
        3. Cross-references with recent transactions
        4. Validates data quality to filter stale information

        Args:
            position: Filter by position (QB, RB, WR, TE, K, DEF)
            count: Maximum number of players to return (default: 25)

        Returns:
            List of available players sorted by relevance
        """
        try:
            print(f"Fetching available free agents{f' at position {position}' if position else ''}...")

            # Strategy 1: Get league players
            available_players = self._get_available_players_from_api(count * 2)  # Get extra to filter

            # Strategy 2: Enrich with transaction data
            available_players = self._enrich_with_transaction_data(available_players)

            # Filter by position if specified
            if position:
                available_players = [
                    p for p in available_players
                    if p.get('position', '').upper() == position.upper()
                ]

            # Sort by relevance (percent owned, recent activity)
            available_players = self._sort_players_by_relevance(available_players)

            # Limit to requested count
            result = available_players[:count]

            print(f"✓ Found {len(result)} available free agents")
            return result

        except Exception as e:
            print(f"Error fetching free agents: {e}")
            import traceback
            traceback.print_exc()
            return []

    def _get_available_players_from_api(self, limit: int) -> List[Dict[str, Any]]:
        """Fetch players from Yahoo API and filter for available ones."""
        try:
            # Get players from the league
            players_obj = self.yahoo_query.get_league_players(
                player_count_limit=limit,
                player_count_start=0
            )

            if not players_obj:
                print("No player data returned from Yahoo API")
                return []

            def decode_if_bytes(val):
                return val.decode('utf-8') if isinstance(val, bytes) else val

            available = []
            for player in players_obj:
                try:
                    # Check if player is available (not owned by any team)
                    is_available = False
                    ownership_type = None

                    if hasattr(player, 'ownership') and player.ownership:
                        ownership_type = decode_if_bytes(player.ownership.ownership_type) if hasattr(player.ownership, 'ownership_type') else None
                        is_available = ownership_type in ['waivers', 'freeagents', None]
                    else:
                        # If no ownership data, assume available
                        is_available = True

                    if not is_available:
                        continue

                    # Extract player info
                    player_info = {
                        'player_id': player.player_id if hasattr(player, 'player_id') else None,
                        'name': decode_if_bytes(player.name.full) if hasattr(player, 'name') and hasattr(player.name, 'full') else 'Unknown',
                        'position': decode_if_bytes(player.primary_position) if hasattr(player, 'primary_position') else 'N/A',
                        'team': decode_if_bytes(player.editorial_team_abbr) if hasattr(player, 'editorial_team_abbr') else '',
                        'ownership_type': ownership_type or 'available',
                        'percent_owned': 0.0,
                    }

                    # Get percent owned if available
                    if hasattr(player, 'percent_owned') and player.percent_owned:
                        if hasattr(player.percent_owned, 'value'):
                            player_info['percent_owned'] = float(player.percent_owned.value)
                        else:
                            player_info['percent_owned'] = float(player.percent_owned)

                    # Get bye week
                    if hasattr(player, 'bye_weeks') and player.bye_weeks:
                        player_info['bye_week'] = player.bye_weeks.week if hasattr(player.bye_weeks, 'week') else None

                    # Get status (injury, etc.)
                    if hasattr(player, 'status'):
                        player_info['status'] = decode_if_bytes(player.status) if player.status else 'Healthy'

                    available.append(player_info)

                except Exception as e:
                    print(f"Error processing player: {e}")
                    continue

            return available

        except Exception as e:
            print(f"Error in _get_available_players_from_api: {e}")
            import traceback
            traceback.print_exc()
            return []

    def _enrich_with_transaction_data(self, players: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Enrich player data with recent transaction information."""
        try:
            # Get recent league transactions
            transactions = self.yahoo_query.get_league_transactions()

            if not transactions:
                return players

            def decode_if_bytes(val):
                return val.decode('utf-8') if isinstance(val, bytes) else val

            # Track recently dropped players (good pickup candidates)
            recently_dropped = {}
            recently_added = set()

            for transaction in transactions[:50]:  # Check last 50 transactions
                try:
                    trans_type = decode_if_bytes(transaction.type) if hasattr(transaction, 'type') else None

                    if trans_type in ['add', 'drop', 'add/drop']:
                        if hasattr(transaction, 'players') and transaction.players:
                            for player in transaction.players:
                                player_name = decode_if_bytes(player.name.full) if hasattr(player, 'name') and hasattr(player.name, 'full') else None

                                # Check transaction type for this specific player
                                if hasattr(player, 'transaction_data') and player.transaction_data:
                                    trans_data = player.transaction_data
                                    player_trans_type = decode_if_bytes(trans_data.type) if hasattr(trans_data, 'type') else None

                                    if player_trans_type == 'drop':
                                        recently_dropped[player_name] = True
                                    elif player_trans_type == 'add':
                                        recently_added.add(player_name)

                except Exception as e:
                    continue

            # Enrich player data
            for player in players:
                player['recently_dropped'] = player.get('name') in recently_dropped
                player['recently_added'] = player.get('name') in recently_added

            return players

        except Exception as e:
            print(f"Error enriching with transaction data: {e}")
            # Return players without enrichment if transactions fail
            return players

    def _sort_players_by_relevance(self, players: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Sort players by relevance (percent owned, recent drops, etc.)."""
        # Filter out obviously stale/invalid data
        filtered_players = []

        # Known retired/invalid players (common in stale Yahoo API data)
        stale_indicators = [
            'Marcedes Lewis', 'Jimmy Graham', 'Randall Cobb', 'Brian Hoyer',
            'Blaine Gabbert', 'Matt Prater', 'Nick Folk', 'Josh Johnson'
        ]

        for player in players:
            player_name = player.get('name', '')

            # Skip known stale players
            if any(stale in player_name for stale in stale_indicators):
                continue

            # Skip players with suspicious 0% ownership AND common positions (likely stale)
            # Keep kickers/defenses with 0% as they might be legitimately unowned
            pos = player.get('position', '')
            if player.get('percent_owned', 0) == 0 and pos in ['QB', 'RB', 'WR', 'TE']:
                # Only keep if recently dropped (active transaction)
                if not player.get('recently_dropped'):
                    continue

            filtered_players.append(player)

        def player_score(player):
            score = 0

            # Percent owned is the primary indicator
            score += player.get('percent_owned', 0) * 10

            # Recently dropped players might be good pickups
            if player.get('recently_dropped'):
                score += 50

            # Penalize recently added (might not be available)
            if player.get('recently_added'):
                score -= 100

            # Penalize injured players
            status = player.get('status', '').upper()
            if status in ['OUT', 'IR', 'SUSP']:
                score -= 30
            elif status in ['DOUBTFUL', 'QUESTIONABLE']:
                score -= 10

            return score

        return sorted(filtered_players, key=player_score, reverse=True)

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
                summary.append("")

            # Waiver wire / Free agents
            summary.append("=== WAIVER WIRE / FREE AGENTS ===")
            try:
                free_agents = self.get_free_agents(count=15)
                if free_agents and len(free_agents) > 0:
                    # Group by position
                    by_position = {}
                    for player in free_agents:
                        pos = player.get('position', 'N/A')
                        if pos not in by_position:
                            by_position[pos] = []
                        by_position[pos].append(player)

                    # Show top players by position
                    found_any = False
                    for pos in ['QB', 'RB', 'WR', 'TE']:
                        if pos in by_position:
                            summary.append(f"\n{pos}:")
                            for player in by_position[pos][:3]:  # Top 3 per position
                                status = f" ({player['status']})" if player.get('status') and player['status'] != 'Healthy' else ''
                                owned = player.get('percent_owned', 0)
                                recently_dropped = " 🔥" if player.get('recently_dropped') else ''
                                summary.append(f"  {player['name']} - {player['team']} ({owned:.0f}% owned){status}{recently_dropped}")
                                found_any = True

                    if not found_any:
                        summary.append("\n⚠ Yahoo API returned stale player data (retired players, wrong teams)")
                        summary.append("Please check Yahoo Fantasy website for accurate waiver wire.")
                    summary.append("")
                else:
                    summary.append("\n⚠ Yahoo API returned stale player data (retired players, wrong teams)")
                    summary.append("Please check Yahoo Fantasy website for accurate waiver wire.")
                    summary.append("\nNote: The Yahoo API has known issues with player data freshness.")
                    summary.append("Your league's actual waiver wire will show current, relevant players.")
                    summary.append("")
            except Exception as e:
                summary.append(f"\nUnable to fetch free agents: {e}")
                summary.append("Please check Yahoo Fantasy website for current waiver wire.")
                summary.append("")

            return "\n".join(summary)
        except Exception as e:
            return f"Error generating team summary: {e}"
