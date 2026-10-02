"""
Automated GitHub Pull Request Reviewer
File location: .github/scripts/review_pr.py
"""
import os
import sys
import json
import subprocess
import httpx

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
PR_NUMBER = os.environ.get("PR_NUMBER")
REPO_NAME = os.environ.get("REPO_NAME")
LLM_API_KEY = os.environ.get("LLM_API_KEY")

LLM_BASE_URL = os.environ.get("LLM_BASE_URL") or "https://api.groq.com/openai/v1/chat/completions"
LLM_MODEL = os.environ.get("LLM_MODEL") or "llama-3.3-70b-versatile"


def get_git_diff() -> str:
    cmd = ["git", "diff", "origin/main...HEAD"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    diff = result.stdout
    if len(diff) > 25000:
        return diff[:25000] + "\n\n[Diff truncated for review context...]"
    return diff


def main():
    if not LLM_API_KEY or not GITHUB_TOKEN:
        print("Missing required environment variables. Skipping review.")
        sys.exit(0)

    diff = get_git_diff()
    if not diff.strip():
        print("Empty diff. Nothing to review.")
        sys.exit(0)

    system_prompt = """You are a Principal Software Architect reviewing a GitHub PR diff.

Focus strictly on Security (OWASP Top 10), performance, and unhandled errors.

Format output in clean Markdown with:
### 🛡️ AI Security & Architecture Review
- **Verdict**: [APPROVE / COMMENT / REQUEST_CHANGES]
- **Risk Level**: [LOW / MEDIUM / HIGH / CRITICAL]
#### Key Findings:
- [File:Line]: Issue description and code fix snippet."""

    headers = {"Authorization": f"Bearer {LLM_API_KEY}", "Content-Type": "application/json"}
    payload = {
        "model": LLM_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Review this PR diff:\n\n```diff\n{diff}\n```"}
        ],
        "temperature": 0.1
    }

    try:
        res = httpx.post(LLM_BASE_URL, headers=headers, json=payload, timeout=45.0)
        review_body = res.json()["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"Error calling LLM provider: {e}")
        sys.exit(1)

    gh_url = f"https://api.github.com/repos/{REPO_NAME}/issues/{PR_NUMBER}/comments"
    gh_headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }

    post_res = httpx.post(gh_url, headers=gh_headers, json={"body": review_body})
    if post_res.status_code == 201:
        print("Successfully posted AI review comment to GitHub PR.")
    else:
        print(f"Failed to post PR comment: {post_res.status_code} - {post_res.text}")


if __name__ == "__main__":
    main()
