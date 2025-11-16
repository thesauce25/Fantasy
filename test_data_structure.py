#!/usr/bin/env python3
"""
Test script to see actual data structure
"""

from yfpy.query import YahooFantasySportsQuery
import os
from dotenv import load_dotenv

load_dotenv()

yahoo_query = YahooFantasySportsQuery(
    league_id=os.getenv('YAHOO_LEAGUE_ID'),
    game_code=os.getenv('YAHOO_GAME_CODE', 'nfl'),
    yahoo_consumer_key=os.getenv('YAHOO_CLIENT_ID'),
    yahoo_consumer_secret=os.getenv('YAHOO_CLIENT_SECRET'),
)

print("=" * 60)
print("LEAGUE INFO")
print("=" * 60)
league = yahoo_query.get_league_info()
print(f"Name: {league.name}")
print(f"Season: {league.season}")
print(f"Current Week: {league.current_week}")
print(f"Num Teams: {league.num_teams}")

print("\n" + "=" * 60)
print("TEAMS")
print("=" * 60)
teams = yahoo_query.get_league_teams()
for i, team in enumerate(teams[:3], 1):
    print(f"\nTeam {i}:")
    print(f"  Name: {team.name}")
    print(f"  Team ID: {team.team_id}")
    print(f"  Team Key: {team.team_key}")
    print(f"  Managers: {team.managers if hasattr(team, 'managers') else 'N/A'}")

    # Check for standings info
    if hasattr(team, 'team_standings'):
        print(f"  Has team_standings: Yes")
        standings = team.team_standings
        print(f"    Standings attributes: {list(vars(standings).keys())[:10]}")

    # Check for points
    if hasattr(team, 'team_points'):
        print(f"  Has team_points: Yes")
        points = team.team_points
        print(f"    Points attributes: {list(vars(points).keys())[:10]}")

print("\n" + "=" * 60)
print("STANDINGS")
print("=" * 60)
standings = yahoo_query.get_league_standings()
print(f"Type: {type(standings)}")
print(f"Attributes: {list(vars(standings).keys())}")
if hasattr(standings, 'teams'):
    print(f"Has teams attribute: Yes")
    print(f"Number of teams: {len(standings.teams) if standings.teams else 0}")

print("\n" + "=" * 60)
print("TEAM MATCHUPS")
print("=" * 60)
try:
    # Get first team's matchups
    first_team = teams[0]
    matchups = yahoo_query.get_team_matchups(team_id=first_team.team_id)
    print(f"Type: {type(matchups)}")
    print(f"Attributes: {list(vars(matchups).keys())[:10]}")
except Exception as e:
    print(f"Error: {e}")

print("\n" + "=" * 60)
print("TEAM ROSTER")
print("=" * 60)
try:
    roster = yahoo_query.get_team_roster_by_week(
        team_id=teams[0].team_id,
        chosen_week='current'
    )
    print(f"Type: {type(roster)}")
    if roster:
        print(f"Number of players: {len(roster)}")
        if len(roster) > 0:
            player = roster[0]
            print(f"\nFirst player:")
            print(f"  Type: {type(player)}")
            print(f"  Attributes: {list(vars(player).keys())[:15]}")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
