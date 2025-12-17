# my_server.py
import os
import json
import logging
import requests
from pathlib import Path
from datetime import datetime
from fastmcp import FastMCP, Context

# Set up logging to file
log_dir = Path(__file__).parent / "logs"
log_dir.mkdir(exist_ok=True)
log_file = log_dir / "mcp.log"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()  # Also log to console
    ]
)

logger = logging.getLogger("mcp_server")

mcp = FastMCP(name="SmartSearchAgent")

@mcp.tool
def greet(name: str) -> str:
    """Greet a user by name."""
    logger.info(f"TOOL CALL: greet(name='{name}')")
    result = f"Hello, {name}!"
    logger.info(f"TOOL RESULT: greet returned: '{result}'")
    return result


# Resource: Store Serper.dev API configuration
@mcp.resource("config://serper-api")
def get_serper_config() -> dict:
    """Provides Serper.dev API configuration including API key.
    
    Reads from config.json file first, then falls back to environment variable.
    This demonstrates how resources can read from configuration files.
    """
    logger.info("RESOURCE CALL: config://serper-api")
    
    # Get the config file path (in the same directory as this file)
    config_path = Path(__file__).parent / "config.json"
    
    # Try to read from config file
    api_key = None
    api_url = "https://google.serper.dev/search"
    max_results = 10
    source = "default"
    
    if config_path.exists():
        try:
            with open(config_path, "r") as f:
                config_data = json.load(f)
                serper_config = config_data.get("serper", {})
                api_key = serper_config.get("api_key")
                api_url = serper_config.get("api_url", api_url)
                max_results = serper_config.get("max_results", max_results)
                source = "config.json"
        except (json.JSONDecodeError, KeyError) as e:
            logger.warning(f"Error reading config.json: {e}")
    
    # Fallback to environment variable if not in config file or config file doesn't exist
    if not api_key:
        api_key = os.getenv("SERPER_API_KEY", "your-api-key-here")
        source = "environment variable" if api_key != "your-api-key-here" else "default"
    
    result = {
        "api_key": api_key,
        "api_url": api_url,
        "max_results": max_results
    }
    
    logger.info(f"RESOURCE RESULT: config://serper-api - Source: {source}, API URL: {api_url}, Max Results: {max_results}")
    logger.debug(f"RESOURCE RESULT: config://serper-api - API Key configured: {'Yes' if api_key and api_key != 'your-api-key-here' else 'No'}")
    
    return result


# Prompt: Format search results in a user-friendly way
@mcp.prompt()
def format_search_results(query: str, results_json: str, num_results: str) -> str:
    """Formats search results from Serper.dev into a readable summary.
    
    Args:
        query: The search query that was executed
        results_json: JSON string of search results from Serper.dev
        num_results: Number of results found (as string)
    """
    logger.info(f"PROMPT CALL: format_search_results(query='{query}', num_results='{num_results}')")
    
    # Parse the JSON string back to a list
    try:
        results = json.loads(results_json)
        num_results_int = int(num_results)
        logger.debug(f"PROMPT: Parsed {len(results)} results from JSON")
    except (json.JSONDecodeError, ValueError) as e:
        logger.error(f"PROMPT ERROR: format_search_results - Failed to parse results: {str(e)}")
        return f"❌ Error parsing results: {str(e)}"
    
    formatted = f"🔍 Search Results for: '{query}'\n"
    formatted += f"Found {num_results_int} results\n\n"
    
    for i, result in enumerate(results[:5], 1):  # Show top 5 results
        title = result.get("title", "No title")
        link = result.get("link", "")
        snippet = result.get("snippet", "No description available")
        
        formatted += f"{i}. {title}\n"
        formatted += f"   📎 {link}\n"
        formatted += f"   {snippet}\n\n"
    
    logger.info(f"PROMPT RESULT: format_search_results - Formatted {min(5, len(results))} results for query '{query}'")
    return formatted


# Tool: Search using Serper.dev, using resource for API key and prompt for formatting
@mcp.tool
async def ai_search(query: str, ctx: Context) -> str:
    """Search the web using Serper.dev AI search API.
    
    This tool demonstrates using both a resource and a prompt:
    - Reads Serper.dev API key from the config://serper-api resource
    - Performs a search using Serper.dev API
    - Uses the format_search_results prompt to format the results
    
    Args:
        query: The search query to execute
    """
    logger.info(f"TOOL CALL: ai_search(query='{query}')")
    
    # Read API configuration from resource
    logger.info("TOOL: Reading resource config://serper-api")
    resource_data = await ctx.read_resource("config://serper-api")
    logger.info("TOOL: Resource config://serper-api read successfully")
    
    logger.debug(f"Resource data type: {type(resource_data)}")
    
    # Handle different return formats from read_resource
    # FastMCP resources might return data in different formats
    config = {}
    
    # Try to extract the actual config dict from various possible structures
    if isinstance(resource_data, dict):
        # Direct dict - use it
        config = resource_data
    elif isinstance(resource_data, list):
        # If it's a list, try to get the first item
        if resource_data:
            first_item = resource_data[0]
            if isinstance(first_item, dict):
                config = first_item
            elif hasattr(first_item, 'contents'):
                # Resource object with contents attribute
                contents = first_item.contents
                if contents and isinstance(contents[0], dict):
                    config = contents[0]
            elif hasattr(first_item, 'content'):
                content = first_item.content
                if isinstance(content, dict):
                    config = content
                elif isinstance(content, str):
                    # Might be JSON string
                    try:
                        config = json.loads(content)
                    except:
                        pass
    elif hasattr(resource_data, 'contents'):
        # Resource object with contents (plural)
        contents = resource_data.contents
        if contents and len(contents) > 0:
            first_content = contents[0]
            if hasattr(first_content, 'text'):
                # Text content - try to parse as JSON
                try:
                    config = json.loads(first_content.text)
                except:
                    pass
            elif isinstance(first_content, dict):
                config = first_content
    elif hasattr(resource_data, 'content'):
        # Resource object with content (singular)
        content = resource_data.content
        if isinstance(content, dict):
            config = content
        elif isinstance(content, str):
            try:
                config = json.loads(content)
            except:
                pass
    elif hasattr(resource_data, '__dict__'):
        # If it's an object, convert to dict
        config = resource_data.__dict__
    
    logger.debug(f"Extracted config keys: {list(config.keys()) if isinstance(config, dict) else 'N/A'}")
    
    api_key = config.get("api_key") if isinstance(config, dict) else None
    api_url = config.get("api_url", "https://google.serper.dev/search") if isinstance(config, dict) else "https://google.serper.dev/search"
    
    if not api_key or api_key == "your-api-key-here":
        logger.error("TOOL ERROR: ai_search - Serper API key not configured")
        return "❌ Error: SERPER_API_KEY not configured. Please set it as an environment variable."
    
    # Log the search request
    logger.info(f"TOOL: Calling Serper.dev API - Query: '{query}'")
    
    # Perform search using Serper.dev API
    try:
        headers = {
            "X-API-KEY": api_key,
            "Content-Type": "application/json"
        }
        payload = {
            "q": query,
            "num": 5  # Get top 5 results
        }
        
        logger.debug(f"TOOL: Serper API request details - URL: {api_url}, Payload: {json.dumps(payload)}")
        start_time = datetime.now()
        
        response = requests.post(api_url, json=payload, headers=headers, timeout=10)
        response.raise_for_status()
        search_data = response.json()
        
        elapsed_time = (datetime.now() - start_time).total_seconds()
        
        # Extract results
        organic_results = search_data.get("organic", [])
        num_results = len(organic_results)
        
        logger.info(f"TOOL: Serper API response received - Query: '{query}', Results: {num_results}, Time: {elapsed_time:.2f}s")
        
        # Use the prompt to format the results
        # MCP prompts require all arguments to be strings, so we serialize the data
        logger.info(f"TOOL: Calling prompt format_search_results for query '{query}'")
        prompt_result = await ctx.get_prompt(
            "format_search_results",
            {
                "query": query,
                "results_json": json.dumps(organic_results),  # Serialize list to JSON string
                "num_results": str(num_results)  # Convert int to string
            }
        )
        logger.info("TOOL: Prompt format_search_results completed successfully")
        
        # Extract formatted text from prompt result
        formatted_text = prompt_result.messages[0].content.text if prompt_result.messages else str(organic_results)
        
        logger.info(f"TOOL RESULT: ai_search completed successfully - Query: '{query}', Results: {num_results}")
        return formatted_text
        
    except requests.exceptions.RequestException as e:
        logger.error(f"TOOL ERROR: ai_search - Serper API request failed - Query: '{query}', Error: {str(e)}")
        return f"❌ Error performing search: {str(e)}"
    except Exception as e:
        logger.error(f"TOOL ERROR: ai_search - Unexpected error - Query: '{query}', Error: {str(e)}")
        return f"❌ Unexpected error: {str(e)}"


if __name__ == "__main__":
    # For Claude Desktop: use stdio transport (no host/port needed)
    # For HTTP client testing: use mcp.run(transport="http", host="127.0.0.1", port=8000)
    mcp.run(transport="http", host="127.0.0.1", port=8000)
    #mcp.run(transport="stdio")