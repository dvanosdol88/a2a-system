#!/usr/bin/env python3
"""
GitHub Token Setup for A2A Agents
Helps configure GitHub Personal Access Tokens
"""

import os
import getpass
from pathlib import Path
from github_manager import GitHubManager

def setup_github_token():
    """Interactive GitHub token setup"""
    print("🔐 A2A GitHub Token Setup")
    print("=" * 40)
    
    # Check if token already exists
    current_token = os.getenv("GITHUB_TOKEN")
    if current_token:
        print(f"✅ GITHUB_TOKEN already set: {current_token[:8]}...")
        test_existing = input("Test existing token? (y/n): ").lower().strip()
        if test_existing == 'y':
            github = GitHubManager(current_token)
            auth_result = github.test_authentication()
            repo_result = github.get_repo_info()
            print(f"Auth: {auth_result['message']}")
            print(f"Repo: {repo_result['message']}")
            if auth_result["success"] and repo_result["success"]:
                print("✅ Existing token works perfectly!")
                return current_token
            else:
                print("❌ Existing token needs to be updated")
    
    print("\n📋 To create a GitHub Personal Access Token:")
    print("1. Go to: https://github.com/settings/tokens")
    print("2. Click 'Generate new token (classic)'")
    print("3. Set expiration (recommend 90 days)")
    print("4. Select scopes:")
    print("   ✅ repo (Full control of private repositories)")
    print("   ✅ workflow (Update GitHub Action workflows)")
    print("   ✅ write:packages (Write packages to GitHub Package Registry)")
    print("5. Click 'Generate token'")
    print("6. Copy the token (it won't be shown again!)")
    
    # Get token from user
    print("\n🔑 Enter your GitHub Personal Access Token:")
    token = getpass.getpass("Token: ").strip()
    
    if not token:
        print("❌ No token provided")
        return None
    
    if not token.startswith("ghp_") and not token.startswith("github_pat_"):
        print("⚠️  Warning: Token doesn't look like a GitHub Personal Access Token")
        proceed = input("Continue anyway? (y/n): ").lower().strip()
        if proceed != 'y':
            return None
    
    # Test the token
    print("\n🧪 Testing token...")
    github = GitHubManager(token)
    
    auth_result = github.test_authentication()
    print(f"Auth: {auth_result['message']}")
    
    if not auth_result["success"]:
        print("❌ Token authentication failed")
        return None
    
    repo_result = github.get_repo_info()
    print(f"Repo: {repo_result['message']}")
    
    if not repo_result["success"]:
        print("❌ Repository access failed - check token permissions")
        return None
    
    # Save token to environment
    print("\n💾 Saving token...")
    
    # Option 1: Export for current session
    os.environ["GITHUB_TOKEN"] = token
    print("✅ Token set for current session")
    
    # Option 2: Add to shell profile
    save_permanent = input("Save to ~/.bashrc for permanent use? (y/n): ").lower().strip()
    if save_permanent == 'y':
        bashrc_path = Path.home() / ".bashrc"
        with open(bashrc_path, "a") as f:
            f.write(f"\n# A2A GitHub Token\nexport GITHUB_TOKEN='{token}'\n")
        print("✅ Token added to ~/.bashrc")
        print("💡 Run 'source ~/.bashrc' or restart terminal to activate")
    
    print("\n🎉 GitHub token setup complete!")
    print(f"👤 Authenticated as: {auth_result.get('user', 'Unknown')}")
    print(f"📁 Repository: {repo_result.get('name', 'Unknown')}")
    print(f"🔒 Private: {repo_result.get('private', 'Unknown')}")
    
    return token

def verify_setup():
    """Verify GitHub setup is working"""
    print("\n🔍 Verifying A2A GitHub setup...")
    
    github = GitHubManager()
    
    # Test auth
    auth_result = github.test_authentication()
    if auth_result["success"]:
        print(f"✅ Authentication: {auth_result['message']}")
    else:
        print(f"❌ Authentication: {auth_result['message']}")
        return False
    
    # Test repo access
    repo_result = github.get_repo_info()
    if repo_result["success"]:
        print(f"✅ Repository: {repo_result['message']}")
    else:
        print(f"❌ Repository: {repo_result['message']}")
        return False
    
    # Test issue listing
    issues_result = github.get_issues()
    if issues_result["success"]:
        print(f"✅ Issues API: Found {issues_result['count']} issues")
    else:
        print(f"❌ Issues API: {issues_result['message']}")
        return False
    
    print("\n🎯 A2A GitHub integration ready for Scenario 3!")
    return True

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "verify":
        verify_setup()
    else:
        token = setup_github_token()
        if token:
            verify_setup()