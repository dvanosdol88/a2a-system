#!/usr/bin/env python3
"""
Git Operations Manager for A2A Agents
Handles local git operations, branch management, and automated workflows
"""

import subprocess
import os
import tempfile
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

class GitManager:
    def __init__(self, repo_path: str = None):
        """Initialize Git manager"""
        if repo_path:
            self.repo_path = Path(repo_path)
        else:
            # Find git repo by walking up from current directory
            current = Path.cwd()
            while current != current.parent:
                if (current / ".git").exists():
                    self.repo_path = current
                    break
                current = current.parent
            else:
                self.repo_path = Path.cwd()
        
        self.ensure_git_repo()
    
    def ensure_git_repo(self):
        """Ensure we're in a git repository"""
        if not (self.repo_path / ".git").exists():
            raise ValueError(f"Not a git repository: {self.repo_path}")
    
    def run_git_command(self, command: List[str], capture_output: bool = True) -> Dict[str, Any]:
        """Run a git command and return result"""
        try:
            full_command = ["git"] + command
            result = subprocess.run(
                full_command,
                cwd=self.repo_path,
                capture_output=capture_output,
                text=True,
                timeout=30
            )
            
            return {
                "success": result.returncode == 0,
                "returncode": result.returncode,
                "stdout": result.stdout.strip() if result.stdout else "",
                "stderr": result.stderr.strip() if result.stderr else "",
                "command": " ".join(full_command)
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "Command timeout",
                "command": " ".join(full_command)
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "command": " ".join(full_command)
            }
    
    def get_current_branch(self) -> str:
        """Get current branch name"""
        result = self.run_git_command(["branch", "--show-current"])
        return result["stdout"] if result["success"] else "unknown"
    
    def get_status(self) -> Dict[str, Any]:
        """Get git status information"""
        result = self.run_git_command(["status", "--porcelain"])
        if not result["success"]:
            return {"success": False, "error": result.get("stderr", "Unknown error")}
        
        lines = result["stdout"].split("\n") if result["stdout"] else []
        modified = []
        untracked = []
        staged = []
        
        for line in lines:
            if not line.strip():
                continue
            status = line[:2]
            filename = line[3:]
            
            if status[0] in "MADRC":  # Staged changes
                staged.append(filename)
            if status[1] in "MD":     # Modified
                modified.append(filename)
            if status == "??":        # Untracked
                untracked.append(filename)
        
        return {
            "success": True,
            "branch": self.get_current_branch(),
            "modified": modified,
            "untracked": untracked,
            "staged": staged,
            "clean": len(modified) == 0 and len(untracked) == 0 and len(staged) == 0
        }
    
    def create_branch(self, branch_name: str, checkout: bool = True) -> Dict[str, Any]:
        """Create a new branch"""
        # Check if branch already exists
        result = self.run_git_command(["branch", "--list", branch_name])
        if result["success"] and result["stdout"]:
            return {"success": False, "error": f"Branch '{branch_name}' already exists"}
        
        # Create branch
        command = ["checkout", "-b", branch_name] if checkout else ["branch", branch_name]
        result = self.run_git_command(command)
        
        if result["success"]:
            return {
                "success": True,
                "branch": branch_name,
                "message": f"✅ Branch '{branch_name}' created" + (" and checked out" if checkout else "")
            }
        else:
            return {
                "success": False,
                "error": result.get("stderr", "Branch creation failed"),
                "message": f"❌ Failed to create branch '{branch_name}'"
            }
    
    def checkout_branch(self, branch_name: str) -> Dict[str, Any]:
        """Checkout existing branch"""
        result = self.run_git_command(["checkout", branch_name])
        
        if result["success"]:
            return {
                "success": True,
                "branch": branch_name,
                "message": f"✅ Switched to branch '{branch_name}'"
            }
        else:
            return {
                "success": False,
                "error": result.get("stderr", "Checkout failed"),
                "message": f"❌ Failed to checkout branch '{branch_name}'"
            }
    
    def add_files(self, files: List[str] = None) -> Dict[str, Any]:
        """Add files to staging area"""
        if files is None:
            command = ["add", "."]
        else:
            command = ["add"] + files
        
        result = self.run_git_command(command)
        
        if result["success"]:
            return {
                "success": True,
                "message": f"✅ Files added to staging area"
            }
        else:
            return {
                "success": False,
                "error": result.get("stderr", "Add failed"),
                "message": f"❌ Failed to add files"
            }
    
    def commit(self, message: str, author: str = None) -> Dict[str, Any]:
        """Create a commit"""
        command = ["commit", "-m", message]
        if author:
            command.extend(["--author", author])
        
        result = self.run_git_command(command)
        
        if result["success"]:
            # Get commit hash
            hash_result = self.run_git_command(["rev-parse", "HEAD"])
            commit_hash = hash_result["stdout"][:7] if hash_result["success"] else "unknown"
            
            return {
                "success": True,
                "commit_hash": commit_hash,
                "message": f"✅ Commit created: {commit_hash}"
            }
        else:
            return {
                "success": False,
                "error": result.get("stderr", "Commit failed"),
                "message": f"❌ Commit failed"
            }
    
    def push_branch(self, branch_name: str = None, remote: str = "origin") -> Dict[str, Any]:
        """Push branch to remote"""
        if branch_name is None:
            branch_name = self.get_current_branch()
        
        # First try to push
        result = self.run_git_command(["push", remote, branch_name])
        
        if result["success"]:
            return {
                "success": True,
                "branch": branch_name,
                "message": f"✅ Branch '{branch_name}' pushed to {remote}"
            }
        else:
            # Try with --set-upstream for new branches
            result = self.run_git_command(["push", "--set-upstream", remote, branch_name])
            
            if result["success"]:
                return {
                    "success": True,
                    "branch": branch_name,
                    "message": f"✅ Branch '{branch_name}' pushed to {remote} (upstream set)"
                }
            else:
                return {
                    "success": False,
                    "error": result.get("stderr", "Push failed"),
                    "message": f"❌ Failed to push branch '{branch_name}'"
                }
    
    def get_remote_url(self, remote: str = "origin") -> str:
        """Get remote URL"""
        result = self.run_git_command(["remote", "get-url", remote])
        return result["stdout"] if result["success"] else ""
    
    def get_commit_log(self, count: int = 5) -> List[Dict[str, str]]:
        """Get recent commit log"""
        result = self.run_git_command([
            "log", f"-{count}", "--pretty=format:%h|%an|%ad|%s", "--date=short"
        ])
        
        if not result["success"]:
            return []
        
        commits = []
        for line in result["stdout"].split("\n"):
            if "|" in line:
                parts = line.split("|", 3)
                if len(parts) == 4:
                    commits.append({
                        "hash": parts[0],
                        "author": parts[1],
                        "date": parts[2],
                        "message": parts[3]
                    })
        
        return commits
    
    def automated_commit_push_workflow(self, 
                                     files: List[str] = None,
                                     commit_message: str = None,
                                     branch_name: str = None,
                                     author: str = None) -> Dict[str, Any]:
        """Complete automated workflow: add -> commit -> push"""
        results = []
        
        # Get current status
        status = self.get_status()
        if not status["success"]:
            return {"success": False, "error": "Failed to get git status"}
        
        results.append(f"📊 Status: {len(status['modified'])} modified, {len(status['untracked'])} untracked, {len(status['staged'])} staged")
        
        # Create branch if specified
        if branch_name and branch_name != status["branch"]:
            branch_result = self.create_branch(branch_name)
            results.append(branch_result["message"])
            if not branch_result["success"]:
                return {"success": False, "results": results, "error": "Branch creation failed"}
        
        # Add files
        if status["modified"] or status["untracked"] or files:
            add_result = self.add_files(files)
            results.append(add_result["message"])
            if not add_result["success"]:
                return {"success": False, "results": results, "error": "File add failed"}
        
        # Commit
        if not commit_message:
            commit_message = f"Automated commit by A2A agent at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        commit_result = self.commit(commit_message, author)
        results.append(commit_result["message"])
        if not commit_result["success"]:
            return {"success": False, "results": results, "error": "Commit failed"}
        
        # Push
        push_result = self.push_branch(branch_name or status["branch"])
        results.append(push_result["message"])
        if not push_result["success"]:
            return {"success": False, "results": results, "error": "Push failed"}
        
        return {
            "success": True,
            "results": results,
            "commit_hash": commit_result.get("commit_hash"),
            "branch": branch_name or status["branch"],
            "message": "✅ Automated workflow completed successfully"
        }

if __name__ == "__main__":
    # Test the Git manager
    git = GitManager()
    
    print("🧪 Testing Git Manager...")
    
    # Test status
    status = git.get_status()
    if status["success"]:
        print(f"✅ Git status: Branch '{status['branch']}', Clean: {status['clean']}")
        print(f"   Modified: {len(status['modified'])}, Untracked: {len(status['untracked'])}, Staged: {len(status['staged'])}")
    else:
        print(f"❌ Git status failed: {status['error']}")
    
    # Test commit log
    commits = git.get_commit_log(3)
    print(f"✅ Recent commits: {len(commits)}")
    for commit in commits[:2]:
        print(f"   {commit['hash']} - {commit['message']}")
    
    print("🎯 Git Manager ready for A2A automation!")