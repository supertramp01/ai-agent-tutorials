=======
# AI Agent Tutorials

This is course which lasts around 4 weeks which enables students to build fully functional AI Agentic apps that integrates:

- Multiple agent frameworks (Google ADK, CrewAI)
- Custom tools via Model Context Protocol (MCP)
- Cloud-hosted FastMCP servers
- Real-world actions like Google Calendar operations
- RAG pipelines & observability
- Frontend integration with Replit

Students will also get familiar with commercial agentic platforms

Pre-requisites and requirements for the course
1. Recommend using Github Code Spaces
2. Use of Serper Dev (use free api key from serper.dev)
3. Use Google Calenadar API Services
4. Use FastMCP Cloud
5. Anthropic Claude Desktop
6. Free version of Replit or equivalent AI Tool


📘 Course Outline (4 Weeks)

## Week 1 — AI Agent Fundamentals

- AI Agent Fundamentals.

  Suggested Reading: AI Agents https://huyenchip.com/2025/01/07/agents.html

- Build Agents using CrewAI

  Suggested Reading: https://github.com/crewAIInc/crewAI

  Video Tutorial: https://www.youtube.com/watch?v=-kSOTtYzgEw

- Build Agents using Google ADK

  Suggested Reading: https://google.github.io/adk-docs/get-started/python/

- Introduction to Replit and other AI Tools

Assignment: TBD


## Week 2 — MCP + Cloud Deployment

- Fundamentals of MCP (Model Context Protocol)

- Tools, resources, prompts, server structure

- Deploy FastMCP on Cloud

- Set up FastMCP Cloud instance

- Run first MCP tool remotely

- Import MCP Server into Claude Desktop

- Local testing and interactive tool invocation

Assignment: Import MCP Server in other tools and apps

# FastMCP Application

This directory contains the application code that uses the FastMCP server.

## Setup

1. Install dependencies from the root directory:
   ```bash
   pip install -e ..
   ```

2. Configure Serper.dev API key:
   
   **Option 1: Using config.json (recommended for resource example)**
   ```bash
   cp config.example.json config.json
   # Edit config.json and add your Serper.dev API key
   ```
   
   **Option 2: Using environment variable**
   ```bash
   export SERPER_API_KEY="your-api-key-here"
   ```
   
   The resource will read from `config.json` first, then fall back to the environment variable.

3. Run the application:
   ```bash
   python main.py
   ```

## MCP Server Features

The server provides:
- **Tools**: 
  - `greet`: Greet someone by name
  - `ai_search`: Search the web using Serper.dev (uses resource and prompt)
- **Resources**: 
  - `config://serper-api`: Serper.dev API configuration (reads from config.json)
- **Prompts**: 
  - `format_search_results`: Formats search results in a user-friendly way

## Usage

The application demonstrates how tools can use both resources and prompts:
- The `ai_search` tool reads the API key from the `config://serper-api` resource
- It performs a search using Serper.dev
- It formats the results using the `format_search_results` prompt


## Week 3 — TBD

## Week 4 - TBD