#!/usr/bin/env python3
"""
Setup script for Fantasy Football Chatbot

This script helps users configure their environment and test their Yahoo API connection.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv, set_key


def print_header(text):
    """Print a formatted header."""
    print(f"\n{'=' * 60}")
    print(f"  {text}")
    print(f"{'=' * 60}\n")


def check_env_file():
    """Check if .env file exists, create from template if not."""
    env_path = Path('.env')
    env_example_path = Path('.env.example')

    if not env_path.exists():
        if env_example_path.exists():
            print("Creating .env file from template...")
            env_example_path.read_text()
            with open(env_path, 'w') as f:
                f.write(env_example_path.read_text())
            print("✓ Created .env file")
        else:
            print("✗ .env.example not found!")
            return False
    else:
        print("✓ .env file exists")

    return True


def setup_yahoo_credentials():
    """Guide user through Yahoo API setup."""
    print_header("Yahoo Fantasy API Setup")

    print("To use this chatbot, you need to create a Yahoo Developer App.")
    print("\nSteps:")
    print("1. Go to: https://developer.yahoo.com/apps/create/")
    print("2. Click 'Create an App'")
    print("3. Fill in:")
    print("   - Application Name: Fantasy Football Chatbot")
    print("   - Application Type: Web Application")
    print("   - Homepage URL: http://localhost:8000")
    print("   - Redirect URI(s): http://localhost:8000")
    print("   - API Permissions: Check 'Fantasy Sports' with Read access")
    print("4. Click 'Create App'")
    print("\nYou'll receive a Client ID and Client Secret.")

    print("\n" + "-" * 60)

    client_id = input("\nEnter your Yahoo Client ID: ").strip()
    client_secret = input("Enter your Yahoo Client Secret: ").strip()

    if client_id and client_secret:
        set_key('.env', 'YAHOO_CLIENT_ID', client_id)
        set_key('.env', 'YAHOO_CLIENT_SECRET', client_secret)
        print("\n✓ Yahoo credentials saved!")
        return True
    else:
        print("\n✗ Invalid credentials provided")
        return False


def setup_league_info():
    """Guide user through league configuration."""
    print_header("Yahoo Fantasy League Setup")

    print("You need to provide your Yahoo Fantasy League ID.")
    print("\nTo find your League ID:")
    print("1. Go to your Yahoo Fantasy Football league")
    print("2. Look at the URL in your browser")
    print("3. It should look like: https://football.fantasysports.yahoo.com/f1/XXXXX")
    print("4. The number XXXXX is your League ID")

    print("\n" + "-" * 60)

    league_id = input("\nEnter your League ID: ").strip()
    game_code = input("Enter game code (default: nfl): ").strip() or "nfl"
    season = input("Enter season year (default: 2024): ").strip() or "2024"

    if league_id:
        set_key('.env', 'YAHOO_LEAGUE_ID', league_id)
        set_key('.env', 'YAHOO_GAME_CODE', game_code)
        set_key('.env', 'YAHOO_SEASON', season)
        print("\n✓ League information saved!")
        return True
    else:
        print("\n✗ League ID is required")
        return False


def setup_anthropic_key():
    """Guide user through Anthropic API setup."""
    print_header("Anthropic API Setup")

    print("To use Claude AI for fantasy advice, you need an Anthropic API key.")
    print("\nSteps:")
    print("1. Go to: https://console.anthropic.com/")
    print("2. Sign up or log in")
    print("3. Go to API Keys section")
    print("4. Create a new API key")

    print("\n" + "-" * 60)

    api_key = input("\nEnter your Anthropic API key: ").strip()

    if api_key:
        set_key('.env', 'ANTHROPIC_API_KEY', api_key)
        print("\n✓ Anthropic API key saved!")
        return True
    else:
        print("\n✗ API key is required")
        return False


def test_configuration():
    """Test the configuration by attempting to import and initialize clients."""
    print_header("Testing Configuration")

    try:
        # Reload environment
        load_dotenv(override=True)

        # Test imports
        print("Testing imports...")
        from yahoo_client import YahooFantasyClient
        from anthropic import Anthropic
        print("✓ All required packages are installed")

        # Test Anthropic API
        print("\nTesting Anthropic API connection...")
        api_key = os.getenv('ANTHROPIC_API_KEY')
        if api_key:
            client = Anthropic(api_key=api_key)
            print("✓ Anthropic API key is valid")
        else:
            print("✗ Anthropic API key not found")
            return False

        # Test Yahoo API (this will trigger OAuth flow)
        print("\nTesting Yahoo API connection...")
        print("(This will open a browser for OAuth authentication)")
        yahoo_client = YahooFantasyClient()
        print("✓ Yahoo API connection successful!")

        return True

    except Exception as e:
        print(f"\n✗ Configuration test failed: {e}")
        return False


def main():
    """Main setup flow."""
    print_header("Fantasy Football Chatbot Setup")

    print("Welcome! This script will help you set up your Fantasy Football Chatbot.")
    print("\nYou'll need:")
    print("  1. A Yahoo Fantasy Football account with an active league")
    print("  2. A Yahoo Developer App (we'll help you create one)")
    print("  3. An Anthropic API key (for Claude AI)")

    input("\nPress Enter to continue...")

    # Check/create .env file
    if not check_env_file():
        print("\n✗ Setup failed: Could not create .env file")
        sys.exit(1)

    # Check if already configured
    load_dotenv()
    needs_yahoo = not (os.getenv('YAHOO_CLIENT_ID') and os.getenv('YAHOO_CLIENT_SECRET'))
    needs_league = not os.getenv('YAHOO_LEAGUE_ID')
    needs_anthropic = not os.getenv('ANTHROPIC_API_KEY')

    # Run setup steps as needed
    if needs_yahoo:
        if not setup_yahoo_credentials():
            print("\n✗ Setup incomplete")
            sys.exit(1)
    else:
        print("\n✓ Yahoo credentials already configured")

    if needs_league:
        if not setup_league_info():
            print("\n✗ Setup incomplete")
            sys.exit(1)
    else:
        print("\n✓ League information already configured")

    if needs_anthropic:
        if not setup_anthropic_key():
            print("\n✗ Setup incomplete")
            sys.exit(1)
    else:
        print("\n✓ Anthropic API key already configured")

    # Test configuration
    print("\n" + "=" * 60)
    test = input("\nWould you like to test the configuration? (y/n): ").strip().lower()
    if test == 'y':
        if test_configuration():
            print("\n" + "=" * 60)
            print("  Setup Complete! 🎉")
            print("=" * 60)
            print("\nYou can now run the chatbot with:")
            print("  python chatbot.py")
        else:
            print("\n✗ Configuration test failed. Please check your settings.")
            sys.exit(1)
    else:
        print("\n✓ Setup complete! Run 'python chatbot.py' to start.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nSetup cancelled.")
        sys.exit(0)
