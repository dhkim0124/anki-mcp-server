import base64
import json
from typing import Any, Dict, List, Optional

import httpx
from mcp.server.fastmcp import FastMCP

from templates import (
    AVAILABLE_STYLES,
    BUILTIN_TEMPLATES,
    generate_back_template,
    generate_cloze_back_template,
    generate_cloze_front_template,
    generate_front_template,
    suggest_style,
    validate_css,
)

# ─── Server Instructions (Phase 4: Conversational Intelligence) ────────────────

SERVER_INSTRUCTIONS = """\
You are an intelligent Anki assistant. You help users create, manage, and \
enrich their Anki decks through natural conversation — they should never \
need to open the Anki UI directly.

## Conversational Workflow

### Before creating anything, always clarify:
1. **Deck destination** — Ask which deck to use. Call `list_decks` to show \
   options and offer to create a new one.
2. **Note type / style** — Suggest a style based on the content:
   - Programming, algorithms, code → suggest **Code Style**
   - Languages, vocabulary, translations → suggest **Duolingo**
   - Night study, eye comfort → suggest **Dark Mode**
   - General or unsure → suggest **Default**
   - If the user wants full control → offer **Custom** (they describe the \
     look in natural language and you generate the CSS).
3. **Card type** — Basic (Q&A) or Cloze (fill-in-the-blank), depending on \
   the content.
4. **Fields** — For custom models, confirm what fields the user needs \
   (e.g. Front, Back, Example, Tips, Image, Sound).

### When creating cards:
- If the user provides a topic without explicit questions, generate card \
  content yourself and confirm before saving.
- Prefer `create_card_batch` for multiple cards — it is faster.
- After creation, suggest syncing with `sync_anki`.

### For destructive operations (delete deck/cards):
- Always call with `confirm=False` first to show the user what will be deleted.
- Only proceed with `confirm=True` after explicit user confirmation.
- Never delete without warning.

### When the user searches for cards:
- Present results grouped by deck with a summary.
- Offer to edit or delete specific results.

### Style suggestions:
- When the user describes a visual style in natural language (e.g. \
  "dark blue background, mint green accents, fade animations"), generate \
  the full CSS yourself and pass it to `create_note_type` with style="custom".
- For predefined styles, just pass the style name: "default", "duolingo", \
  "dark", or "code".

### Media:
- Use `add_media` to upload files first, then reference them in card fields.
- Images: `<img src="filename.png">`
- Audio: `[sound:filename.mp3]`
- Or use `create_card_custom` with `audio`/`picture` parameters for URL-based media.

## Response Style
- Be concise but helpful.
- After every operation, briefly suggest the logical next step.
- Use the user's language (if they write in Spanish, respond in Spanish).
"""

# Initialize the MCP server
mcp = FastMCP("anki-mcp-server", instructions=SERVER_INSTRUCTIONS)

# Constants for AnkiConnect API communication
ANKI_CONNECT_URL = "http://localhost:8765"
ANKI_CONNECT_VERSION = 6

# Media configuration
MEDIA_MAX_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB
ALLOWED_MEDIA_TYPES = {
    "image/jpeg": [".jpg", ".jpeg"],
    "image/png": [".png"],
    "audio/mpeg": [".mp3"],
    "audio/wav": [".wav"],
    "audio/ogg": [".ogg"],
}


class AnkiConnectError(Exception):
    """Raised when AnkiConnect returns an error response."""

    pass


async def request_anki(action: str, **params) -> Any:
    """Send a request to AnkiConnect API.

    Args:
        action: The AnkiConnect action to perform
        **params: Additional parameters for the action

    Returns:
        The result from AnkiConnect

    Raises:
        AnkiConnectError: When AnkiConnect returns an error
        httpx.HTTPError: When the HTTP request fails
    """
    request_data = {
        "action": action,
        "version": ANKI_CONNECT_VERSION,
        "params": params,
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(
            ANKI_CONNECT_URL, json=request_data, timeout=30.0
        )
        response.raise_for_status()
        data = response.json()

        if data.get("error") is not None:
            raise AnkiConnectError(data["error"])
        return data["result"]


# ─── Deck Operations ───────────────────────────────────────────────────────────


@mcp.tool()
async def create_deck(
    name: str,
    description: str = "",
) -> str:
    """Create a new Anki deck.

    Args:
        name: Name of the deck. Supports nested decks with :: separator (e.g. "Parent::Child")
        description: Optional description for the deck
    """
    try:
        deck_id = await request_anki("createDeck", deck=name)
        style_name, style_reason = suggest_style(name + " " + description)
        return json.dumps({
            "success": True,
            "deck_id": str(deck_id),
            "message": f"Deck '{name}' created successfully.",
            "suggestions": [
                f"Recommended style: '{style_name}' — {style_reason}",
                "Next: create a note type with `create_note_type` or add cards with `create_card`.",
            ],
        })
    except AnkiConnectError as e:
        return json.dumps({"success": False, "deck_id": None, "message": f"AnkiConnect error: {e}"})
    except Exception as e:
        return json.dumps({"success": False, "deck_id": None, "message": f"Connection error: {e}"})


@mcp.tool()
async def list_decks() -> str:
    """List all available Anki decks with statistics (total cards, new, due, learning)."""
    try:
        names_and_ids = await request_anki("deckNamesAndIds")

        deck_names = list(names_and_ids.keys())
        stats = await request_anki("getDeckStats", decks=deck_names)

        decks = []
        for name, deck_id in names_and_ids.items():
            deck_stat = stats.get(str(deck_id), {})
            decks.append({
                "name": name,
                "id": str(deck_id),
                "total": deck_stat.get("total_in_deck", 0),
                "new": deck_stat.get("new_count", 0),
                "due": deck_stat.get("review_count", 0),
                "learning": deck_stat.get("learn_count", 0),
            })

        return json.dumps(decks)
    except AnkiConnectError as e:
        return json.dumps({"error": f"AnkiConnect error: {e}"})
    except Exception as e:
        return json.dumps({"error": f"Connection error: {e}"})


@mcp.tool()
async def delete_deck(
    deck_name: str,
    confirm: bool = False,
) -> str:
    """Delete an existing Anki deck and all its cards.

    Args:
        deck_name: Name of the deck to delete
        confirm: Must be True to proceed with deletion. If False, returns a warning with card count.
    """
    try:
        if not confirm:
            cards = await request_anki("findCards", query=f'deck:"{deck_name}"')
            card_count = len(cards) if isinstance(cards, list) else 0
            return json.dumps({
                "success": False,
                "message": (
                    f"Warning: Deck '{deck_name}' contains {card_count} card(s). "
                    f"Set confirm=True to proceed with deletion."
                ),
            })

        await request_anki("deleteDecks", decks=[deck_name], cardsToo=True)
        return json.dumps({
            "success": True,
            "message": f"Deck '{deck_name}' deleted successfully.",
        })
    except AnkiConnectError as e:
        return json.dumps({"success": False, "message": f"AnkiConnect error: {e}"})
    except Exception as e:
        return json.dumps({"success": False, "message": f"Connection error: {e}"})


# ─── Card Operations ───────────────────────────────────────────────────────────


@mcp.tool()
async def create_card(
    deck_name: str, front: str, back: str, tags: List[str] | None = None
) -> str:
    """Create a single Anki card with the Basic model.

    Args:
        deck_name: Name of the deck to add the card to
        front: Content for the front of the card
        back: Content for the back of the card
        tags: Optional list of tags
    """
    try:
        note = {
            "deckName": deck_name,
            "modelName": "Basic",
            "fields": {"Front": front, "Back": back},
            "tags": tags or [],
        }
        result = await request_anki("addNote", note=note)
        return json.dumps({
            "success": True,
            "card_id": str(result),
            "message": f"Card created successfully in '{deck_name}'.",
        })
    except AnkiConnectError as e:
        return json.dumps({"success": False, "card_id": None, "message": f"AnkiConnect error: {e}"})
    except Exception as e:
        return json.dumps({"success": False, "card_id": None, "message": f"Connection error: {e}"})


@mcp.tool()
async def create_card_batch(
    deck_name: str,
    cards: List[Dict[str, str]],
    model_name: str = "Basic",
    tags: List[str] | None = None,
) -> str:
    """Create multiple Anki cards in a single operation.

    Args:
        deck_name: Name of the deck to add cards to
        cards: List of field dicts. For Basic model: [{"Front": "question", "Back": "answer"}, ...]
        model_name: Note type/model to use (default: "Basic")
        tags: Optional tags applied to all cards
    """
    try:
        notes = [
            {
                "deckName": deck_name,
                "modelName": model_name,
                "fields": card,
                "tags": tags or [],
            }
            for card in cards
        ]

        results = await request_anki("addNotes", notes=notes)

        created_ids = [str(r) for r in results if r is not None]
        failed = len(results) - len(created_ids)

        message = f"Created {len(created_ids)} of {len(cards)} card(s) in '{deck_name}'."
        if failed > 0:
            message += f" {failed} card(s) failed (possibly duplicates)."

        suggestions = ["Sync with AnkiWeb using `sync_anki` to access cards on other devices."]
        if failed > 0:
            suggestions.append("Review failed cards — they may be duplicates.")

        return json.dumps({
            "success": len(created_ids) > 0,
            "created": len(created_ids),
            "failed": failed,
            "ids": created_ids,
            "message": message,
            "suggestions": suggestions,
        })
    except AnkiConnectError as e:
        return json.dumps({"success": False, "created": 0, "failed": 0, "ids": [], "message": f"AnkiConnect error: {e}"})
    except Exception as e:
        return json.dumps({"success": False, "created": 0, "failed": 0, "ids": [], "message": f"Connection error: {e}"})


@mcp.tool()
async def search_cards(
    query: str,
    deck: str = "",
) -> str:
    """Search for notes/cards using Anki's search syntax.

    Args:
        query: Search query using Anki syntax (e.g. "tag:python", "front:*HTTP*", or plain text)
        deck: Optional deck name to limit search scope
    """
    try:
        search_query = query
        if deck:
            search_query = f'deck:"{deck}" {query}'

        note_ids = await request_anki("findNotes", query=search_query)

        if not note_ids:
            return json.dumps({"results": [], "total": 0, "suggestions": []})

        notes_info = await request_anki("notesInfo", notes=note_ids)

        # Collect all card IDs to resolve deck names
        all_card_ids = []
        note_to_cards: Dict[int, List[int]] = {}
        for note in notes_info:
            card_ids = note.get("cards", [])
            all_card_ids.extend(card_ids)
            note_to_cards[note["noteId"]] = card_ids

        # Resolve deck names from card info
        card_to_deck: Dict[int, str] = {}
        if all_card_ids:
            cards_info = await request_anki("cardsInfo", cards=all_card_ids)
            card_to_deck = {c["cardId"]: c["deckName"] for c in cards_info}

        results = []
        for note in notes_info:
            fields = note.get("fields", {})
            card_ids = note_to_cards.get(note["noteId"], [])
            deck_name = card_to_deck.get(card_ids[0], "Unknown") if card_ids else "Unknown"

            results.append({
                "note_id": str(note.get("noteId", "")),
                "model": note.get("modelName", ""),
                "deck": deck_name,
                "fields": {k: v.get("value", "") for k, v in fields.items()},
                "tags": note.get("tags", []),
            })

        suggestions = []
        if results:
            suggestions.append("Use `update_card` with a note_id to edit a specific card.")
            suggestions.append("Use `delete_cards` with note_ids to remove cards.")

        return json.dumps({
            "results": results,
            "total": len(results),
            "suggestions": suggestions,
        })
    except AnkiConnectError as e:
        return json.dumps({"error": f"AnkiConnect error: {e}"})
    except Exception as e:
        return json.dumps({"error": f"Connection error: {e}"})


@mcp.tool()
async def update_card(
    note_id: int,
    fields: Dict[str, str],
    tags: List[str] | None = None,
) -> str:
    """Update fields of an existing Anki note/card.

    Args:
        note_id: The note ID (obtained from search_cards results)
        fields: Dict of field names to new values (e.g. {"Front": "new question", "Back": "new answer"})
        tags: Optional replacement tags list. If provided, replaces all existing tags.
    """
    try:
        await request_anki("updateNoteFields", note={"id": note_id, "fields": fields})

        if tags is not None:
            note_info = await request_anki("notesInfo", notes=[note_id])
            if note_info:
                old_tags = note_info[0].get("tags", [])
                if old_tags:
                    await request_anki("removeTags", notes=[note_id], tags=" ".join(old_tags))
                if tags:
                    await request_anki("addTags", notes=[note_id], tags=" ".join(tags))

        return json.dumps({
            "success": True,
            "message": f"Note {note_id} updated successfully.",
        })
    except AnkiConnectError as e:
        return json.dumps({"success": False, "message": f"AnkiConnect error: {e}"})
    except Exception as e:
        return json.dumps({"success": False, "message": f"Connection error: {e}"})


@mcp.tool()
async def delete_cards(
    note_ids: List[int],
    confirm: bool = False,
) -> str:
    """Delete one or more Anki notes and their associated cards.

    Args:
        note_ids: List of note IDs to delete (obtained from search_cards results)
        confirm: Must be True to proceed with deletion
    """
    try:
        if not confirm:
            return json.dumps({
                "success": False,
                "deleted": 0,
                "message": (
                    f"Warning: About to delete {len(note_ids)} note(s) and all their cards. "
                    f"Set confirm=True to proceed."
                ),
            })

        await request_anki("deleteNotes", notes=note_ids)
        return json.dumps({
            "success": True,
            "deleted": len(note_ids),
            "message": f"Successfully deleted {len(note_ids)} note(s).",
        })
    except AnkiConnectError as e:
        return json.dumps({"success": False, "deleted": 0, "message": f"AnkiConnect error: {e}"})
    except Exception as e:
        return json.dumps({"success": False, "deleted": 0, "message": f"Connection error: {e}"})


# ─── Note Types / Models (Phase 2) ─────────────────────────────────────────────


@mcp.tool()
async def create_note_type(
    name: str,
    fields: List[str],
    style: str = "default",
    css: str = "",
    front_template: str = "",
    back_template: str = "",
    is_cloze: bool = False,
) -> str:
    """Create a custom note type/model with CSS styling and HTML templates.

    Args:
        name: Name of the note type
        fields: List of field names (e.g. ["Front", "Back", "Example", "Tips"])
        style: Predefined style name ("default", "duolingo", "dark", "code") or "custom"
        css: Custom CSS styling. Required when style="custom". Ignored for predefined styles.
        front_template: Custom front HTML template. Use {{FieldName}} for fields. Auto-generated if empty.
        back_template: Custom back HTML template. Use {{FieldName}} for fields. Auto-generated if empty.
        is_cloze: Whether this is a Cloze (fill-in-the-blank) model. Use {{cloze:FieldName}} in templates.
    """
    try:
        if not fields:
            return json.dumps({"success": False, "model_id": None, "message": "At least one field is required."})

        # Resolve CSS
        if style == "custom":
            if not css:
                return json.dumps({"success": False, "model_id": None, "message": "Custom style requires the 'css' parameter."})
            is_valid, error = validate_css(css)
            if not is_valid:
                return json.dumps({"success": False, "model_id": None, "message": f"CSS validation failed: {error}"})
            final_css = css
        elif style in BUILTIN_TEMPLATES:
            final_css = BUILTIN_TEMPLATES[style]
        else:
            return json.dumps({
                "success": False,
                "model_id": None,
                "message": f"Unknown style '{style}'. Available: {', '.join(AVAILABLE_STYLES)}",
            })

        # Resolve HTML templates
        if front_template or back_template:
            for label, content in [("Front template", front_template), ("Back template", back_template)]:
                if content:
                    is_valid, error = validate_css(content)
                    if not is_valid:
                        return json.dumps({"success": False, "model_id": None, "message": f"{label} validation failed: {error}"})
            front_html = front_template or (generate_cloze_front_template(fields) if is_cloze else generate_front_template(fields))
            back_html = back_template or (generate_cloze_back_template(fields) if is_cloze else generate_back_template(fields))
        elif is_cloze:
            front_html = generate_cloze_front_template(fields)
            back_html = generate_cloze_back_template(fields)
        else:
            front_html = generate_front_template(fields)
            back_html = generate_back_template(fields)

        card_template_name = "Cloze" if is_cloze else name
        result = await request_anki(
            "createModel",
            modelName=name,
            inOrderFields=fields,
            css=final_css,
            isCloze=is_cloze,
            cardTemplates=[{
                "Name": card_template_name,
                "Front": front_html,
                "Back": back_html,
            }],
        )

        model_id = str(result.get("id", "")) if isinstance(result, dict) else str(result)
        return json.dumps({
            "success": True,
            "model_id": model_id,
            "message": f"Note type '{name}' created with style '{style}'.",
            "suggestions": [
                f"Create cards using this model with `create_card_custom(model_name='{name}', ...)`.",
                "You can update the style later with `update_note_type_style` or `update_note_type_template`.",
            ],
        })
    except AnkiConnectError as e:
        return json.dumps({"success": False, "model_id": None, "message": f"AnkiConnect error: {e}"})
    except Exception as e:
        return json.dumps({"success": False, "model_id": None, "message": f"Connection error: {e}"})


@mcp.tool()
async def get_note_types() -> str:
    """List all available note types/models with their field names."""
    try:
        model_names_ids = await request_anki("modelNamesAndIds")

        if not model_names_ids:
            return json.dumps([])

        models = []
        for name, model_id in model_names_ids.items():
            fields = await request_anki("modelFieldNames", modelName=name)
            models.append({
                "name": name,
                "id": str(model_id),
                "fields": fields if isinstance(fields, list) else [],
            })

        return json.dumps(models)
    except AnkiConnectError as e:
        return json.dumps({"error": f"AnkiConnect error: {e}"})
    except Exception as e:
        return json.dumps({"error": f"Connection error: {e}"})


@mcp.tool()
async def create_card_custom(
    deck_name: str,
    model_name: str,
    fields: Dict[str, str],
    tags: List[str] | None = None,
    audio: List[Dict[str, str]] | None = None,
    picture: List[Dict[str, str]] | None = None,
) -> str:
    """Create a card using a custom note type with dynamic fields and optional media.

    Args:
        deck_name: Name of the deck to add the card to
        model_name: Name of the note type/model to use (created via create_note_type)
        fields: Dict of field names to values. Must match the model's fields.
        tags: Optional list of tags
        audio: Optional list of audio attachments. Each dict should have:
               - "url" or "data" (base64): the audio source
               - "filename": target filename in Anki media
               - "fields": list of field names where [sound:filename] will be inserted
        picture: Optional list of image attachments. Each dict should have:
                 - "url" or "data" (base64): the image source
                 - "filename": target filename in Anki media
                 - "fields": list of field names where <img src="filename"> will be inserted
    """
    try:
        note: Dict[str, Any] = {
            "deckName": deck_name,
            "modelName": model_name,
            "fields": fields,
            "tags": tags or [],
        }
        if audio:
            note["audio"] = audio
        if picture:
            note["picture"] = picture

        result = await request_anki("addNote", note=note)
        return json.dumps({
            "success": True,
            "card_id": str(result),
            "message": f"Custom card created in '{deck_name}' using model '{model_name}'.",
        })
    except AnkiConnectError as e:
        return json.dumps({"success": False, "card_id": None, "message": f"AnkiConnect error: {e}"})
    except Exception as e:
        return json.dumps({"success": False, "card_id": None, "message": f"Connection error: {e}"})


@mcp.tool()
async def update_note_type_style(
    model_name: str,
    css: str,
) -> str:
    """Update the CSS styling of an existing note type/model.

    Args:
        model_name: Name of the note type to update
        css: New CSS styling to apply
    """
    try:
        is_valid, error = validate_css(css)
        if not is_valid:
            return json.dumps({"success": False, "message": f"CSS validation failed: {error}"})

        await request_anki("updateModelStyling", model={"name": model_name, "css": css})
        return json.dumps({
            "success": True,
            "message": f"CSS updated for note type '{model_name}'.",
        })
    except AnkiConnectError as e:
        return json.dumps({"success": False, "message": f"AnkiConnect error: {e}"})
    except Exception as e:
        return json.dumps({"success": False, "message": f"Connection error: {e}"})


@mcp.tool()
async def update_note_type_template(
    model_name: str,
    templates: Dict[str, Dict[str, str]],
) -> str:
    """Update HTML templates of an existing note type/model.

    Args:
        model_name: Name of the note type to update
        templates: Dict of template name to {"Front": "html", "Back": "html"}.
                   Example: {"Card 1": {"Front": "{{Front}}", "Back": "{{Back}}"}}
    """
    try:
        for tpl_name, tpl in templates.items():
            for side in ("Front", "Back"):
                if side in tpl:
                    is_valid, error = validate_css(tpl[side])
                    if not is_valid:
                        return json.dumps({
                            "success": False,
                            "message": f"Template '{tpl_name}' {side} validation failed: {error}",
                        })

        await request_anki("updateModelTemplates", model={"name": model_name, "templates": templates})
        return json.dumps({
            "success": True,
            "message": f"Templates updated for note type '{model_name}'.",
        })
    except AnkiConnectError as e:
        return json.dumps({"success": False, "message": f"AnkiConnect error: {e}"})
    except Exception as e:
        return json.dumps({"success": False, "message": f"Connection error: {e}"})


# ─── Media (Phase 3) ──────────────────────────────────────────────────────────


@mcp.tool()
async def add_media(
    filename: str,
    data: str,
    media_type: str,
) -> str:
    """Upload an image or audio file to Anki's media folder for use in cards.

    The uploaded file can then be referenced in card fields:
    - Images: <img src="filename.png">
    - Audio: [sound:filename.mp3]

    Args:
        filename: Target filename in Anki media (e.g. "diagram.png", "pronunciation.mp3")
        data: File content encoded as base64 string
        media_type: MIME type of the file. Allowed: image/jpeg, image/png, audio/mpeg, audio/wav, audio/ogg
    """
    try:
        # Validate media type
        if media_type not in ALLOWED_MEDIA_TYPES:
            allowed = ", ".join(sorted(ALLOWED_MEDIA_TYPES.keys()))
            return json.dumps({
                "success": False,
                "media_path": None,
                "message": f"Unsupported media type '{media_type}'. Allowed: {allowed}",
            })

        # Validate base64 and check size
        try:
            decoded = base64.b64decode(data, validate=True)
        except Exception:
            return json.dumps({
                "success": False,
                "media_path": None,
                "message": "Invalid base64 data.",
            })

        if len(decoded) > MEDIA_MAX_SIZE_BYTES:
            max_mb = MEDIA_MAX_SIZE_BYTES // (1024 * 1024)
            actual_mb = round(len(decoded) / (1024 * 1024), 2)
            return json.dumps({
                "success": False,
                "media_path": None,
                "message": f"File too large ({actual_mb} MB). Maximum allowed: {max_mb} MB.",
            })

        # Validate file extension matches media type
        valid_extensions = ALLOWED_MEDIA_TYPES[media_type]
        if not any(filename.lower().endswith(ext) for ext in valid_extensions):
            return json.dumps({
                "success": False,
                "media_path": None,
                "message": f"Filename '{filename}' extension doesn't match type '{media_type}'. Expected: {', '.join(valid_extensions)}",
            })

        # Upload via AnkiConnect
        result = await request_anki("storeMediaFile", filename=filename, data=data)

        # Build usage hint
        if media_type.startswith("image/"):
            usage = f'<img src="{filename}">'
        else:
            usage = f"[sound:{filename}]"

        return json.dumps({
            "success": True,
            "media_path": filename,
            "message": f"Media '{filename}' uploaded successfully. Use in cards: {usage}",
            "suggestions": [
                f"Reference in card fields: {usage}",
                "Or use `create_card_custom` with audio/picture parameters to attach media directly.",
            ],
        })
    except AnkiConnectError as e:
        return json.dumps({"success": False, "media_path": None, "message": f"AnkiConnect error: {e}"})
    except Exception as e:
        return json.dumps({"success": False, "media_path": None, "message": f"Connection error: {e}"})


# ─── Sync ──────────────────────────────────────────────────────────────────────


@mcp.tool()
async def sync_anki() -> str:
    """Synchronize local Anki collection with AnkiWeb for cross-platform access."""
    try:
        await request_anki("sync")
        return json.dumps({
            "success": True,
            "message": "Sync with AnkiWeb completed successfully.",
        })
    except AnkiConnectError as e:
        return json.dumps({"success": False, "message": f"AnkiConnect error: {e}"})
    except Exception as e:
        return json.dumps({"success": False, "message": f"Connection error: {e}"})


# ─── Entry Point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import os

    transport = os.environ.get("MCP_TRANSPORT", "stdio")
    mcp.run(transport=transport)
