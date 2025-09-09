
import httpx
import asyncio
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

load_dotenv()

class GitHubAdapter:
    def __init__(self):
        self.token = os.getenv("GITHUB_TOKEN")
        self.base_url = "https://api.github.com"
        self.headers = {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3+json"
        }
    
    async def get_trending_ai_repos(self, days: int = 7) -> List[Dict]:
        """Fetch trending AI repositories from the last N days"""
        date_filter = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
        
        # Search for AI-related repos with recent activity
        query_terms = [
            "artificial intelligence",
            "machine learning", 
            "deep learning",
            "neural network",
            "transformer",
            "llm",
            "generative ai"
        ]
        
        repos = []
        async with httpx.AsyncClient() as client:
            for term in query_terms[:3]:  # Limit API calls
                url = f"{self.base_url}/search/repositories"
                params = {
                    "q": f'"{term}" created:>{date_filter} language:Python',
                    "sort": "stars",
                    "order": "desc",
                    "per_page": 10
                }
                
                response = await client.get(url, headers=self.headers, params=params)
                if response.status_code == 200:
                    data = response.json()
                    repos.extend(data.get("items", [])[:5])
                
                # Rate limiting
                await asyncio.sleep(1)
        
        return self._deduplicate_repos(repos)
    
    async def get_ai_discussions(self, days: int = 7) -> List[Dict]:
        """Fetch interesting AI-related issues and discussions"""
        date_filter = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
        
        async with httpx.AsyncClient() as client:
            url = f"{self.base_url}/search/issues"
            params = {
                "q": f"AI OR ML OR 'machine learning' created:>{date_filter} type:issue",
                "sort": "reactions",
                "order": "desc",
                "per_page": 20
            }
            
            response = await client.get(url, headers=self.headers, params=params)
            if response.status_code == 200:
                return response.json().get("items", [])
        
        return []
    
    async def get_repo_stats(self, repo_full_name: str) -> Dict:
        """Get detailed stats for a specific repository"""
        async with httpx.AsyncClient() as client:
            url = f"{self.base_url}/repos/{repo_full_name}"
            response = await client.get(url, headers=self.headers)
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "name": data["name"],
                    "full_name": data["full_name"],
                    "stars": data["stargazers_count"],
                    "forks": data["forks_count"],
                    "language": data["language"],
                    "description": data["description"],
                    "url": data["html_url"],
                    "created_at": data["created_at"],
                    "updated_at": data["updated_at"]
                }
        
        return {}
    
    def _deduplicate_repos(self, repos: List[Dict]) -> List[Dict]:
        """Remove duplicate repositories based on full_name"""
        seen = set()
        unique_repos = []
        
        for repo in repos:
            if repo["full_name"] not in seen:
                seen.add(repo["full_name"])
                unique_repos.append(repo)
        
        return unique_repos[:15]  # Limit to top 15
