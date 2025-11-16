#!/usr/bin/env python3
"""
Test script to verify trade proposal features work correctly
"""

from yahoo_client import YahooFantasyClient
from dotenv import load_dotenv

def test_trade_features():
    """Test the new trade-related methods."""
    print("="*60)
    print("Testing Trade Proposal Features")
    print("="*60)

    load_dotenv()

    try:
        print("\n1. Initializing Yahoo client...")
        client = YahooFantasyClient()
        print("✓ Client initialized successfully")

        print("\n2. Testing get_all_league_teams()...")
        teams = client.get_all_league_teams()
        print(f"✓ Found {len(teams)} teams in league:")
        for team in teams[:3]:  # Show first 3
            record = f"{team['wins']}-{team['losses']}-{team['ties']}"
            print(f"   - {team['name']} ({record}) - Team ID: {team['team_id']}")

        print("\n3. Testing get_all_teams_rosters()...")
        all_rosters = client.get_all_teams_rosters()
        print(f"✓ Fetched rosters for {len(all_rosters)} teams")

        # Show sample roster
        if all_rosters:
            sample_team = list(all_rosters.keys())[0]
            roster_data = all_rosters[sample_team]
            print(f"\n   Sample team: {sample_team}")
            print(f"   - Record: {roster_data['record']}")
            print(f"   - Roster size: {len(roster_data['roster'])} players")
            if roster_data['roster']:
                print(f"   - First player: {roster_data['roster'][0]['name']}")

        print("\n4. Testing format_trade_context()...")
        trade_context = client.format_trade_context()
        lines = trade_context.split('\n')
        print(f"✓ Generated trade context ({len(lines)} lines)")
        print(f"   First few lines:")
        for line in lines[:10]:
            print(f"   {line}")

        print("\n" + "="*60)
        print("✓ All tests passed successfully!")
        print("="*60)
        print("\nThe chatbot should now be able to:")
        print("- Fetch all teams in the league")
        print("- Get rosters for all teams")
        print("- Propose specific trades based on league data")

    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_trade_features()
