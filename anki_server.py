from typing import Any, List
import httpx
from mcp.server.fastmcp import FastMCP

# Initialize the MCP server
mcp = FastMCP("anki-mcp-server")

# Constants for AnkiConnect API communication
ANKI_CONNECT_URL = "http://localhost:8765"


async def request_anki(action: str, **params) -> Any:
    """Send a request to AnkiConnect API.

    Args:
        action: The action to perform
        **params: Additional parameters for the action
    """
    request_data = {"action": action, "version": 6, "params": params}

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                ANKI_CONNECT_URL, json=request_data, timeout=30.0
            )
            response.raise_for_status()
            data = response.json()

            if data.get("error") is not None:
                return f"Error: {data['error']}"
            return data["result"]
        except Exception as e:
            return f"Request error: {str(e)}"


@mcp.tool()
async def create_card(
    deck_name: str, front: str, back: str, tags: List[str] = None
) -> str:
    """Create an Anki card.

    Args:
        deck_name: Name of the deck to add the card to
        front: Content for the front of the card
        back: Content for the back of the card
        tags: List of tags to add to the card (optional)
    """
    if tags is None:
        tags = []

    # Configure note information
    note = {
        "deckName": deck_name,
        "modelName": "Basic",
        "fields": {"Front": front, "Back": back},
        "tags": tags,
    }

    # Add note via AnkiConnect
    result = await request_anki("addNote", note=note)

    # Check success
    if isinstance(result, (int, str)) and not str(result).startswith("Error"):
        return f"Card successfully created. ID: {result}"
    else:
        return f"Failed to create card: {result}"


@mcp.tool()
async def get_decks() -> str:
    """Get a list of all available Anki decks."""
    decks = await request_anki("deckNames")

    if isinstance(decks, list):
        return "\n".join(decks) if decks else "No decks found."
    else:
        return f"Failed to get deck list: {decks}"


# Start the server when this script is run directly
if __name__ == "__main__":
    # Use stdio transport for Smithery deployment
    mcp.start(transport="stdio")
