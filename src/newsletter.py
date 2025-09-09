
from typing import Dict, List
from datetime import datetime
import re

class NewsletterGenerator:
    def __init__(self):
        self.template_sections = {
            "header": self._generate_header,
            "highlights": self._generate_highlights,
            "tools": self._generate_tools_section,
            "discussions": self._generate_discussions,
            "stats": self._generate_stats,
            "footer": self._generate_footer
        }
    
    def generate_newsletter(self, data: Dict) -> str:
        """Generate complete newsletter from data"""
        sections = []
        
        for section_name, generator_func in self.template_sections.items():
            try:
                section_content = generator_func(data)
                if section_content:
                    sections.append(section_content)
            except Exception as e:
                print(f"Error generating {section_name}: {e}")
        
        return "\n\n---\n\n".join(sections)
    
    def _generate_header(self, data: Dict) -> str:
        timestamp = data.get("generation_timestamp", datetime.now().isoformat())
        date_str = datetime.fromisoformat(timestamp.replace('Z', '')).strftime("%B %d, %Y")
        week_num = datetime.now().isocalendar()[1]
        
        return f"""# 🤖 AI Weekly Newsletter
*{date_str} | Week {week_num}*"""
    
    def _generate_highlights(self, data: Dict) -> str:
        repos = data.get("trending_repos", [])[:3]
        
        if not repos:
            return "## 📰 Top 3 AI Highlights\n\n*No trending repositories found this week.*"
        
        highlights = ["## 📰 Top 3 AI Highlights\n"]
        
        for i, repo in enumerate(repos, 1):
            name = repo.get("name", "Unknown")
            description = repo.get("description", "No description available")[:200]
            url = repo.get("html_url", "#")
            owner = repo.get("owner", {}).get("login", "Unknown")
            stars = repo.get("stargazers_count", 0)
            
            highlight = f"""### 🚀 **{name} by {owner}**
{description}... 

⭐ **{stars:,} stars** | **Repository:** [{owner}/{name}]({url})"""
            
            highlights.append(highlight)
        
        return "\n\n".join(highlights)
    
    def _generate_tools_section(self, data: Dict) -> str:
        repos = data.get("trending_repos", [])[3:8]  # Next 5 repos as tools
        
        if not repos:
            return "## 🛠️ New AI Tools & Libraries\n\n*No new tools discovered this week.*"
        
        tools = ["## 🛠️ New AI Tools & Libraries\n"]
        
        for repo in repos:
            name = repo.get("name", "Unknown")
            description = repo.get("description", "No description available")[:150]
            url = repo.get("html_url", "#")
            owner = repo.get("owner", {}).get("login", "Unknown")
            language = repo.get("language", "Unknown")
            
            tool = f"""### **{name}**
{description}

- **Language:** {language}
- **Repository:** [{owner}/{name}]({url})"""
            
            tools.append(tool)
        
        return "\n\n".join(tools)
    
    def _generate_discussions(self, data: Dict) -> str:
        discussions = data.get("discussions", [])[:5]
        
        if not discussions:
            return "## 🧩 Interesting Discussions & Issues\n\n*No notable discussions found this week.*"
        
        disc_section = ["## 🧩 Interesting Discussions & Issues\n"]
        
        for discussion in discussions:
            title = discussion.get("title", "Untitled")[:100]
            body = discussion.get("body", "No description")[:200]
            url = discussion.get("html_url", "#")
            repo_name = discussion.get("repository_url", "").split("/")[-1] if discussion.get("repository_url") else "Unknown"
            
            # Clean up body text
            body = re.sub(r'[#\*\[\]`]', '', body).strip()[:150]
            
            disc = f"""### **{title}**
{body}...

**Repository:** {repo_name} | [View Discussion]({url})"""
            
            disc_section.append(disc)
        
        return "\n\n".join(disc_section)
    
    def _generate_stats(self, data: Dict) -> str:
        stats = data.get("weekly_stats", {})
        
        if not stats:
            return "## 📊 Weekly Stats\n\n*Stats unavailable this week.*"
        
        total_stars = stats.get("total_stars", 0)
        total_forks = stats.get("total_forks", 0)
        languages = stats.get("languages", [])
        top_repos = stats.get("top_repos", [])
        
        stats_content = [f"""## 📊 Weekly Stats

### 🌟 **Community Growth**
- **Total Stars Tracked:** {total_stars:,}
- **Total Forks:** {total_forks:,}
- **Active Languages:** {', '.join(languages[:5])}"""]
        
        if top_repos:
            stats_content.append("### 📈 **Top Performing Repositories**")
            table_rows = ["| Repository | Stars | Forks | Language |", "|------------|-------|-------|----------|"]
            
            for repo in top_repos[:3]:
                if repo:  # Check if repo data exists
                    name = repo.get("name", "Unknown")[:20]
                    stars = repo.get("stars", 0)
                    forks = repo.get("forks", 0)
                    language = repo.get("language", "N/A") or "N/A"
                    table_rows.append(f"| **{name}** | {stars:,} | {forks:,} | {language} |")
            
            stats_content.append("\n".join(table_rows))
        
        return "\n\n".join(stats_content)
    
    def _generate_footer(self, data: Dict) -> str:
        return """## 🔮 Looking Ahead

### **What to Watch:**
- Keep an eye on emerging AI frameworks and tools
- Monitor community discussions for breakthrough insights
- Watch for new model releases and research developments

---

*That's a wrap for this week! Stay tuned for more AI developments next Monday.*

**📧 Questions or suggestions?** Open an issue on our repository.
**🔄 Share this newsletter** with your AI-enthusiastic colleagues!"""
