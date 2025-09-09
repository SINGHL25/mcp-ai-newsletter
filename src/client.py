
import httpx
import asyncio
from typing import Dict, Optional
import os
from dotenv import load_dotenv
import anthropic

from newsletter import NewsletterGenerator
from utils import setup_logging

load_dotenv()
logger = setup_logging()

class MCPNewsletterClient:
    def __init__(self, server_url: str = "http://localhost:8000"):
        self.server_url = server_url
        self.anthropic_client = anthropic.Anthropic(
            api_key=os.getenv("ANTHROPIC_API_KEY")
        )
        self.newsletter_generator = NewsletterGenerator()
    
    async def generate_newsletter(self, days: int = 7, enhance_with_claude: bool = True) -> str:
        """Generate complete newsletter using MCP server + Claude enhancement"""
        try:
            # Step 1: Get data from MCP server
            logger.info("Fetching data from MCP server...")
            raw_data = await self._fetch_newsletter_data(days)
            
            # Step 2: Generate basic newsletter
            logger.info("Generating newsletter structure...")
            basic_newsletter = self.newsletter_generator.generate_newsletter(raw_data)
            
            # Step 3: Enhance with Claude (optional)
            if enhance_with_claude:
                logger.info("Enhancing newsletter with Claude...")
                enhanced_newsletter = await self._enhance_with_claude(basic_newsletter, raw_data)
                return enhanced_newsletter
            
            return basic_newsletter
            
        except Exception as e:
            logger.error(f"Error generating newsletter: {e}")
            raise
    
    async def _fetch_newsletter_data(self, days: int) -> Dict:
        """Fetch data from MCP server"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.server_url}/generate-newsletter-data",
                json={
                    "days": days,
                    "include_stats": True,
                    "max_repos": 15
                }
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                raise Exception(f"MCP server error: {response.status_code} - {response.text}")
    
    async def _enhance_with_claude(self, basic_newsletter: str, raw_data: Dict) -> str:
        """Use Claude to enhance and polish the newsletter"""
        
        prompt = f"""You are an expert AI newsletter editor. Please enhance this AI newsletter to make it more engaging, professional, and informative.

Current newsletter:
{basic_newsletter}

Raw data for context:
- Found {len(raw_data.get('trending_repos', []))} trending repositories
- Found {len(raw_data.get('discussions', []))} interesting discussions
- Weekly stats available: {bool(raw_data.get('weekly_stats'))}

Please:
1. Improve the writing quality and tone (friendly but professional)
2. Add insights and context where appropriate
3. Ensure sections flow well together
4. Keep all repository links and data intact
5. Add engaging headlines and descriptions
6. Maintain the existing markdown structure

Return only the enhanced newsletter in markdown format."""

        try:
            message = self.anthropic_client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=4000,
                messages=[{"role": "user", "content": prompt}]
            )
            
            return message.content[0].text
            
        except Exception as e:
            logger.warning(f"Claude enhancement failed: {e}. Returning basic newsletter.")
            return basic_newsletter

# CLI interface
async def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate AI Newsletter")
    parser.add_argument("--days", type=int, default=7, help="Days to look back")
    parser.add_argument("--no-claude", action="store_true", help="Skip Claude enhancement")
    parser.add_argument("--output", type=str, help="Output file path")
    
    args = parser.parse_args()
    
    client = MCPNewsletterClient()
    newsletter = await client.generate_newsletter(
        days=args.days,
        enhance_with_claude=not args.no_claude
    )
    
    if args.output:
        with open(args.output, 'w') as f:
            f.write(newsletter)
        print(f"Newsletter saved to {args.output}")
    else:
        print(newsletter)

if __name__ == "__main__":
    asyncio.run(main())
