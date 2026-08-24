import os
import sys
from typing import List, Set

import requests

API_URL = "https://api.github.com"


def get_token() -> str:
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        print("Error: GITHUB_TOKEN environment variable is not set.")
        print("Set it before running the application.")
        sys.exit(1)
    return token


def github_get(session: requests.Session, path: str, params: dict | None = None):
    response = session.get(f"{API_URL}{path}", params=params, timeout=30)

    if response.status_code == 401:
        print("Error: GitHub token is invalid or expired.")
        sys.exit(1)

    if response.status_code == 403:
        print("Error: GitHub API request was forbidden or rate-limited.")
        print("Check your token permissions and GitHub API rate limits.")
        sys.exit(1)

    if not response.ok:
        print(f"Error: GitHub API returned HTTP {response.status_code}.")
        print(response.text)
        sys.exit(1)

    return response


def get_all_users(session: requests.Session, endpoint: str) -> Set[str]:
    users: Set[str] = set()
    page = 1
    per_page = 100

    while True:
        response = github_get(
            session,
            endpoint,
            params={"per_page": per_page, "page": page},
        )
        data = response.json()

        if not isinstance(data, list):
            print(f"Error: Unexpected response from {endpoint}.")
            sys.exit(1)

        users.update(user["login"] for user in data if "login" in user)

        if len(data) < per_page:
            break

        page += 1

    return users


def main() -> None:
    token = get_token()

    session = requests.Session()
    session.headers.update(
        {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "github-unfollowers",
        }
    )

    # Verify authentication before requesting follower/following data.
    user_response = github_get(session, "/user")
    authenticated_user = user_response.json().get("login", "unknown")

    following = get_all_users(session, "/user/following")
    followers = get_all_users(session, "/user/followers")

    unfollowers = sorted(following - followers, key=str.lower)

    print("GitHub Unfollowers")
    print("==================")
    print()
    print(f"Authenticated as: @{authenticated_user}")
    print(f"Following: {len(following)}")
    print(f"Followers: {len(followers)}")
    print(f"Users who don't follow you back: {len(unfollowers)}")
    print()

    if not unfollowers:
        print("Everyone you follow follows you back. 🎉")
        return

    for index, username in enumerate(unfollowers, start=1):
        print(f"{index}. {username}")


if __name__ == "__main__":
    main()
