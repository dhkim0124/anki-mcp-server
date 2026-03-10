# Product Requirements Document
## Anki MCP Server — Conversational Intelligence System

**Version:** 2.0
**Status:** Implemented
**Branch:** `full-control-anki`

---

## 1. Vision

Transform the Anki MCP Server from a minimal 2-tool script into a **full-featured conversational assistant** that lets users create, manage, and enrich Anki decks through natural language — without ever opening the Anki UI.

**Original limitations addressed:**
- Only `create_card` (hardcoded Basic model) and `get_decks` existed
- No custom note types, styling, or media support
- No conversational guidance or batch operations

---

## 2. Implemented Tools

All tools communicate with Anki via [AnkiConnect](https://github.com/FooSoft/anki-connect) on `localhost:8765`.

### Deck Operations

| Tool | Parameters | Returns |
|------|-----------|---------|
| `create_deck` | `name: str`, `description?: str` | `{success, deck_id, message, suggestions}` |
| `list_decks` | — | `[{name, id, total, new, due, learning}]` |
| `delete_deck` | `deck_name: str`, `confirm: bool` | `{success, message}` |

### Card Operations

| Tool | Parameters | Returns |
|------|-----------|---------|
| `create_card` | `deck_name, front, back, tags?` | `{success, card_id, message}` |
| `create_card_batch` | `deck_name, cards: list[dict], model_name?, tags?` | `{success, created, failed, ids, message}` |
| `create_card_custom` | `deck_name, model_name, fields: dict, tags?, audio?, picture?` | `{success, card_id, message}` |
| `search_cards` | `query: str`, `deck?: str` | `{results, total, suggestions}` |
| `update_card` | `note_id: int\|str`, `fields: dict`, `tags?` | `{success, message}` |
| `delete_cards` | `note_ids: list[int]`, `confirm: bool` | `{success, deleted, message}` |

### Note Types / Templates

| Tool | Parameters | Returns |
|------|-----------|---------|
| `create_note_type` | `name, fields: list, style, css?, front_template?, back_template?, is_cloze?` | `{success, model_id, message}` |
| `get_note_types` | — | `[{name, id, fields}]` |
| `update_note_type_style` | `model_name: str`, `css: str` | `{success, message}` |
| `update_note_type_template` | `model_name: str`, `templates: dict` | `{success, message}` |

### Media & Sync

| Tool | Parameters | Returns |
|------|-----------|---------|
| `add_media` | `filename: str`, `data: str (base64)`, `media_type: str` | `{success, media_path, message}` |
| `sync_anki` | — | `{success, message}` |

---

## 3. Style Templates

Four built-in CSS templates plus a fully custom mode:

| Style | Key | Description |
|-------|-----|-------------|
| Default | `"default"` | Clean Anki standard |
| Duolingo | `"duolingo"` | Green gradient, Poppins font, slide-in animation |
| Dark Mode | `"dark"` | Dark background `#1a1a1a`, cyan accent |
| Code | `"code"` | Monospace, Dracula-inspired, syntax classes |
| Custom | `"custom"` | User provides full CSS; validated before applying |

**Custom mode:** pass `style="custom"` and a complete CSS string. The LLM can generate this CSS from natural language descriptions (e.g., *"deep blue background, mint green accents, fade animations"*).

**Security:** All custom CSS is validated to reject `javascript:` URLs, `<script>` tags, `expression()`, `-moz-binding`, `behavior`, and inline event handlers.

---

## 4. Conversational Behavior

The server ships with `SERVER_INSTRUCTIONS` (in `instructions.py`) that guide the LLM to:

1. **Always clarify** deck destination, note type, and card type before creating anything
2. **Suggest styles** based on content keywords (`code` → Code style, `language/vocab` → Duolingo, `dark/night` → Dark)
3. **Use `confirm=False` first** for destructive operations, only proceeding on explicit `confirm=True`
4. **Prefer batch creation** (`create_card_batch`) for multiple cards
5. **Suggest sync** after card creation

---

## 5. Architecture

```
anki-mcp-server/
├── anki_server.py      # MCP tool definitions, AnkiConnect client
├── config.py           # Constants: URL, version, media limits
├── instructions.py     # SERVER_INSTRUCTIONS for LLM guidance
├── templates.py        # CSS templates, CSS validation, HTML generators
└── tests/
    ├── test_anki_server.py   # 54+ tests for all tools (mocked AnkiConnect)
    └── test_templates.py     # 32 tests for template logic and CSS validation
```

**Key design decisions:**
- `AnkiConnectError` exception separates API errors from HTTP errors
- CSS/HTML validation runs before any AnkiConnect call (fail fast)
- `suggest_style()` heuristic enables style auto-recommendation
- All tools return JSON strings for MCP `stdio` transport compatibility

---

## 6. Constraints

- **AnkiConnect required:** Anki must be running with the AnkiConnect plugin on port 8765
- **No JavaScript in templates:** Security restriction — CSS/static HTML only
- **Media limits:** 10 MB max; allowed types: `image/jpeg`, `image/png`, `audio/mpeg`, `audio/wav`, `audio/ogg`
- **No content generation:** The MCP creates structure/style; card content comes from the user or the LLM

---

## 7. References

- [AnkiConnect API](https://github.com/FooSoft/anki-connect)
- [Anki Template Docs](https://docs.ankiweb.net/templates/index.html)
- [Anki CSS Guide](https://docs.ankiweb.net/styling.html)
