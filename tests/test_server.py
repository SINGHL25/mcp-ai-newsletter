
import pytest
import asyncio
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch, MagicMock
import httpx

from src.server import app, github_adapter
from src.github_adapter import GitHubAdapter

class TestMCPServer:
    
    @pytest.fixture
    def client(self):
        """Create test client for FastAPI app"""
        return TestClient(app)
    
    @pytest.fixture
    def mock_github_data(self):
        """Mock GitHub API response data"""
        return {
            "trending_repos": [
                {
                    "name": "ai-framework",
                    "full_name": "org/ai-framework",
                    "owner": {"login": "org"},
                    "description": "Advanced AI framework",
                    "html_url": "https://github.com/org/ai-framework",
                    "stargazers_count": 5000,
                    "language": "Python",
                    "created_at": "2025-09-01T00:00:00Z"
                }
            ],
            "discussions": [
                {
                    "title": "AI Safety Guidelines",
                    "body": "Discussion about AI safety best practices",
                    "html_url": "https://github.com/org/repo/issues/100",
                    "repository_url": "https://api.github.com/repos/org/repo"
                }
            ]
        }
    
    def test_health_check(self, client):
        """Test health check endpoint"""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
    
    @patch('src.server.github_adapter.get_trending_ai_repos')
    @patch('src.server.github_adapter.get_ai_discussions')
    @patch('src.server.github_adapter.get_repo_stats')
    def test_generate_newsletter_data_success(self, mock_stats, mock_discussions, mock_repos, client, mock_github_data):
        """Test successful newsletter data generation"""
        
        # Setup mocks
        mock_repos.return_value = asyncio.Future()
        mock_repos.return_value.set_result(mock_github_data["trending_repos"])
        
        mock_discussions.return_value = asyncio.Future() 
        mock_discussions.return_value.set_result(mock_github_data["discussions"])
        
        mock_stats.return_value = asyncio.Future()
        mock_stats.return_value.set_result({
            "name": "ai-framework",
            "stars": 5000,
            "forks": 1000,
            "language": "Python"
        })
        
        # Make request
        response = client.post("/generate-newsletter-data", json={
            "days": 7,
            "include_stats": True,
            "max_repos": 10
        })
        
        assert response.status_code == 200
        data = response.json()
        
        assert "trending_repos" in data
        assert "discussions" in data  
        assert "weekly_stats" in data
        assert "generation_timestamp" in data
        
        # Verify data structure
        assert len(data["trending_repos"]) >= 1
        assert data["trending_repos"][0]["name"] == "ai-framework"
    
    def test_generate_newsletter_data_validation(self, client):
        """Test request validation"""
        # Test with invalid data types
        response = client.post("/generate-newsletter-data", json={
            "days": "invalid",  # Should be int
            "include_stats": "not_boolean",  # Should be bool
            "max_repos": -1  # Should be positive
        })
        
        assert response.status_code == 422  # Validation error
    
    @patch('src.server.github_adapter.get_trending_ai_repos')
    def test_generate_newsletter_data_github_error(self, mock_repos, client):
        """Test handling of GitHub API errors"""
        
        # Setup mock to raise exception
        mock_repos.side_effect = Exception("GitHub API Error")
        
        response = client.post("/generate-newsletter-data", json={
            "days": 7
        })
        
        assert response.status_code == 500
        assert "GitHub API Error" in response.json()["detail"]
    
    @patch('src.server.github_adapter.get_trending_ai_repos')
    def test_trending_repos_endpoint(self, mock_repos, client, mock_github_data):
        """Test direct trending repos endpoint"""
        
        mock_repos.return_value = asyncio.Future()
        mock_repos.return_value.set_result(mock_github_data["trending_repos"])
        
        response = client.get("/trending-repos?days=7&limit=5")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        assert data[0]["name"] == "ai-framework"
    
    @patch('src.server.github_adapter.get_ai_discussions')
    def test_ai_discussions_endpoint(self, mock_discussions, client, mock_github_data):
        """Test direct discussions endpoint"""
        
        mock_discussions.return_value = asyncio.Future()
        mock_discussions.return_value.set_result(mock_github_data["discussions"])
        
        response = client.get("/ai-discussions?days=7&limit=5")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        assert data[0]["title"] == "AI Safety Guidelines"
    
    def test_generate_newsletter_data_default_params(self, client):
        """Test newsletter generation with default parameters"""
        with patch('src.server.github_adapter.get_trending_ai_repos') as mock_repos, \
             patch('src.server.github_adapter.get_ai_discussions') as mock_discussions:
            
            mock_repos.return_value = asyncio.Future()
            mock_repos.return_value.set_result([])
            
            mock_discussions.return_value = asyncio.Future()
            mock_discussions.return_value.set_result([])
            
            response = client.post("/generate-newsletter-data", json={})
            
            assert response.status_code == 200
            data = response.json()
            
            # Check default values were used
            assert "trending_repos" in data
            assert "discussions" in data


class TestGitHubAdapterIntegration:
    """Integration tests for GitHub adapter with server"""
    
    @pytest.fixture
    def adapter(self):
        """Create GitHub adapter instance"""
        return GitHubAdapter()
    
    @pytest.mark.asyncio
    async def test_adapter_with_mock_httpx(self, adapter):
        """Test adapter with mocked HTTP client"""
        
        mock_response_data = {
            "items": [
                {
                    "name": "test-ai-lib",
                    "full_name": "user/test-ai-lib",
                    "owner": {"login": "user"},
                    "description": "Test AI library",
                    "html_url": "https://github.com/user/test-ai-lib",
                    "stargazers_count": 100,
                    "language": "Python",
                    "created_at": "2025-09-01T00:00:00Z"
                }
            ]
        }
        
        with patch('httpx.AsyncClient') as mock_client:
            # Setup mock response
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = mock_response_data
            
            mock_client.return_value.__aenter__.return_value.get = AsyncMock(
                return_value=mock_response
            )
            
            # Test trending repos
            repos = await adapter.get_trending_ai_repos(7)
            
            assert len(repos) >= 1
            assert repos[0]["name"] == "test-ai-lib"
    
    @pytest.mark.asyncio 
    async def test_adapter_rate_limiting(self, adapter):
        """Test that adapter respects rate limiting"""
        
        with patch('httpx.AsyncClient') as mock_client, \
             patch('asyncio.sleep') as mock_sleep:
            
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"items": []}
            
            mock_client.return_value.__aenter__.return_value.get = AsyncMock(
                return_value=mock_response
            )
            
            await adapter.get_trending_ai_repos(7)
            
            # Should call sleep for rate limiting
            assert mock_sleep.called
    
    @pytest.mark.asyncio
    async def test_adapter_error_handling(self, adapter):
        """Test adapter handles HTTP errors gracefully"""
        
        with patch('httpx.AsyncClient') as mock_client:
            # Setup mock error response
            mock_response = MagicMock()
            mock_response.status_code = 403  # Rate limited
            
            mock_client.return_value.__aenter__.return_value.get = AsyncMock(
                return_value=mock_response
            )
            
            # Should return empty list on error, not raise exception
            repos = await adapter.get_trending_ai_repos(7)
            assert repos == []


class TestServerConfiguration:
    """Test server configuration and setup"""
    
    def test_server_metadata(self, client):
        """Test server metadata in OpenAPI spec"""
        response = client.get("/openapi.json")
        
        assert response.status_code == 200
        spec = response.json()
        
        assert spec["info"]["title"] == "AI Newsletter MCP Server"
        assert spec["info"]["description"] == "MCP server for AI newsletter generation"
        assert spec["info"]["version"] == "1.0.0"
    
    def test_cors_configuration(self, client):
        """Test CORS headers if configured"""
        response = client.get("/health")
        
        # Basic response test - CORS would be configured in actual deployment
        assert response.status_code == 200
    
    def test_request_validation_schemas(self, client):
        """Test Pydantic model validation"""
        # Test valid request
        valid_request = {
            "days": 7,
            "include_stats": True,
            "max_repos": 10
        }
        
        with patch('src.server.github_adapter.get_trending_ai_repos') as mock_repos, \
             patch('src.server.github_adapter.get_ai_discussions') as mock_discussions:
            
            mock_repos.return_value = asyncio.Future()
            mock_repos.return_value.set_result([])
            
            mock_discussions.return_value = asyncio.Future()
            mock_discussions.return_value.set_result([])
            
            response = client.post("/generate-newsletter-data", json=valid_request)
            assert response.status_code == 200
        
        # Test invalid request
        invalid_request = {
            "days": -5,  # Negative days
            "include_stats": "maybe",  # Wrong type
            "max_repos": "unlimited"  # Wrong type
        }
        
        response = client.post("/generate-newsletter-data", json=invalid_request)
        assert response.status_code == 422


# Test fixtures for async operations
@pytest.fixture
def event_loop():
    """Create event loop for async tests"""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()
