#!/usr/bin/env python3
"""
GitHub API Manager for A2A Agents
Handles authentication, API calls, and GitHub operations
"""

import requests
import json
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any

class GitHubManager:
    def __init__(self, token: Optional[str] = None, repo_owner: str = "dvanosdol88", repo_name: str = "a2a-system"):
        """Initialize GitHub API manager"""
        self.token = token or os.getenv("GITHUB_TOKEN")
        self.repo_owner = repo_owner
        self.repo_name = repo_name
        self.base_url = "https://api.github.com"
        self.repo_url = f"{self.base_url}/repos/{repo_owner}/{repo_name}"
        
        if not self.token:
            print("⚠️  WARNING: No GitHub token provided. Set GITHUB_TOKEN environment variable.")
    
    def _headers(self) -> Dict[str, str]:
        """Get request headers with authentication"""
        headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "A2A-System/1.0"
        }
        if self.token:
            headers["Authorization"] = f"token {self.token}"
        return headers
    
    def _make_request(self, method: str, url: str, data: Optional[Dict] = None) -> requests.Response:
        """Make authenticated GitHub API request"""
        try:
            response = requests.request(
                method=method,
                url=url,
                headers=self._headers(),
                json=data,
                timeout=30
            )
            return response
        except Exception as e:
            print(f"❌ GitHub API request failed: {e}")
            raise
    
    def test_authentication(self) -> Dict[str, Any]:
        """Test GitHub API authentication"""
        try:
            response = self._make_request("GET", f"{self.base_url}/user")
            if response.status_code == 200:
                user_data = response.json()
                return {
                    "success": True,
                    "user": user_data.get("login"),
                    "name": user_data.get("name"),
                    "message": f"✅ Authenticated as {user_data.get('login')}"
                }
            else:
                return {
                    "success": False,
                    "status_code": response.status_code,
                    "message": f"❌ Authentication failed: {response.status_code}"
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"❌ Authentication error: {str(e)}"
            }
    
    def get_repo_info(self) -> Dict[str, Any]:
        """Get repository information"""
        try:
            response = self._make_request("GET", self.repo_url)
            if response.status_code == 200:
                repo_data = response.json()
                return {
                    "success": True,
                    "name": repo_data.get("name"),
                    "private": repo_data.get("private"),
                    "default_branch": repo_data.get("default_branch"),
                    "clone_url": repo_data.get("clone_url"),
                    "ssh_url": repo_data.get("ssh_url"),
                    "message": f"✅ Repository access confirmed: {repo_data.get('name')}"
                }
            else:
                return {
                    "success": False,
                    "status_code": response.status_code,
                    "message": f"❌ Repository access failed: {response.status_code}"
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"❌ Repository error: {str(e)}"
            }
    
    def create_issue(self, title: str, body: str, labels: List[str] = None, assignees: List[str] = None) -> Dict[str, Any]:
        """Create a GitHub issue"""
        data = {
            "title": title,
            "body": body
        }
        if labels:
            data["labels"] = labels
        if assignees:
            data["assignees"] = assignees
        
        try:
            response = self._make_request("POST", f"{self.repo_url}/issues", data)
            if response.status_code == 201:
                issue_data = response.json()
                return {
                    "success": True,
                    "issue_number": issue_data.get("number"),
                    "html_url": issue_data.get("html_url"),
                    "message": f"✅ Issue created: #{issue_data.get('number')}"
                }
            else:
                return {
                    "success": False,
                    "status_code": response.status_code,
                    "message": f"❌ Issue creation failed: {response.status_code}"
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"❌ Issue creation error: {str(e)}"
            }
    
    def create_pr(self, title: str, head: str, base: str, body: str = "") -> Dict[str, Any]:
        """Create a pull request"""
        data = {
            "title": title,
            "head": head,
            "base": base,
            "body": body
        }
        
        try:
            response = self._make_request("POST", f"{self.repo_url}/pulls", data)
            if response.status_code == 201:
                pr_data = response.json()
                return {
                    "success": True,
                    "pr_number": pr_data.get("number"),
                    "html_url": pr_data.get("html_url"),
                    "message": f"✅ Pull request created: #{pr_data.get('number')}"
                }
            else:
                return {
                    "success": False,
                    "status_code": response.status_code,
                    "message": f"❌ PR creation failed: {response.status_code}"
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"❌ PR creation error: {str(e)}"
            }
    
    def comment_on_issue(self, issue_number: int, comment: str) -> Dict[str, Any]:
        """Add comment to issue or PR"""
        data = {"body": comment}
        
        try:
            response = self._make_request("POST", f"{self.repo_url}/issues/{issue_number}/comments", data)
            if response.status_code == 201:
                comment_data = response.json()
                return {
                    "success": True,
                    "comment_id": comment_data.get("id"),
                    "html_url": comment_data.get("html_url"),
                    "message": f"✅ Comment added to #{issue_number}"
                }
            else:
                return {
                    "success": False,
                    "status_code": response.status_code,
                    "message": f"❌ Comment failed: {response.status_code}"
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"❌ Comment error: {str(e)}"
            }
    
    def get_issues(self, state: str = "open", labels: str = None) -> Dict[str, Any]:
        """Get repository issues"""
        params = {"state": state}
        if labels:
            params["labels"] = labels
        
        try:
            url = f"{self.repo_url}/issues"
            if params:
                param_str = "&".join([f"{k}={v}" for k, v in params.items()])
                url += f"?{param_str}"
            
            response = self._make_request("GET", url)
            if response.status_code == 200:
                issues = response.json()
                return {
                    "success": True,
                    "count": len(issues),
                    "issues": issues,
                    "message": f"✅ Found {len(issues)} issues"
                }
            else:
                return {
                    "success": False,
                    "status_code": response.status_code,
                    "message": f"❌ Issues fetch failed: {response.status_code}"
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"❌ Issues fetch error: {str(e)}"
            }
    
    def get_pull_requests(self, state: str = "open") -> Dict[str, Any]:
        """Get repository pull requests"""
        try:
            response = self._make_request("GET", f"{self.repo_url}/pulls?state={state}")
            if response.status_code == 200:
                prs = response.json()
                return {
                    "success": True,
                    "count": len(prs),
                    "pull_requests": prs,
                    "message": f"✅ Found {len(prs)} pull requests"
                }
            else:
                return {
                    "success": False,
                    "status_code": response.status_code,
                    "message": f"❌ PRs fetch failed: {response.status_code}"
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"❌ PRs fetch error: {str(e)}"
            }

if __name__ == "__main__":
    # Test the GitHub manager
    github = GitHubManager()
    
    print("🧪 Testing GitHub API Manager...")
    
    # Test authentication
    auth_result = github.test_authentication()
    print(f"Auth: {auth_result['message']}")
    
    # Test repository access
    repo_result = github.get_repo_info()
    print(f"Repo: {repo_result['message']}")
    
    if auth_result["success"] and repo_result["success"]:
        print("✅ GitHub API Manager ready for A2A integration!")
    else:
        print("❌ GitHub API Manager needs token configuration")