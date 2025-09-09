
import pytest
from src.newsletter import NewsletterGenerator

def test_newsletter_generation():
    generator = NewsletterGenerator()
    
    # Mock data
    test_data = {
        "trending_repos": [
            {
                "name": "test-repo",
                "owner": {"login": "testuser"},
                "description": "Test repository",
                "html_url": "https://github.com/testuser/test-repo",
                "stargazers_count": 100
            }
        ],
        "discussions": [
            {
                "title": "Test Discussion",
                "body": "Test discussion body",
                "html_url": "https://github.com/test/issue/1"
            }
        ],
        "weekly_stats": {
            "total_stars": 1000,
            "total_forks": 200,
            "languages": ["Python", "JavaScript"]
        },
        "generation_timestamp": "2025-09-09T12:00:00"
    }
    
    newsletter = generator.generate_newsletter(test_data)
    
    assert "# 🤖 AI Weekly Newsletter" in newsletter
    assert "test-repo" in newsletter
    assert "Test Discussion" in newsletter
    assert "1,000" in newsletter  # Formatted number
