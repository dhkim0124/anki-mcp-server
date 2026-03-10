# anki-mcp-server

[![smithery badge](https://smithery.ai/badge/@dhkim0124/anki-mcp-server)](https://smithery.ai/server/@dhkim0124/anki-mcp-server)

*Read this in other languages: [English](README.md), [한국어](docs/README_KO.md)*

A Model Context Protocol (MCP) server that connects Claude and Anki, allowing you to create, manage, and enrich flashcard decks through natural language — without ever opening the Anki UI.

## Requirements

- Python 3.9 or higher
- Anki 2.1.x or higher
- [AnkiConnect](https://ankiweb.net/shared/info/2055492159) add-on
- Claude Desktop (or any MCP-compatible client)

## Installation

### 1. Set up Anki and AnkiConnect

1. Install [Anki](https://apps.ankiweb.net/).
2. Install the AnkiConnect add-on:
   - In Anki, go to `Tools > Add-ons > Get Add-ons`
   - Enter code `2055492159` and click OK
   - Restart Anki
3. Verify it works by visiting `http://localhost:8765` — you should see `AnkiConnect v.6`.

### 2. Install anki-mcp-server

```bash
git clone https://github.com/dhkim0124/anki-mcp-server.git
cd anki-mcp-server

python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

pip install -r requirements.txt
```

### 3. Configure Claude Desktop

Edit your Claude Desktop config file:

- **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`
- **macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Linux:** `~/.config/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "anki-mcp": {
      "command": "python",
      "args": ["/absolute/path/to/anki_server.py"]
    }
  }
}
```

## Usage

With Anki running in the background, you can ask Claude things like:

- *"Create a Python deck with Code style and add 10 cards about decorators"*
- *"Show me my decks and their stats"*
- *"Search for cards tagged 'sql' and update the one about indexes"*
- *"Create a custom dark-mode deck with fields: Word, Definition, Example, Audio"*
- *"Upload this image and attach it to a new card in my Biology deck"*
- *"Sync my collection with AnkiWeb"*

The server guides the conversation — it asks clarifying questions about deck, style, and card type before creating anything, and always asks for confirmation before destructive operations.

## Available Tools

### Deck Management

| Tool | Description |
|------|-------------|
| `list_decks` | List all decks with stats (total, new, due, learning cards) |
| `create_deck` | Create a new deck (supports nested decks with `::`) |
| `delete_deck` | Delete a deck — requires explicit confirmation |

### Card Operations

| Tool | Description |
|------|-------------|
| `create_card` | Create a single Basic card (front/back) |
| `create_card_batch` | Create multiple cards in one call |
| `create_card_custom` | Create a card using a custom note type, with optional audio/image attachments |
| `search_cards` | Search using Anki's query syntax (tags, text, deck filters) |
| `update_card` | Edit fields and tags of an existing card |
| `delete_cards` | Delete one or more cards — requires explicit confirmation |

### Note Types & Styling

| Tool | Description |
|------|-------------|
| `create_note_type` | Create a custom note type with chosen fields, CSS style, and HTML templates |
| `get_note_types` | List all available note types and their fields |
| `update_note_type_style` | Update the CSS of an existing note type |
| `update_note_type_template` | Update the HTML templates of an existing note type |

### Media & Sync

| Tool | Description |
|------|-------------|
| `add_media` | Upload an image or audio file (base64) to Anki's media folder |
| `sync_anki` | Sync your local collection with AnkiWeb |

## Style Templates

Four built-in styles are available via the `style` parameter in `create_note_type`:

| Style | Key | Best for |
|-------|-----|----------|
| Default | `"default"` | General use |
| Duolingo | `"duolingo"` | Language learning, gamified feel |
| Dark Mode | `"dark"` | Night studying, reduced eye strain |
| Code | `"code"` | Programming, algorithms |
| Custom | `"custom"` | Full control — you provide the CSS |

For **custom style**, describe what you want in natural language and Claude generates the CSS:

> *"Dark blue background, mint green accents, smooth fade-in animation"*

All custom CSS is validated to block `javascript:` URLs, `<script>` tags, and inline event handlers before being sent to Anki.

## Project Structure

```
anki-mcp-server/
├── anki_server.py      # MCP tool definitions and AnkiConnect client
├── config.py           # Constants: URL, API version, media limits
├── instructions.py     # LLM system instructions for conversational behavior
├── templates.py        # Built-in CSS themes, CSS validation, HTML generators
└── tests/
    ├── test_anki_server.py   # Tests for all tools (mocked AnkiConnect)
    └── test_templates.py     # Tests for template logic and CSS validation
```

## Running Tests

```bash
pip install pytest pytest-asyncio
pytest tests/ -v
```

All tests mock AnkiConnect via `httpx` — no running Anki instance required.

## Troubleshooting

- **Anki must be open:** The MCP server requires Anki to be running.
- **AnkiConnect not responding:** Visit `http://localhost:8765` to confirm it's active.
- **Windows firewall:** You may need to allow Anki through the firewall for AnkiConnect to work.
- **Restart everything:** If issues persist, restart Anki, Claude Desktop, and re-check the config file path.

## Contributing

Fork the repository and open a pull request. Contributions are welcome in:

- New card types or template styles
- Additional language support
- Interface and UX improvements
- Documentation

## License

MIT License — see [LICENSE](LICENSE) for details.
