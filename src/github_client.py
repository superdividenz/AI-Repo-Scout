"""
GitHub API client for fetching repository data and trends.
Uses only the free GitHub REST API with rate limiting support.
"""

import requests
import time
import os
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GitHubAPIClient:
    """Free GitHub API client with rate limiting and trending analysis."""
    
    def __init__(self, token: Optional[str] = None):
        """Initialize the GitHub API client.
        
        Args:
            token: GitHub personal access token (optional but recommended)
        """
        self.token = token or os.getenv('GITHUB_TOKEN')
        self.base_url = "https://api.github.com"
        self.session = requests.Session()
        
        # Set up authentication headers
        if self.token:
            self.session.headers.update({
                'Authorization': f'token {self.token}',
                'Accept': 'application/vnd.github.v3+json'
            })
            self.rate_limit = 5000  # With token
        else:
            self.session.headers.update({
                'Accept': 'application/vnd.github.v3+json'
            })
            self.rate_limit = 60  # Without token
            logger.warning("No GitHub token provided. Rate limited to 60 requests/hour.")
    
    def _make_request(self, endpoint: str, params: Dict = None) -> Dict:
        """Make a rate-limited request to the GitHub API."""
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = self.session.get(url, params=params)
            
            # Check rate limit
            remaining = int(response.headers.get('X-RateLimit-Remaining', 0))
            if remaining < 10:
                reset_time = int(response.headers.get('X-RateLimit-Reset', 0))
                sleep_time = max(reset_time - time.time(), 0) + 1
                logger.warning(f"Rate limit approaching. Sleeping for {sleep_time} seconds.")
                time.sleep(sleep_time)
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {e}")
            return {}
    
    def get_trending_repos(self, language: str = None, since: str = "daily") -> List[Dict]:
        """Get trending repositories from GitHub.
        
        Args:
            language: Programming language filter (optional)
            since: Time period ('daily', 'weekly', 'monthly')
            
        Returns:
            List of repository dictionaries
        """
        # Calculate date range for trending
        days_map = {"daily": 1, "weekly": 7, "monthly": 30}
        days = days_map.get(since, 1)
        date_threshold = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        
        # Search for recently created/updated repos with high stars
        query_parts = [
            f"created:>{date_threshold}",
            "stars:>10"
        ]
        
        if language:
            query_parts.append(f"language:{language}")
        
        query = " ".join(query_parts)
        
        params = {
            'q': query,
            'sort': 'stars',
            'order': 'desc',
            'per_page': 100
        }
        
        data = self._make_request('/search/repositories', params)
        repos = data.get('items', [])
        
        # Enrich with additional data
        enriched_repos = []
        for repo in repos[:50]:  # Limit to avoid rate limits
            enriched_repo = self._enrich_repo_data(repo)
            if enriched_repo:
                enriched_repos.append(enriched_repo)
        
        return enriched_repos
    
    def _enrich_repo_data(self, repo: Dict) -> Dict:
        """Enrich repository data with additional metrics."""
        try:
            # Get detailed repo info
            repo_data = self._make_request(f"/repos/{repo['full_name']}")
            
            # Get contributor count
            contributors = self._make_request(f"/repos/{repo['full_name']}/contributors")
            contributor_count = len(contributors) if isinstance(contributors, list) else 0
            
            # Get recent activity (commits, issues, PRs)
            commits = self._make_request(f"/repos/{repo['full_name']}/commits", 
                                       {'since': (datetime.now() - timedelta(days=7)).isoformat()})
            recent_commits = len(commits) if isinstance(commits, list) else 0
            
            # Calculate engagement metrics
            stars = repo_data.get('stargazers_count', 0)
            forks = repo_data.get('forks_count', 0)
            issues = repo_data.get('open_issues_count', 0)
            
            # Star velocity (stars per day since creation)
            created_at = datetime.strptime(repo_data['created_at'], '%Y-%m-%dT%H:%M:%SZ')
            days_since_creation = (datetime.now() - created_at).days
            star_velocity = stars / max(days_since_creation, 1)
            
            return {
                'name': repo_data['name'],
                'full_name': repo_data['full_name'],
                'description': repo_data.get('description', ''),
                'html_url': repo_data['html_url'],
                'language': repo_data.get('language'),
                'stars': stars,
                'forks': forks,
                'issues': issues,
                'contributors': contributor_count,
                'recent_commits': recent_commits,
                'star_velocity': star_velocity,
                'created_at': repo_data['created_at'],
                'updated_at': repo_data['updated_at'],
                'topics': repo_data.get('topics', []),
                'license': repo_data.get('license', {}).get('name') if repo_data.get('license') else None,
                'size': repo_data.get('size', 0),
                'default_branch': repo_data.get('default_branch', 'main')
            }
            
        except Exception as e:
            logger.error(f"Failed to enrich repo {repo.get('full_name', 'unknown')}: {e}")
            return None
    
    def get_repo_details(self, repo_full_name: str) -> Dict:
        """Get detailed information about a specific repository."""
        return self._make_request(f"/repos/{repo_full_name}")
    
    def get_trending_by_language(self, languages: List[str], limit: int = 20) -> Dict[str, List[Dict]]:
        """Get trending repos for multiple programming languages."""
        results = {}
        
        for language in languages:
            logger.info(f"Fetching trending {language} repositories...")
            repos = self.get_trending_repos(language=language)
            results[language] = repos[:limit]
            
            # Small delay to respect rate limits
            time.sleep(1)
        
        return results
    
    def search_repos(self, query: str, sort: str = "stars", order: str = "desc") -> List[Dict]:
        """Search for repositories with a custom query."""
        params = {
            'q': query,
            'sort': sort,
            'order': order,
            'per_page': 50
        }
        
        data = self._make_request('/search/repositories', params)
        return data.get('items', [])
    
    def get_rate_limit_status(self) -> Dict:
        """Check current rate limit status."""
        return self._make_request('/rate_limit')


# Utility functions for data analysis

def calculate_momentum_score(repo: Dict) -> float:
    """Calculate a momentum score for a repository based on various metrics."""
    
    # Weights for different factors
    weights = {
        'star_velocity': 0.3,
        'contributor_ratio': 0.2,
        'activity_ratio': 0.2,
        'freshness': 0.15,
        'engagement': 0.15
    }
    
    # Normalize metrics (0-1 scale)
    star_velocity = min(repo.get('star_velocity', 0) / 10, 1)  # Cap at 10 stars/day
    contributor_ratio = min(repo.get('contributors', 0) / max(repo.get('stars', 1), 1), 1)
    activity_ratio = min(repo.get('recent_commits', 0) / 50, 1)  # Cap at 50 commits/week
    
    # Freshness (newer repos get higher scores)
    created_at = datetime.strptime(repo['created_at'], '%Y-%m-%dT%H:%M:%SZ')
    days_old = (datetime.now() - created_at).days
    freshness = max(1 - (days_old / 365), 0)  # Fresher if less than a year old
    
    # Engagement (issues + forks relative to stars)
    engagement = min((repo.get('issues', 0) + repo.get('forks', 0)) / max(repo.get('stars', 1), 1), 1)
    
    # Calculate weighted score
    score = (
        weights['star_velocity'] * star_velocity +
        weights['contributor_ratio'] * contributor_ratio +
        weights['activity_ratio'] * activity_ratio +
        weights['freshness'] * freshness +
        weights['engagement'] * engagement
    )
    
    return round(score * 100, 2)  # Convert to 0-100 scale


def filter_quality_repos(repos: List[Dict], min_stars: int = 10, min_score: float = 20) -> List[Dict]:
    """Filter repositories based on quality metrics."""
    quality_repos = []
    
    for repo in repos:
        # Add momentum score
        repo['momentum_score'] = calculate_momentum_score(repo)
        
        # Filter criteria
        if (repo.get('stars', 0) >= min_stars and 
            repo['momentum_score'] >= min_score and
            repo.get('description')):  # Must have a description
            quality_repos.append(repo)
    
    # Sort by momentum score
    return sorted(quality_repos, key=lambda x: x['momentum_score'], reverse=True)