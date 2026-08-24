# GitHub Unfollowers

A lightweight Python utility for finding GitHub accounts that you follow but that do not follow you back.

## ✨ Features

- Fetches your GitHub followers and following lists.
- Compares both lists to identify non-followers.
- Prints usernames that do not follow you back.
- Supports GitHub Personal Access Tokens through an environment variable.
- Keeps the process local — no follower data needs to be uploaded to a third-party service.
- Designed to be simple to run and easy to extend.

## 📋 Requirements

- Python 3.9+
- A GitHub Personal Access Token with the minimum permissions required to read your account's followers/following data.

## 🚀 Installation

```bash
git clone https://github.com/alirezaborzuei/github-unfollowers.git
cd github-unfollowers

python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
```

## 🔐 Authentication

Create a GitHub Personal Access Token and store it as an environment variable instead of hard-coding it in the source code.

### Windows PowerShell

```powershell
$env:GITHUB_TOKEN="YOUR_GITHUB_TOKEN"
```

### macOS / Linux

```bash
export GITHUB_TOKEN="YOUR_GITHUB_TOKEN"
```

> **Security:** Never commit your token to Git. Add `.env` and other local secret files to `.gitignore` if you use them.

## ▶️ Usage

Run the application with:

```bash
python main.py
```

The application compares:

```text
Following - Followers = Users who don't follow you back
```

Example output:

```text
GitHub Unfollowers
==================

Following: 250
Followers: 210

Users who don't follow you back: 42

1. username_one
2. username_two
3. username_three
...
```

## 📁 Suggested Project Structure

```text
github-unfollowers/
├── main.py
├── requirements.txt
├── README.md
├── .gitignore
└── LICENSE
```

## 🧠 How It Works

1. Authenticate with GitHub using a Personal Access Token.
2. Request the authenticated user's following list.
3. Request the authenticated user's followers list.
4. Convert both collections into username sets.
5. Calculate the difference between the sets.
6. Display the accounts that you follow but that do not follow you back.

Conceptually:

```python
unfollowers = set(following) - set(followers)
```

## ⚠️ Unfollowing Accounts

This project is intended primarily for **identifying** accounts that do not follow you back.

Before adding any automated unfollow functionality, review GitHub's current API permissions, rate limits, and terms of use. A safer workflow is to generate the list first and manually decide which accounts to unfollow.

## 🛡️ Privacy & Security

- Do not commit GitHub tokens.
- Do not store tokens in source code.
- Use environment variables or another secure secret-management mechanism.
- Review the requested token permissions and use the minimum access required.
- Treat generated follower/following lists as personal account data.

## 📄 License

This project is provided for personal and educational use. Add the license that best matches how you want others to use and distribute the project.

## 👤 Author

**Alireza Borzouei**

GitHub: [@alirezaborzuei](https://github.com/alirezaborzuei)
