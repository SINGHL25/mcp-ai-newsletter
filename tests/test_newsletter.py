
import pytest
from datetime import datetime
from src.newsletter import NewsletterGenerator

class TestNewsletterGenerator:
    
    @pytest.fixture
    def generator(self):
        """Create newsletter generator instance"""
        return NewsletterGenerator()
    
    @pytest.fixture
    def sample_data(self):
        """Sample data for testing newsletter generation"""
        return {
            "trending_repos": [
                {
                    "name": "awesome-ml",
                    "full_name": "user/awesome-ml",
                    "owner": {"login": "mluser"},
                    "description": "An awesome machine learning library with advanced features",
                    "html_url": "https://github.com/user/awesome-ml",
                    "stargazers_count": 2500,
                    "language": "Python"
                },
                {
                    "name": "ai-toolkit",
                    "full_name": "dev/ai-toolkit", 
                    "owner": {"login": "developer"},
                    "description": "Comprehensive toolkit for AI development",
                    "html_url": "https://github.com/dev/ai-toolkit",
                    "stargazers_count": 1800,
                    "language": "JavaScript"
                }
            ],
            "discussions": [
                {
                    "title": "Best practices for AI model deployment",
                    "body": "Discussion about deploying machine learning models in production environments with scalability considerations",
                    "html_url": "https://github.com/user/repo/issues/456",
                    "repository_url": "https://api.github.com/repos/user/ai-deployment"
                },
                {
                    "title": "Ethics in AI development",
                    "body": "Important conversation about ethical considerations when developing AI systems",
                    "html_url": "https://github.com/ethics/ai/issues/123",
                    "repository_url": "https://api.github.com/repos/ethics/ai-ethics"
                }
            ],
            "weekly_stats": {
                "total_stars": 15000,
                "total_forks": 3200,
                "languages": ["Python", "JavaScript", "TypeScript", "Go"],
                "top_repos": [
                    {
                        "name": "awesome-ml",
                        "stars": 2500,
                        "forks": 500,
                        "language": "Python"
                    },
                    {
                        "name": "ai-toolkit", 
                        "stars": 1800,
                        "forks": 300,
                        "language": "JavaScript"
                    }
                ]
            },
            "generation_timestamp": "2025-09-09T12:00:00Z"
        }
    
    def test_generate_complete_newsletter(self, generator, sample_data):
        """Test complete newsletter generation"""
        newsletter = generator.generate_newsletter(sample_data)
        
        # Check main structure
        assert "# 🤖 AI Weekly Newsletter" in newsletter
        assert "## 📰 Top 3 AI Highlights" in newsletter
        assert "## 🛠️ New AI Tools & Libraries" in newsletter
        assert "## 🧩 Interesting Discussions & Issues" in newsletter
        assert "## 📊 Weekly Stats" in newsletter
        assert "## 🔮 Looking Ahead" in newsletter
        
        # Check content includes data
        assert "awesome-ml" in newsletter
        assert "mluser" in newsletter
        assert "2,500 stars" in newsletter
        assert "Best practices for AI model deployment" in newsletter
        assert "15,000" in newsletter  # formatted total stars
    
    def test_generate_header(self, generator, sample_data):
        """Test header generation"""
        header = generator._generate_header(sample_data)
        
        assert "# 🤖 AI Weekly Newsletter" in header
        assert "September" in header or "Week" in header
        assert "2025" in header
    
    def test_generate_highlights_with_repos(self, generator, sample_data):
        """Test highlights generation with repository data"""
        highlights = generator._generate_highlights(sample_data)
        
        assert "## 📰 Top 3 AI Highlights" in highlights
        assert "awesome-ml by mluser" in highlights
        assert "⭐ **2,500 stars**" in highlights
        assert "https://github.com/user/awesome-ml" in highlights
        assert "machine learning library" in highlights
    
    def test_generate_highlights_empty_data(self, generator):
        """Test highlights generation with no repository data"""
        empty_data = {"trending_repos": []}
        highlights = generator._generate_highlights(empty_data)
        
        assert "## 📰 Top 3 AI Highlights" in highlights
        assert "No trending repositories found" in highlights
    
    def test_generate_tools_section(self, generator, sample_data):
        """Test tools section generation"""
        tools = generator._generate_tools_section(sample_data)
        
        assert "## 🛠️ New AI Tools & Libraries" in tools
        # Should skip first 3 repos (used in highlights) and show next ones
        # With only 2 repos in sample data, this might be empty
        assert "🛠️ New AI Tools & Libraries" in tools
    
    def test_generate_discussions(self, generator, sample_data):
        """Test discussions section generation"""
        discussions = generator._generate_discussions(sample_data)
        
        assert "## 🧩 Interesting Discussions & Issues" in discussions
        assert "Best practices for AI model deployment" in discussions
        assert "Ethics in AI development" in discussions
        assert "ai-deployment" in discussions  # repo name extracted
        assert "View Discussion" in discussions
    
    def test_generate_discussions_empty(self, generator):
        """Test discussions generation with no data"""
        empty_data = {"discussions": []}
        discussions = generator._generate_discussions(empty_data)
        
        assert "## 🧩 Interesting Discussions & Issues" in discussions
        assert "No notable discussions found" in discussions
    
    def test_generate_stats(self, generator, sample_data):
        """Test stats section generation"""
        stats = generator._generate_stats(sample_data)
        
        assert "## 📊 Weekly Stats" in stats
        assert "15,000" in stats  # formatted total stars
        assert "3,200" in stats   # formatted total forks
        assert "Python, JavaScript, TypeScript, Go" in stats
        assert "Top Performing Repositories" in stats
        assert "| Repository | Stars | Forks | Language |" in stats
        assert "| **awesome-ml** | 2,500 | 500 | Python |" in stats
    
    def test_generate_stats_empty(self, generator):
        """Test stats generation with no data"""
        empty_data = {"weekly_stats": {}}
        stats = generator._generate_stats(empty_data)
        
        assert "## 📊 Weekly Stats" in stats
        assert "Stats unavailable" in stats
    
    def test_generate_footer(self, generator, sample_data):
        """Test footer generation"""
        footer = generator._generate_footer(sample_data)
        
        assert "## 🔮 Looking Ahead" in footer
        assert "What to Watch:" in footer
        assert "That's a wrap for this week!" in footer
        assert "Share this newsletter" in footer
    
    def test_newsletter_sections_integration(self, generator):
        """Test that all sections integrate properly"""
        # Test with minimal data
        minimal_data = {
            "trending_repos": [
                {
                    "name": "test-repo",
                    "owner": {"login": "testuser"},
                    "description": "Test description",
                    "html_url": "https://github.com/test/repo",
                    "stargazers_count": 100,
                    "language": "Python"
                }
            ],
            "discussions": [
                {
                    "title": "Test Discussion",
                    "body": "Test body",
                    "html_url": "https://github.com/test/issue/1"
                }
            ],
            "weekly_stats": {
                "total_stars": 100,
                "languages": ["Python"]
            },
            "generation_timestamp": "2025-09-09T12:00:00Z"
        }
        
        newsletter = generator.generate_newsletter(minimal_data)
        
        # Check that sections are properly separated
        sections = newsletter.split("\n\n---\n\n")
        assert len(sections) >= 5  # At least 5 main sections
        
        # Each section should have proper headers
        assert any("🤖 AI Weekly Newsletter" in section for section in sections)
        assert any("📰 Top 3 AI Highlights" in section for section in sections)
        assert any("📊 Weekly Stats" in section for section in sections)
    
    def test_data_sanitization(self, generator):
        """Test that newsletter handles malformed data gracefully"""
        malformed_data = {
            "trending_repos": [
                {
                    "name": None,  # None value
                    "owner": {"login": "testuser"},
                    "description": "",  # Empty string
                    "html_url": "https://github.com/test/repo",
                    "stargazers_count": "not_a_number",  # Wrong type
                    "language": "Python"
                }
            ],
            "discussions": [
                {
                    "title": "Test Discussion",
                    # Missing body
                    "html_url": "https://github.com/test/issue/1"
                }
            ],
            "weekly_stats": None,  # None stats
            "generation_timestamp": "2025-09-09T12:00:00Z"
        }
        
        # Should not raise exceptions
        newsletter = generator.generate_newsletter(malformed_data)
        
        assert "# 🤖 AI Weekly Newsletter" in newsletter
        assert "Unknown" in newsletter or "No description" in newsletter


class TestNewsletterHelpers:
    """Test helper functions and edge cases"""
    
    def test_newsletter_with_special_characters(self):
        """Test newsletter handles special characters in descriptions"""
        generator = NewsletterGenerator()
        
        special_data = {
            "trending_repos": [
                {
                    "name": "special-chars",
                    "owner": {"login": "user"},
                    "description": "Repository with **bold** and `code` and [links](url)",
                    "html_url": "https://github.com/user/special-chars",
                    "stargazers_count": 50,
                    "language": "Python"
                }
            ],
            "discussions": [
                {
                    "title": "Discussion with *markdown* and #hashtags",
                    "body": "Body with **formatting** and ```code blocks```",
                    "html_url": "https://github.com/test/issue/1"
                }
            ],
            "weekly_stats": {"total_stars": 50},
            "generation_timestamp": "2025-09-09T12:00:00Z"
        }
        
        newsletter = generator.generate_newsletter(special_data)
        
        # Should handle special characters gracefully
        assert "special-chars" in newsletter
        assert "Discussion with" in newsletter
