
## 🧪 Step 7: Utility Functions

Create `src/utils.py`:

```python
import logging
import sys
from datetime import datetime
from typing import Any, Dict

def setup_logging(level=logging.INFO) -> logging.Logger:
    """Setup logging configuration"""
    logger = logging.getLogger("ai_newsletter")
    
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    
    logger.setLevel(level)
    return logger

def format_number(num: int) -> str:
    """Format numbers with commas"""
    return f"{num:,}"

def truncate_text(text: str, max_length: int = 150) -> str:
    """Truncate text to max_length with ellipsis"""
    if not text:
        return "No description available"
    
    if len(text) <= max_length:
        return text
    
    return text[:max_length].rsplit(' ', 1)[0] + "..."

def clean_repo_description(description: str) -> str:
    """Clean and format repository descriptions"""
    if not description:
        return "No description available"
    
    # Remove common markdown and special characters
    import re
    cleaned = re.sub(r'[#\*\[\]`]', '', description)
    cleaned = cleaned.strip()
    
    return truncate_text(cleaned, 200)

def validate_github_data(repo_data: Dict) -> bool:
    """Validate that repository data has required fields"""
    required_fields = ["name", "full_name", "html_url", "owner"]
    
    return all(field in repo_data for field in required_fields)

def format_date(date_string: str) -> str:
    """Format ISO date string to readable format"""
    try:
        dt = datetime.fromisoformat(date_string.replace('Z', ''))
        return dt.strftime("%B %d, %Y")
    except:
        return "Unknown date"
