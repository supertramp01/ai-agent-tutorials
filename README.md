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




