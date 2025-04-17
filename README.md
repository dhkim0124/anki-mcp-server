# anki-mcp-server

[![smithery badge](https://smithery.ai/badge/@dhkim0124/anki-mcp-server)](https://smithery.ai/server/@dhkim0124/anki-mcp-server)

*Read this in other languages: [English](README.md), [한국어](docs/README_KO.md)*

A Model Context Protocol (MCP) server that connects Claude and Anki, allowing you to easily create flashcards using natural language.

## Introduction

anki-mcp-server acts as a bridge between Claude and the Anki app, enabling communication between them. This allows you to give natural language commands to Claude to create and manage Anki flashcards. For example, if you request "Add an easy Japanese vocabulary card to my Japanese deck," Claude will automatically create an appropriate card.

## Requirements

- Python 3.8 or higher
- Anki 2.1.x or higher
- AnkiConnect add-on
- Claude Desktop (or an environment with access to Claude API)

## Installation

### 1. Setting up Anki and AnkiConnect

1. Install [Anki](https://apps.ankiweb.net/).
2. Install the AnkiConnect add-on:
   - Run Anki and select `Tools > Add-ons > Get Add-ons` from the top menu
   - Enter the code `2055492159` and click 'OK'
   - Restart Anki

### 2. Installing anki-mcp-server

```bash
# Clone the repository
git clone https://github.com/dhkim0124/anki-mcp-server.git
cd anki-mcp-server

# Create and activate a virtual environment (optional)
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install required packages
pip install -r requirements.txt
```

## Configuration

### Claude Desktop Setup

Modify the Claude Desktop configuration file to register the MCP server:

1. Claude Desktop configuration file location:
   - Windows: `%APPDATA%\Claude\claude_desktop_config.json`
   - macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - Linux: `~/.config/Claude/claude_desktop_config.json`

2. Add the following content to the configuration file:

```json
{
  "mcpServers": {
    "anki-mcp": {
      "command": "python",
      "args": ["path/anki_server.py"],
      "env": {}
    }
  }
}
```

Replace `path/anki_server.py` with the absolute path to your anki_server.py file.

## How to Use

1. Run the Anki application and keep it running in the background.
2. Launch Claude Desktop.
3. You can give Claude natural language commands such as:

### Example Commands

- "Add an easy Japanese vocabulary card to my Japanese deck"
- "Create a card for the English word 'perseverance' with its meaning and example sentences"
- "Summarize the programming concepts I learned today into a card"
- "Create 5 history timeline cards"

Claude will interpret these requests and create appropriate cards in Anki through the MCP server.

## Key Features

### Card Creation Features

- Basic question-answer format card creation
- Language learning card creation (word, meaning, example sentences)
- Automatic tag addition
- Adding cards to multiple decks

### Deck Management Features

- View available deck list
- Create new decks
- Search for cards in specific decks

## Troubleshooting

### Connection Issues

- **Check if Anki is running**: The MCP server requires Anki to be running to communicate with it.
- **Verify AnkiConnect**: Make sure AnkiConnect is properly installed. Visit `http://localhost:8765` in your web browser to confirm you see the "AnkiConnect v.6" message.
- **Firewall settings**: Windows users may need to allow firewall access for Anki.

### MCP Server Issues

- **Check logs**: If problems occur, check the server logs for error messages.
- **Restart**: If issues persist, try restarting Anki, Claude Desktop, and the MCP server.

## Extension and Contribution

If you'd like to contribute to the project, fork the GitHub repository and submit a pull request. We welcome contributions in the following areas:

- Support for new card types
- Improved language support
- Interface improvements
- Documentation improvements

## License

This project is distributed under the MIT License. See the LICENSE file for details.

## Contact

For issues or questions, please contact us through GitHub issues.
