"""
Social Integration Service
Handles enrichment from external platforms like GitHub and LinkedIn.
All integrations require explicit user consent and use public APIs only.
"""
import re
from typing import Dict, List, Optional
from loguru import logger

try:
    import httpx
    HTTPX_AVAILABLE = True
except ImportError:
    HTTPX_AVAILABLE = False


class SocialIntegrationService:
    """
    Service for enriching candidate profiles with publicly available social data.
    All operations require explicit user consent (GDPR compliant).
    """

    GITHUB_API = "https://api.github.com"

    def __init__(self):
        self._client = None

    def _get_client(self):
        if not HTTPX_AVAILABLE:
            logger.warning("httpx not installed. Social integration disabled.")
            return None
        if self._client is None:
            self._client = httpx.Client(timeout=10.0, headers={"Accept": "application/json"})
        return self._client

    # ─── GitHub Integration ──────────────────────────────────────────────────

    def enrich_from_github(self, github_username: str) -> Dict:
        """
        Fetch public GitHub profile data to enrich a candidate's technical profile.
        Extracts: languages used, top repos, contribution count, bio.

        Args:
            github_username: GitHub username (e.g., "octocat")

        Returns:
            Dictionary with enriched profile data
        """
        client = self._get_client()
        if not client:
            return {"error": "HTTP client not available"}

        try:
            # Fetch user profile
            user_resp = client.get(f"{self.GITHUB_API}/users/{github_username}")
            if user_resp.status_code != 200:
                return {"error": f"GitHub user not found: {github_username}"}

            user_data = user_resp.json()

            # Fetch repos
            repos_resp = client.get(
                f"{self.GITHUB_API}/users/{github_username}/repos",
                params={"sort": "updated", "per_page": 10}
            )
            repos = repos_resp.json() if repos_resp.status_code == 200 else []

            # Extract languages
            languages = set()
            top_repos = []
            for repo in repos:
                if repo.get("language"):
                    languages.add(repo["language"])
                if not repo.get("fork", False):
                    top_repos.append({
                        "name": repo["name"],
                        "description": repo.get("description", ""),
                        "language": repo.get("language"),
                        "stars": repo.get("stargazers_count", 0),
                        "url": repo.get("html_url")
                    })

            return {
                "source": "github",
                "username": github_username,
                "profile_url": user_data.get("html_url"),
                "bio": user_data.get("bio", ""),
                "public_repos": user_data.get("public_repos", 0),
                "followers": user_data.get("followers", 0),
                "languages": list(languages),
                "top_repositories": top_repos[:5],
                "inferred_skills": list(languages),  # Languages as skills
                "account_created": user_data.get("created_at"),
            }

        except Exception as e:
            logger.error(f"GitHub enrichment failed for {github_username}: {e}")
            return {"error": str(e)}

    # ─── LinkedIn (Placeholder - requires OAuth) ─────────────────────────────

    def enrich_from_linkedin(self, linkedin_url: str) -> Dict:
        """
        Placeholder for LinkedIn integration.
        Full implementation requires LinkedIn OAuth2 application approval.

        Args:
            linkedin_url: LinkedIn profile URL

        Returns:
            Dictionary with enrichment status
        """
        # Extract username from URL
        username_match = re.search(r'linkedin\.com/in/([^/?]+)', linkedin_url)
        username = username_match.group(1) if username_match else linkedin_url

        return {
            "source": "linkedin",
            "username": username,
            "profile_url": linkedin_url,
            "status": "integration_pending",
            "message": "LinkedIn API integration requires OAuth2 app approval. "
                       "Profile URL has been stored for manual review.",
            "inferred_skills": []
        }

    # ─── Social Sharing ──────────────────────────────────────────────────────

    def generate_share_links(self, job_title: str, company: str, job_url: str) -> Dict:
        """
        Generate social media sharing links for a job posting.

        Args:
            job_title: Job title
            company: Company name
            job_url: URL to the job posting

        Returns:
            Dictionary with share URLs for various platforms
        """
        from urllib.parse import quote

        text = quote(f"Check out this opportunity: {job_title} at {company}")
        encoded_url = quote(job_url)

        return {
            "linkedin": f"https://www.linkedin.com/sharing/share-offsite/?url={encoded_url}",
            "twitter": f"https://twitter.com/intent/tweet?text={text}&url={encoded_url}",
            "facebook": f"https://www.facebook.com/sharer/sharer.php?u={encoded_url}",
            "email": f"mailto:?subject={quote(f'{job_title} at {company}')}&body={text}%20{encoded_url}",
            "copy_link": job_url
        }

    # ─── Referral System ─────────────────────────────────────────────────────

    def generate_referral_link(self, job_id: str, referrer_id: str, base_url: str = "http://localhost:3000") -> str:
        """Generate a unique referral link for a job posting."""
        import hashlib
        ref_code = hashlib.md5(f"{job_id}-{referrer_id}".encode()).hexdigest()[:8]
        return f"{base_url}/jobs/{job_id}?ref={ref_code}"
