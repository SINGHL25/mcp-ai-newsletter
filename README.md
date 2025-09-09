# mcp-ai-newsletter
MCP server + client project to auto-generate AI Weekly Newsletter using Claude, GitHub Issues/PRs, and Streamlit
<img width="2048" height="2048" alt="newsletter_preview" src="https://github.com/user-attachments/assets/7bde9d6a-6d65-45a9-af76-0eee2adfd261" />
🚀 Use Case – AI Weekly Newsletter

The MCP server exposes an API that:

Pulls latest AI/ML repo updates from GitHub (stars, commits, PRs).

Compiles them into a weekly "AI newsletter" draft.

The MCP client calls the server + Claude API to:

Summarize updates in human-readable format.

Suggest headlines and highlights.

Streamlit app lets users preview, edit, and export newsletter.

Output can be shared as:

Markdown (for GitHub Pages)

PDF (for email/newsletter blast)

Blog (Medium/Dev.to integration optional)

📖 Example Workflow

MCP server fetches top GitHub AI repos/issues from the past week.

Claude API is used to summarize + beautify content.

Streamlit frontend displays:

Summary cards (trending repos, issues, PRs)

Newsletter preview

Download/export button

Users can publish to GitHub Pages or export PDF.

🛠️ Tech Stack

MCP → server-client interaction (FastAPI + OpenAPI)

Claude API → text summarization & newsletter styling

GitHub API → fetch trending repos/issues

Python → backend logic

Streamlit → frontend preview + testing

Docker → containerized deployment

📚 Learning Resources

🔹 MCP Docs: Model Context Protocol GitHub

🔹 FastAPI: https://fastapi.tiangolo.com/

🔹 GitHub API: https://docs.github.com/en/rest

🔹 Streamlit: https://docs.streamlit.io/

🔹 Anthropic Claude API: https://docs.anthropic.com/

📄 README Highlights

Overview – Why MCP + AI newsletter

Setup Guide – Install dependencies, run MCP server

Run MCP Client – Example commands

Streamlit Testing – streamlit run src/streamlit_app.py

Deployment – Docker & GitHub Actions for auto-build

Future Roadmap – Adding Twitter/Reddit feeds
