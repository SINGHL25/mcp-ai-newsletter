<img width="2048" height="2048" alt="api_usage" src="https://github.com/user-attachments/assets/63a97477-a241-4607-b1a0-fb4552dd2bd1" />

🚀 MCP AI Newsletter API Usage Guide
Overview
This guide provides comprehensive examples for using the MCP AI Newsletter API endpoints programmatically.

🔧 Quick Start
Authentication Setup
pythonimport os
import httpx
import asyncio
from dotenv import load_dotenv

load_dotenv()

# Environment variables required
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
MCP_SERVER_URL = os.getenv("MCP_SERVER_URL", "http://localhost:8000")

headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {GITHUB_TOKEN}"  # If implementing auth
}
📊 Core Endpoints
1. Health Check
Check if the MCP server is running:
pythonasync def check_server_health():
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{MCP_SERVER_URL}/health")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Server Status: {data['status']}")
            print(f"📅 Timestamp: {data['timestamp']}")
            return True
        else:
            print(f"❌ Server Error: {response.status_code}")
            return False

# Usage
asyncio.run(check_server_health())
2. Generate Complete Newsletter Data
Main endpoint for newsletter generation:
pythonasync def generate_newsletter_data(days=7, include_stats=True, max_repos=15):
    """Generate complete newsletter data"""
    
    payload = {
        "days": days,
        "include_stats": include_stats,
        "max_repos": max_repos
    }
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            f"{MCP_SERVER_URL}/generate-newsletter-data",
            json=payload
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"API Error: {response.status_code} - {response.text}")

# Usage example
async def main():
    try:
        data = await generate_newsletter_data(days=7, max_repos=20)
        
        print(f"📈 Found {len(data['trending_repos'])} trending repositories")
        print(f"💬 Found {len(data['discussions'])} discussions")
        print(f"📊 Weekly stats: {data['weekly_stats']['total_stars']} total stars")
        
        return data
        
    except Exception as e:
        print(f"Error: {e}")

asyncio.run(main())
3. Get Trending Repositories Only
For when you only need repository data:
pythonasync def get_trending_repos(days=7, limit=10):
    """Fetch only trending AI repositories"""
    
    params = {
        "days": days,
        "limit": limit
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{MCP_SERVER_URL}/trending-repos",
            params=params
        )
        
        if response.status_code == 200:
            repos = response.json()
            
            print(f"🔥 Top {len(repos)} Trending AI Repositories:")
            for repo in repos[:5]:
                print(f"  ⭐ {repo['name']} ({repo['stargazers_count']} stars)")
                print(f"     {repo['description'][:100]}...")
                print(f"     🔗 {repo['html_url']}")
                print()
            
            return repos
        else:
            print(f"Error fetching repos: {response.status_code}")
            return []

# Usage
repos = asyncio.run(get_trending_repos(days=14, limit=20))
4. Get AI Discussions
Fetch interesting AI discussions and issues:
pythonasync def get_ai_discussions(days=7, limit=10):
    """Fetch AI-related discussions"""
    
    params = {
        "days": days,
        "limit": limit
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{MCP_SERVER_URL}/ai-discussions",
            params=params
        )
        
        if response.status_code == 200:
            discussions = response.json()
            
            print(f"💬 Top {len(discussions)} AI Discussions:")
            for disc in discussions[:3]:
                repo_name = disc.get('repository_url', '').split('/')[-1]
                print(f"  📝 {disc['title']}")
                print(f"     Repository: {repo_name}")
                print(f"     🔗 {disc['html_url']}")
                print()
            
            return discussions
        else:
            print(f"Error fetching discussions: {response.status_code}")
            return []

# Usage
discussions = asyncio.run(get_ai_discussions(days=5, limit=15))
🔨 Advanced Usage Patterns
1. Batch Processing Multiple Requests
pythonasync def batch_newsletter_requests():
    """Process multiple newsletter requests concurrently"""
    
    # Different time periods
    requests = [
        {"days": 1, "max_repos": 5},   # Daily highlights
        {"days": 7, "max_repos": 15},  # Weekly roundup
        {"days": 30, "max_repos": 10}  # Monthly trends
    ]
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        tasks = [
            client.post(f"{MCP_SERVER_URL}/generate-newsletter-data", json=req)
            for req in requests
        ]
        
        responses = await asyncio.gather(*tasks)
        
        results = {}
        for i, response in enumerate(responses):
            period = ["daily", "weekly", "monthly"][i]
            if response.status_code == 200:
                results[period] = response.json()
            else:
                print(f"Error in {period} request: {response.status_code}")
        
        return results

# Usage
batch_data = asyncio.run(batch_newsletter_requests())
2. Error Handling & Retry Logic
pythonimport time
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10)
)
async def resilient_newsletter_generation(days=7):
    """Newsletter generation with retry logic"""
    
    async with httpx.AsyncClient(timeout=120.0) as client:
        response = await client.post(
            f"{MCP_SERVER_URL}/generate-newsletter-data",
            json={"days": days, "include_stats": True, "max_repos": 15}
        )
        
        if response.status_code == 429:  # Rate limited
            print("Rate limited, waiting...")
            await asyncio.sleep(60)
            raise Exception("Rate limited - retrying")
        
        if response.status_code != 200:
            raise Exception(f"API Error: {response.status_code}")
        
        return response.json()

# Usage with error handling
async def safe_generation():
    try:
        data = await resilient_newsletter_generation(days=7)
        print("✅ Newsletter data generated successfully")
        return data
    except Exception as e:
        print(f"❌ Failed after retries: {e}")
        return None

asyncio.run(safe_generation())
3. Data Filtering & Processing
pythondef filter_newsletter_data(data, min_stars=100, languages=None):
    """Filter and process newsletter data"""
    
    if languages is None:
        languages = ["Python", "JavaScript", "TypeScript"]
    
    # Filter repositories by criteria
    filtered_repos = [
        repo for repo in data.get("trending_repos", [])
        if repo.get("stargazers_count", 0) >= min_stars
        and repo.get("language") in languages
    ]
    
    # Sort by stars
    filtered_repos.sort(
        key=lambda x: x.get("stargazers_count", 0),
        reverse=True
    )
    
    # Filter discussions by length (quality indicator)
    quality_discussions = [
        disc for disc in data.get("discussions", [])
        if len(disc.get("body", "")) > 100
    ]
    
    return {
        "trending_repos": filtered_repos,
        "discussions": quality_discussions,
        "weekly_stats": data.get("weekly_stats", {}),
        "generation_timestamp": data.get("generation_timestamp")
    }

# Usage
async def get_filtered_newsletter():
    raw_data = await generate_newsletter_data(days=7, max_repos=25)
    
    filtered_data = filter_newsletter_data(
        raw_data,
        min_stars=200,
        languages=["Python", "TypeScript", "Go"]
    )
    
    print(f"📊 Filtered to {len(filtered_data['trending_repos'])} high-quality repos")
    return filtered_data

asyncio.run(get_filtered_newsletter())
🔄 Integration Examples
1. Webhook Integration
pythonfrom fastapi import FastAPI, BackgroundTasks
import json

app = FastAPI()

@app.post("/webhook/generate-newsletter")
async def webhook_newsletter_generation(background_tasks: BackgroundTasks):
    """Webhook endpoint for external newsletter triggers"""
    
    async def generate_and_save():
        try:
            data = await generate_newsletter_data(days=7)
            
            # Save to file or database
            with open(f"newsletter_{data['generation_timestamp']}.json", "w") as f:
                json.dump(data, f, indent=2)
            
            print("✅ Newsletter generated via webhook")
            
        except Exception as e:
            print(f"❌ Webhook generation failed: {e}")
    
    background_tasks.add_task(generate_and_save)
    return {"status": "generating", "message": "Newsletter generation started"}
2. Scheduled Generation
pythonimport schedule
import time
from datetime import datetime

def scheduled_newsletter_generation():
    """Generate newsletter on schedule"""
    
    async def generate():
        try:
            data = await generate_newsletter_data(days=7, max_repos=20)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"newsletters/weekly_{timestamp}.json"
            
            with open(filename, "w") as f:
                json.dump(data, f, indent=2)
            
            print(f"✅ Scheduled newsletter saved to {filename}")
            
        except Exception as e:
            print(f"❌ Scheduled generation failed: {e}")
    
    asyncio.run(generate())

# Schedule weekly generation (every Monday at 9 AM)
schedule.every().monday.at("09:00").do(scheduled_newsletter_generation)

# Run scheduler
while True:
    schedule.run_pending()
    time.sleep(60)
3. Multi-format Export
pythonimport json
import csv
from datetime import datetime

async def export_newsletter_data(format_type="json"):
    """Export newsletter data in different formats"""
    
    data = await generate_newsletter_data(days=7)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    if format_type == "json":
        filename = f"newsletter_{timestamp}.json"
        with open(filename, "w") as f:
            json.dump(data, f, indent=2)
    
    elif format_type == "csv":
        filename = f"newsletter_repos_{timestamp}.csv"
        with open(filename, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=[
                "name", "owner", "stars", "language", "description", "url"
            ])
            writer.writeheader()
            
            for repo in data["trending_repos"]:
                writer.writerow({
                    "name": repo["name"],
                    "owner": repo["owner"]["login"],
                    "stars": repo["stargazers_count"],
                    "language": repo.get("language", ""),
                    "description": repo.get("description", "")[:100],
                    "url": repo["html_url"]
                })
    
    print(f"✅ Data exported as {filename}")
    return filename

# Export in different formats
asyncio.run(export_newsletter_data("json"))
asyncio.run(export_newsletter_data("csv"))
⚠️ Best Practices
1. Rate Limiting
pythonimport asyncio
from datetime import datetime, timedelta

class RateLimiter:
    def __init__(self, calls_per_minute=30):
        self.calls_per_minute = calls_per_minute
        self.calls = []
    
    async def wait_if_needed(self):
        now = datetime.now()
        
        # Remove old calls
        self.calls = [call_time for call_time in self.calls 
                     if now - call_time < timedelta(minutes=1)]
        
        if len(self.calls) >= self.calls_per_minute:
            wait_time = 60 - (now - self.calls[0]).seconds
            print(f"Rate limit reached, waiting {wait_time} seconds...")
            await asyncio.sleep(wait_time)
        
        self.calls.append(now)

# Usage
limiter = RateLimiter(calls_per_minute=20)

async def rate_limited_request():
    await limiter.wait_if_needed()
    return await generate_newsletter_data()
