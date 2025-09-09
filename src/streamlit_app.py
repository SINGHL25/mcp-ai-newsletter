
import streamlit as st
import asyncio
from client import MCPNewsletterClient
from datetime import datetime
import os

st.set_page_config(
    page_title="AI Newsletter Generator",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 AI Newsletter Generator")
st.markdown("Generate AI newsletters using GitHub data via MCP server")

# Sidebar configuration
st.sidebar.header("⚙️ Configuration")

# Check environment variables
github_token = os.getenv("GITHUB_TOKEN")
anthropic_key = os.getenv("ANTHROPIC_API_KEY")

if not github_token:
    st.sidebar.error("❌ GITHUB_TOKEN not found in environment")
if not anthropic_key:
    st.sidebar.error("❌ ANTHROPIC_API_KEY not found in environment")

# Settings
days = st.sidebar.slider("Days to look back", 1, 30, 7)
enhance_with_claude = st.sidebar.checkbox("Enhance with Claude", value=True)
server_url = st.sidebar.text_input("MCP Server URL", "http://localhost:8000")

# Generation section
st.header("📰 Generate Newsletter")

if st.button("🚀 Generate Newsletter", type="primary"):
    if not github_token or not anthropic_key:
        st.error("Please set required environment variables")
    else:
        with st.spinner("Generating newsletter... This may take a minute."):
            try:
                # Run async function
                client = MCPNewsletterClient(server_url)
                newsletter = asyncio.run(client.generate_newsletter(
                    days=days,
                    enhance_with_claude=enhance_with_claude
                ))
                
                # Display results
                st.success("✅ Newsletter generated successfully!")
                
                # Show newsletter
                st.markdown("### 📄 Generated Newsletter")
                st.markdown(newsletter)
                
                # Download option
                st.download_button(
                    label="📥 Download Newsletter",
                    data=newsletter,
                    file_name=f"ai_newsletter_{datetime.now().strftime('%Y%m%d')}.md",
                    mime="text/markdown"
                )
                
            except Exception as e:
                st.error(f"❌ Error generating newsletter: {str(e)}")

# Test server connection
st.header("🔧 Server Status")
if st.button("Test MCP Server Connection"):
    try:
        import httpx
        response = httpx.get(f"{server_url}/health")
        if response.status_code == 200:
            st.success("✅ MCP Server is running")
            st.json(response.json())
        else:
            st.error(f"❌ Server responded with status {response.status_code}")
    except Exception as e:
        st.error(f"❌ Cannot connect to server: {str(e)}")

# Instructions
st.header("📖 How to Use")
st.markdown("""
1. **Set Environment Variables:**
   ```bash
   export GITHUB_TOKEN="your_github_token"
   export ANTHROPIC_API_KEY="your_anthropic_key"
