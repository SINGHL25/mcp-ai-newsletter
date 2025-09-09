
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
        mock_repos.return_value.set_result(mock_githu
