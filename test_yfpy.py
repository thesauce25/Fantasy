#!/usr/bin/env python3
"""
Test script to discover YFPY 17.0 API methods and data structures
"""

from yfpy.query import YahooFantasySportsQuery
import os
from dotenv import load_dotenv

load_dotenv()

print("=" * 60)
print("YFPY 17.0 API Inspector")
print("=" * 60)

# List all methods available
print("\nAvailable methods in YahooFantasySportsQuery:")
print("-" * 60)
methods = [method for method in dir(YahooFantasySportsQuery) if not method.startswith('_') and callable(getattr(YahooFantasySportsQuery, method))]

# Filter to common ones
relevant_methods = [m for m in methods if any(keyword in m.lower() for keyword in ['team', 'league', 'roster', 'matchup', 'standing', 'player'])]

for method in sorted(relevant_methods):
    print(f"  - {method}")

print("\n" * 2)
print("=" * 60)
print("Testing with your league...")
print("=" * 60)

try:
    yahoo_query = YahooFantasySportsQuery(
        league_id=os.getenv('YAHOO_LEAGUE_ID'),
        game_code=os.getenv('YAHOO_GAME_CODE', 'nfl'),
        yahoo_consumer_key=os.getenv('YAHOO_CLIENT_ID'),
        yahoo_consumer_secret=os.getenv('YAHOO_CLIENT_SECRET'),
    )

    print("\n1. Testing get_league_info()...")
    league = yahoo_query.get_league_info()
    print(f"   Type: {type(league)}")
    print(f"   Attributes: {dir(league)[:10]}...")  # First 10 attributes

    print("\n2. Testing get_league_teams()...")
    teams = yahoo_query.get_league_teams()
    print(f"   Type: {type(teams)}")
    if teams:
        print(f"   First team type: {type(teams[0]) if isinstance(teams, list) else 'N/A'}")
        if isinstance(teams, list) and len(teams) > 0:
            print(f"   First team attributes: {list(vars(teams[0]).keys())[:5] if hasattr(teams[0], '__dict__') else 'No __dict__'}")

    print("\n3. Testing get_league_standings()...")
    standings = yahoo_query.get_league_standings()
    print(f"   Type: {type(standings)}")
    if standings:
        print(f"   First item type: {type(standings[0]) if isinstance(standings, list) else 'N/A'}")

    print("\n4. Looking for matchup methods...")
    matchup_methods = [m for m in methods if 'matchup' in m.lower()]
    print(f"   Matchup methods: {matchup_methods}")

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
