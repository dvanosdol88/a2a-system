#!/usr/bin/env python3
"""
Quick GitHub Token Setup for A2A
Non-interactive version for command line
"""

import os
import sys
from github_manager import GitHubManager

def setup_token_from_args():
    """Set up GitHub token from command line argument"""
    if len(sys.argv) < 2:
        print("Usage: python3 quick_token_setup.py <your_github_token>")
        print("\nTo create a token:")
        print("1. Go to: https://github.com/settings/tokens")
        print("2. Click 'Generate new token (classic)'")
        print("3. Select scopes: repo, workflow, write:packages")
        print("4. Copy the token and run: python3 quick_token_setup.py <token>")
        return False
    
    token = sys.argv[1].strip()
    
    print("🔐 A2A GitHub Token Setup")
    print("=" * 40)
    
    # Validate token format
    if not token.startswith(("ghp_", "github_pat_")):
        print("⚠️  Warning: Token doesn't look like a GitHub Personal Access Token")
        print("   Expected format: ghp_... or github_pat_...")
    
    # Test the token
    print("🧪 Testing token...")
    github = GitHubManager(token)
    
    # Test authentication
    auth_result = github.test_authentication()
    print(f"Auth: {auth_result['message']}")
    
    if not auth_result["success"]:
        print("❌ Token authentication failed")
        return False
    
    # Test repository access
    repo_result = github.get_repo_info()
    print(f"Repo: {repo_result['message']}")
    
    if not repo_result["success"]:
        print("❌ Repository access failed - check token permissions")
        return False
    
    # Set environment variable
    os.environ["GITHUB_TOKEN"] = token
    print("✅ Token set for current session")
    
    # Show success info
    print("\n🎉 GitHub token setup complete!")
    print(f"👤 Authenticated as: {auth_result.get('user', 'Unknown')}")
    print(f"📁 Repository: {repo_result.get('name', 'Unknown')}")
    print(f"🔒 Private: {repo_result.get('private', 'Unknown')}")
    
    print("\n💡 To make permanent:")
    print(f"   export GITHUB_TOKEN='{token}'")
    print("   # Add to ~/.bashrc or ~/.profile")
    
    return True

if __name__ == "__main__":
    success = setup_token_from_args()
    if success:
        print("\n🎯 Ready to test A2A GitHub integration!")
        print("Run: python3 -c \"from github_manager import GitHubManager; GitHubManager().test_authentication()\"")
    else:
        sys.exit(1)