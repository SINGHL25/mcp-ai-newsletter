
import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
import httpx
from src.client import MCPNewsletterClient
from src.newsletter import NewsletterGenerator

class TestMCPNewsletterClient:
    
    @pytest.fixture
    def client(self):
        """Create test client instance"""
        with patch('src.client.anthropic.Anthropic'):
            return MCPNewsletterClient("http://test-server:8000")
    
    @pytest.fixture
    def mock_server_response(self):
        """Mock MCP server response data"""
        return {
            "trending_repos": [
                {
                    "name": "awesome-ai",
                    "full_name": "user/awesome-ai",
                    "owner": {"login": "user"},
                    "description": "An awesome AI library",
                    "html_url": "https://github.com/user/awesome-ai",
                    "stargazers_count": 1500,
                    "language": "Python",
                    "created_at": "2025-09-01T00:00:00Z"
                }
            ],
            "discussions": [
                {
                    "title": "AI Safety Discussion",
                    "body": "Important discussion about AI safety practices",
                    "html_url": "https://github.com/user/repo/issues/123",
                    "repository_url": "https://api.github.com/repos/user/repo"
                }
            ],
            "weekly_stats": {
                "total_stars": 5000,
                "total_forks": 800,
                "languages": ["Python", "JavaScript", "TypeScript"],
                "top_repos": [
                    {
                        "name": "awesome-ai",
                        "stars": 1500,
                        "forks": 300,
                        "language": "Python"
                    }
                ]
            },
            "generation_timestamp": "2025-09-09T12:00:00Z"
        }
    
    @pytest.mark.asyncio
    async def test_fetch_newsletter_data_success(self, client, mock_server_response):
        """Test successful data fetching from MCP server"""
        
        with patch('httpx.AsyncClient') as mock_client:
            # Setup mock response
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = mock_server_response
            
            mock_client.return_value.__aenter__.return_value.post = AsyncMock(
                return_value=mock_response
            )
            
            # Test the fetch
            result = await client._fetch_newsletter_data(7)
            
            # Assertions
            assert result == mock_server_response
            assert len(result["trending_repos"]) == 1
            assert result["trending_repos"][0]["name"] == "awesome-ai"
            assert result["weekly_stats"]["total_stars"] == 5000
    
    @pytest.mark.asyncio
    async def test_fetch_newsletter_data_server_error(self, client):
        """Test handling of server errors"""
        
        with patch('httpx.AsyncClient') as mock_client:
            # Setup mock error response
            mock_response = MagicMock()
            mock_response.status_code = 500
            mock_response.text = "Internal Server Error"
            
            mock_client.return_value.__aenter__.return_value.post = AsyncMock(
                return_value=mock_response
            )
            
            # Test error handling
            with pytest.raises(Exception) as exc_info:
                await client._fetch_newsletter_data(7)
            
            assert "MCP server error: 500" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_enhance_with_claude_success(self, client):
        """Test Claude enhancement functionality"""
        
        basic_newsletter = "# Basic Newsletter\nSome content here"
        mock_data = {"trending_repos": [], "discussions": []}
        enhanced_content = "# Enhanced Newsletter\nBeautiful enhanced content"
        
        # Mock Claude response
        mock_message = MagicMock()
        mock_message.content = [MagicMock(text=enhanced_content)]
        
        with patch.object(client.anthropic_client, 'messages') as mock_messages:
            mock_messages.create.return_value = mock_message
            
            result = await client._enhance_with_claude(basic_newsletter, mock_data)
            
            assert result == enhanced_content
            mock_messages.create.assert_called_once()
            
            # Check the call arguments
            call_args = mock_messages.create.call_args
            assert call_args[1]['model'] == "claude-3-sonnet-20240229"
            assert call_args[1]['max_tokens'] == 4000
    
    @pytest.mark.asyncio
    async def test_enhance_with_claude_failure(self, client):
        """Test Claude enhancement fallback on error"""
        
        basic_newsletter = "# Basic Newsletter\nSome content here"
        mock_data = {"trending_repos": [], "discussions": []}
        
        # Mock Claude API error
        with patch.object(client.anthropic_client, 'messages') as mock_messages:
            mock_messages.create.side_effect = Exception("API Error")
            
            result = await client._enhance_with_claude(basic_newsletter, mock_data)
            
            # Should return original newsletter on error
            assert result == basic_newsletter
    
    @pytest.mark.asyncio
    async def test_generate_newsletter_full_flow(self, client, mock_server_response):
        """Test complete newsletter generation flow"""
        
        enhanced_newsletter = "# Enhanced AI Newsletter\nFull content here"
        
        # Mock server response
        with patch.object(client, '_fetch_newsletter_data') as mock_fetch:
            mock_fetch.return_value = mock_server_response
            
            # Mock Claude enhancement
            with patch.object(client, '_enhance_with_claude') as mock_enhance:
                mock_enhance.return_value = enhanced_newsletter
                
                result = await client.generate_newsletter(days=7, enhance_with_claude=True)
                
                assert result == enhanced_newsletter
                mock_fetch.assert_called_once_with(7)
                mock_enhance.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_generate_newsletter_without_enhancement(self, client, mock_server_response):
        """Test newsletter generation without Claude enhancement"""
        
        with patch.object(client, '_fetch_newsletter_data') as mock_fetch:
            mock_fetch.return_value = mock_server_response
            
            # Mock newsletter generator
            with patch.object(client.newsletter_generator, 'generate_newsletter') as mock_gen:
                mock_gen.return_value = "# Basic Newsletter\nContent"
                
                result = await client.generate_newsletter(days=7, enhance_with_claude=False)
                
                assert result == "# Basic Newsletter\nContent"
                mock_fetch.assert_called_once_with(7)
                mock_gen.assert_called_once_with(mock_server_response)


class TestNewsletterClientIntegration:
    """Integration tests for client components"""
    
    @pytest.mark.asyncio
    async def test_client_with_real_newsletter_generator(self):
        """Test client with actual newsletter generator"""
        
        mock_data = {
            "trending_repos": [
                {
                    "name": "test-repo",
                    "full_name": "user/test-repo", 
                    "owner": {"login": "testuser"},
                    "description": "A test repository for AI",
                    "html_url": "https://github.com/user/test-repo",
                    "stargazers_count": 100,
                    "language": "Python"
                }
            ],
            "discussions": [],
            "weekly_stats": {"total_stars": 100},
            "generation_timestamp": "2025-09-09T12:00:00Z"
        }
        
        with patch('src.client.anthropic.Anthropic'):
            client = MCPNewsletterClient()
            
            # Use real newsletter generator
            newsletter = client.newsletter_generator.generate_newsletter(mock_data)
            
            assert "# 🤖 AI Weekly Newsletter" in newsletter
            assert "test-repo" in newsletter
            assert "testuser" in newsletter


# Fixtures for all tests
@pytest.fixture
def event_loop():
    """Create event loop for async tests"""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()
