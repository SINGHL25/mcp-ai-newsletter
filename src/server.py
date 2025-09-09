
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional
import asyncio
from datetime import datetime

from github_adapter import GitHubAdapter
from utils import setup_logging

logger = setup_logging()

app = FastAPI(
    title="AI Newsletter MCP Server",
    description="MCP server for AI newsletter generation",
    version="1.0.0"
)

github_adapter = GitHubAdapter()

class NewsletterRequest(BaseModel):
    days: Optional[int] = 7
    include_stats: Optional[bool] = True
    max_repos: Optional[int] = 10

class NewsletterData(BaseModel):
    trending_repos: List[Dict]
    discussions: List[Dict]
    weekly_stats: Dict
    generation_timestamp: str

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.post("/generate-newsletter-data", response_model=NewsletterData)
async def generate_newsletter_data(request: NewsletterRequest):
    """
    MCP endpoint to generate all data needed for AI newsletter
    """
    try:
        logger.info(f"Generating newsletter data for last {request.days} days")
        
        # Fetch data concurrently
        trending_repos_task = github_adapter.get_trending_ai_repos(request.days)
        discussions_task = github_adapter.get_ai_discussions(request.days)
        
        trending_repos, discussions = await asyncio.gather(
            trending_repos_task,
            discussions_task
        )
        
        # Limit results
        trending_repos = trending_repos[:request.max_repos]
        discussions = discussions[:10]
        
        # Generate weekly stats if requested
        weekly_stats = {}
        if request.include_stats and trending_repos:
            stats_tasks = [
                github_adapter.get_repo_stats(repo["full_name"]) 
                for repo in trending_repos[:5]
            ]
            detailed_repos = await asyncio.gather(*stats_tasks)
            
            weekly_stats = {
                "total_stars": sum(repo.get("stars", 0) for repo in detailed_repos),
                "total_forks": sum(repo.get("forks", 0) for repo in detailed_repos),
                "languages": list(set(repo.get("language") for repo in detailed_repos if repo.get("language"))),
                "top_repos": detailed_repos[:3]
            }
        
        return NewsletterData(
            trending_repos=trending_repos,
            discussions=discussions,
            weekly_stats=weekly_stats,
            generation_timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        logger.error(f"Error generating newsletter data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/trending-repos")
async def get_trending_repos(days: int = 7, limit: int = 10):
    """Get trending AI repositories"""
    repos = await github_adapter.get_trending_ai_repos(days)
    return repos[:limit]

@app.get("/ai-discussions") 
async def get_ai_discussions(days: int = 7, limit: int = 10):
    """Get trending AI discussions"""
    discussions = await github_adapter.get_ai_discussions(days)
    return discussions[:limit]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
