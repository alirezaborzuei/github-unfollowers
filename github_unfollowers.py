#!/usr/bin/env python3
"""
GitHub Unfollowers Finder
Finds all users you follow who don't follow you back
"""

import requests
import time
import sys
from typing import List, Set
import os

class GitHubUnfollowers:
    def __init__(self, username: str, token: str = None):
        """
        Initialize with GitHub username and optional personal access token
        
        Args:
            username: Your GitHub username
            token: GitHub Personal Access Token (recommended for higher rate limits)
        """
        self.username = username
        self.token = token
        self.base_url = "https://api.github.com"
        
        # Set up headers
        self.headers = {
            "Accept": "application/vnd.github.v3+json"
        }
        if token:
            self.headers["Authorization"] = f"token {token}"
    
    def _make_request(self, url: str, retry_count: int = 3) -> List[dict]:
        """
        Make a GET request to GitHub API with rate limit handling
        
        Args:
            url: API endpoint URL
            retry_count: Number of retries on failure
        
        Returns:
            List of items from the API response
        """
        for attempt in range(retry_count):
            try:
                response = requests.get(url, headers=self.headers)
                
                # Check for rate limiting
                if response.status_code == 403 and 'X-RateLimit-Remaining' in response.headers:
                    if int(response.headers['X-RateLimit-Remaining']) == 0:
                        reset_time = int(response.headers.get('X-RateLimit-Reset', 0))
                        if reset_time:
                            wait_time = reset_time - time.time() + 5
                            if wait_time > 0:
                                print(f"⏰ Rate limit exceeded. Waiting {wait_time:.0f} seconds...")
                                time.sleep(wait_time)
                                continue
                
                response.raise_for_status()
                
                # Handle pagination
                data = response.json()
                if isinstance(data, list):
                    # Check for next page
                    if 'Link' in response.headers:
                        links = response.headers['Link'].split(',')
                        for link in links:
                            if 'rel="next"' in link:
                                next_url = link.split(';')[0].strip('<>')
                                next_page = self._make_request(next_url)
                                data.extend(next_page)
                
                return data if isinstance(data, list) else [data]
                
            except requests.exceptions.RequestException as e:
                print(f"⚠️  Request failed (attempt {attempt + 1}/{retry_count}): {e}")
                if attempt < retry_count - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                else:
                    print(f"❌ Failed to fetch {url}")
                    return []
        
        return []
    
    def get_following(self) -> Set[str]:
        """
        Get the list of users you follow
        
        Returns:
            Set of usernames you follow
        """
        print(f"📊 Fetching users you follow...")
        url = f"{self.base_url}/users/{self.username}/following?per_page=100"
        data = self._make_request(url)
        users = {user['login'] for user in data}
        print(f"✅ You follow {len(users)} users")
        return users
    
    def get_followers(self) -> Set[str]:
        """
        Get the list of users who follow you
        
        Returns:
            Set of usernames who follow you
        """
        print(f"📊 Fetching your followers...")
        url = f"{self.base_url}/users/{self.username}/followers?per_page=100"
        data = self._make_request(url)
        users = {user['login'] for user in data}
        print(f"✅ You have {len(users)} followers")
        return users
    
    def find_non_followers(self) -> List[str]:
        """
        Find users you follow who don't follow you back
        
        Returns:
            List of usernames who don't follow you back
        """
        following = self.get_following()
        followers = self.get_followers()
        
        non_followers = following - followers
        return sorted(list(non_followers))
    
    def display_results(self, non_followers: List[str]):
        """
        Display the results in a formatted way
        
        Args:
            non_followers: List of usernames who don't follow back
        """
        if not non_followers:
            print("\n🎉 Great news! Everyone you follow follows you back!")
            return
        
        print(f"\n🔍 Found {len(non_followers)} user(s) who don't follow you back:")
        print("-" * 50)
        
        for i, user in enumerate(non_followers, 1):
            print(f"{i:3d}. @{user}")
        
        print("-" * 50)
        print(f"\n📝 Summary:")
        print(f"   Total following: {len(self.get_following())}")
        print(f"   Total followers: {len(self.get_followers())}")
        print(f"   Not following back: {len(non_followers)}")
        
        # Offer to create an unfollow list
        save_option = input("\n💾 Save list to file? (y/n): ").lower()
        if save_option == 'y':
            self.save_to_file(non_followers)
    
    def save_to_file(self, non_followers: List[str]):
        """
        Save the list to a text file
        
        Args:
            non_followers: List of usernames who don't follow back
        """
        filename = f"{self.username}_non_followers.txt"
        try:
            with open(filename, 'w') as f:
                f.write(f"Users @{self.username} follows who don't follow back:\n")
                f.write(f"Generated on: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("=" * 50 + "\n\n")
                for user in non_followers:
                    f.write(f"@{user}\n")
                f.write(f"\nTotal: {len(non_followers)} users")
            
            print(f"✅ List saved to {filename}")
        except Exception as e:
            print(f"❌ Error saving file: {e}")


def main():
    """Main function to run the script"""
    print("=" * 50)
    print("🐙 GitHub Unfollowers Finder")
    print("=" * 50)
    print()
    
    # Get username
    username = input("Enter your GitHub username: ").strip()
    if not username:
        print("❌ Username cannot be empty!")
        sys.exit(1)
    
    # Check for token in environment variable or ask for it
    token = os.environ.get('GITHUB_TOKEN')
    if not token:
        token = input("Enter your GitHub Personal Access Token (optional, press Enter to skip): ").strip()
        if not token:
            print("\n⚠️  No token provided. You may hit rate limits quickly (60 requests/hour).")
            print("   To get a token: Settings → Developer settings → Personal access tokens → Tokens (classic)")
            token = None
    
    print("\n🚀 Starting analysis...\n")
    
    # Create instance and find non-followers
    try:
        finder = GitHubUnfollowers(username, token)
        non_followers = finder.find_non_followers()
        finder.display_results(non_followers)
        
    except KeyboardInterrupt:
        print("\n\n🛑 Operation cancelled by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ An error occurred: {e}")
        print("Please check your username and try again.")
        sys.exit(1)


if __name__ == "__main__":
    main()