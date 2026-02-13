"""Unit tests for Anki MCP Server — Phase 1, 2 & 3 tools.

All tests mock the AnkiConnect HTTP layer via httpx to avoid requiring
a running Anki instance.
"""

import base64
import json
from unittest.mock import AsyncMock, patch

import httpx
import pytest

from anki_server import (
    AnkiConnectError,
    add_media,
    create_card,
    create_card_batch,
    create_card_custom,
    create_deck,
    create_note_type,
    delete_cards,
    delete_deck,
    get_note_types,
    list_decks,
    request_anki,
    search_cards,
    sync_anki,
    update_card,
    update_note_type_style,
    update_note_type_template,
)


# ─── Helpers ───────────────────────────────────────────────────────────────────


def _anki_response(result=None, error=None):
    """Build a mock AnkiConnect JSON response."""
    return {"result": result, "error": error}


def _mock_post(result=None, error=None):
    """Return a patched httpx.AsyncClient.post that resolves to a mock response."""
    resp = AsyncMock(spec=httpx.Response)
    resp.status_code = 200
    resp.raise_for_status = lambda: None
    resp.json.return_value = _anki_response(result, error)

    client = AsyncMock(spec=httpx.AsyncClient)
    client.post.return_value = resp
    client.__aenter__ = AsyncMock(return_value=client)
    client.__aexit__ = AsyncMock(return_value=False)
    return client


# ─── request_anki ──────────────────────────────────────────────────────────────


class TestRequestAnki:
    @pytest.mark.asyncio
    async def test_success(self):
        client = _mock_post(result=42)
        with patch("anki_server.httpx.AsyncClient", return_value=client):
            result = await request_anki("testAction", key="value")
        assert result == 42

    @pytest.mark.asyncio
    async def test_anki_error(self):
        client = _mock_post(error="deck not found")
        with patch("anki_server.httpx.AsyncClient", return_value=client):
            with pytest.raises(AnkiConnectError, match="deck not found"):
                await request_anki("testAction")

    @pytest.mark.asyncio
    async def test_connection_error(self):
        client = AsyncMock(spec=httpx.AsyncClient)
        client.post.side_effect = httpx.ConnectError("refused")
        client.__aenter__ = AsyncMock(return_value=client)
        client.__aexit__ = AsyncMock(return_value=False)
        with patch("anki_server.httpx.AsyncClient", return_value=client):
            with pytest.raises(httpx.ConnectError):
                await request_anki("testAction")


# ─── create_deck ───────────────────────────────────────────────────────────────


class TestCreateDeck:
    @pytest.mark.asyncio
    async def test_success(self):
        client = _mock_post(result=1234567890)
        with patch("anki_server.httpx.AsyncClient", return_value=client):
            raw = await create_deck(name="Test Deck")
        data = json.loads(raw)
        assert data["success"] is True
        assert data["deck_id"] == "1234567890"
        assert "Test Deck" in data["message"]
        assert "suggestions" in data

    @pytest.mark.asyncio
    async def test_style_suggestion_for_code_deck(self):
        client = _mock_post(result=111)
        with patch("anki_server.httpx.AsyncClient", return_value=client):
            raw = await create_deck(name="Python Algorithms", description="programming exercises")
        data = json.loads(raw)
        assert any("code" in s.lower() for s in data["suggestions"])

    @pytest.mark.asyncio
    async def test_anki_error(self):
        client = _mock_post(error="permission denied")
        with patch("anki_server.httpx.AsyncClient", return_value=client):
            raw = await create_deck(name="Bad Deck")
        data = json.loads(raw)
        assert data["success"] is False
        assert "permission denied" in data["message"]


# ─── list_decks ────────────────────────────────────────────────────────────────


class TestListDecks:
    @pytest.mark.asyncio
    async def test_success(self):
        names_ids = {"Default": 1, "Spanish": 2}
        stats = {
            "1": {"total_in_deck": 10, "new_count": 3, "review_count": 5, "learn_count": 2},
            "2": {"total_in_deck": 20, "new_count": 8, "review_count": 10, "learn_count": 2},
        }
        call_count = 0

        async def mock_post(url, **kwargs):
            nonlocal call_count
            json_data = kwargs.get("json", {})
            action = json_data["action"]
            resp = AsyncMock(spec=httpx.Response)
            resp.status_code = 200
            resp.raise_for_status = lambda: None
            if action == "deckNamesAndIds":
                resp.json.return_value = _anki_response(names_ids)
            elif action == "getDeckStats":
                resp.json.return_value = _anki_response(stats)
            call_count += 1
            return resp

        client = AsyncMock(spec=httpx.AsyncClient)
        client.post = mock_post
        client.__aenter__ = AsyncMock(return_value=client)
        client.__aexit__ = AsyncMock(return_value=False)

        with patch("anki_server.httpx.AsyncClient", return_value=client):
            raw = await list_decks()

        decks = json.loads(raw)
        assert isinstance(decks, list)
        assert len(decks) == 2
        assert decks[0]["name"] == "Default"
        assert decks[0]["total"] == 10
        assert decks[1]["new"] == 8


# ─── delete_deck ───────────────────────────────────────────────────────────────


class TestDeleteDeck:
    @pytest.mark.asyncio
    async def test_confirm_false_returns_warning(self):
        client = _mock_post(result=[1, 2, 3])  # findCards returns 3 card IDs
        with patch("anki_server.httpx.AsyncClient", return_value=client):
            raw = await delete_deck(deck_name="OldDeck", confirm=False)
        data = json.loads(raw)
        assert data["success"] is False
        assert "3 card(s)" in data["message"]
        assert "confirm=True" in data["message"]

    @pytest.mark.asyncio
    async def test_confirm_true_deletes(self):
        client = _mock_post(result=None)  # deleteDecks returns None on success
        with patch("anki_server.httpx.AsyncClient", return_value=client):
            raw = await delete_deck(deck_name="OldDeck", confirm=True)
        data = json.loads(raw)
        assert data["success"] is True
        assert "deleted" in data["message"].lower()


# ─── create_card ───────────────────────────────────────────────────────────────


class TestCreateCard:
    @pytest.mark.asyncio
    async def test_success(self):
        client = _mock_post(result=9999)
        with patch("anki_server.httpx.AsyncClient", return_value=client):
            raw = await create_card(deck_name="MyDeck", front="Q", back="A", tags=["test"])
        data = json.loads(raw)
        assert data["success"] is True
        assert data["card_id"] == "9999"

    @pytest.mark.asyncio
    async def test_duplicate_error(self):
        client = _mock_post(error="cannot create note because it is a duplicate")
        with patch("anki_server.httpx.AsyncClient", return_value=client):
            raw = await create_card(deck_name="MyDeck", front="Q", back="A")
        data = json.loads(raw)
        assert data["success"] is False
        assert "duplicate" in data["message"]


# ─── create_card_batch ─────────────────────────────────────────────────────────


class TestCreateCardBatch:
    @pytest.mark.asyncio
    async def test_all_succeed(self):
        client = _mock_post(result=[100, 101, 102])
        with patch("anki_server.httpx.AsyncClient", return_value=client):
            cards = [
                {"Front": "Q1", "Back": "A1"},
                {"Front": "Q2", "Back": "A2"},
                {"Front": "Q3", "Back": "A3"},
            ]
            raw = await create_card_batch(deck_name="Batch", cards=cards)
        data = json.loads(raw)
        assert data["success"] is True
        assert data["created"] == 3
        assert data["failed"] == 0

    @pytest.mark.asyncio
    async def test_partial_failure(self):
        client = _mock_post(result=[100, None, 102])  # second card failed
        with patch("anki_server.httpx.AsyncClient", return_value=client):
            cards = [
                {"Front": "Q1", "Back": "A1"},
                {"Front": "Q1", "Back": "A1"},  # duplicate
                {"Front": "Q3", "Back": "A3"},
            ]
            raw = await create_card_batch(deck_name="Batch", cards=cards)
        data = json.loads(raw)
        assert data["success"] is True
        assert data["created"] == 2
        assert data["failed"] == 1
        assert "failed" in data["message"].lower()


# ─── search_cards ──────────────────────────────────────────────────────────────


class TestSearchCards:
    @pytest.mark.asyncio
    async def test_found_results(self):
        notes_info = [
            {
                "noteId": 111,
                "modelName": "Basic",
                "fields": {
                    "Front": {"value": "What is HTTP?", "order": 0},
                    "Back": {"value": "Hypertext Transfer Protocol", "order": 1},
                },
                "tags": ["networking"],
                "cards": [222],
            }
        ]
        cards_info = [{"cardId": 222, "deckName": "CS"}]

        async def mock_post(url, **kwargs):
            json_data = kwargs.get("json", {})
            action = json_data["action"]
            resp = AsyncMock(spec=httpx.Response)
            resp.status_code = 200
            resp.raise_for_status = lambda: None
            if action == "findNotes":
                resp.json.return_value = _anki_response([111])
            elif action == "notesInfo":
                resp.json.return_value = _anki_response(notes_info)
            elif action == "cardsInfo":
                resp.json.return_value = _anki_response(cards_info)
            return resp

        client = AsyncMock(spec=httpx.AsyncClient)
        client.post = mock_post
        client.__aenter__ = AsyncMock(return_value=client)
        client.__aexit__ = AsyncMock(return_value=False)

        with patch("anki_server.httpx.AsyncClient", return_value=client):
            raw = await search_cards(query="HTTP")

        data = json.loads(raw)
        assert data["total"] == 1
        assert data["results"][0]["note_id"] == "111"
        assert data["results"][0]["deck"] == "CS"
        assert data["results"][0]["fields"]["Front"] == "What is HTTP?"
        assert "suggestions" in data

    @pytest.mark.asyncio
    async def test_no_results(self):
        client = _mock_post(result=[])
        with patch("anki_server.httpx.AsyncClient", return_value=client):
            raw = await search_cards(query="nonexistent")
        data = json.loads(raw)
        assert data["results"] == []
        assert data["total"] == 0

    @pytest.mark.asyncio
    async def test_deck_scoped_search(self):
        async def mock_post(url, **kwargs):
            json_data = kwargs.get("json", {})
            action = json_data["action"]
            resp = AsyncMock(spec=httpx.Response)
            resp.status_code = 200
            resp.raise_for_status = lambda: None
            if action == "findNotes":
                query = json_data["params"]["query"]
                assert 'deck:"MyDeck"' in query
                resp.json.return_value = _anki_response([])
            return resp

        client = AsyncMock(spec=httpx.AsyncClient)
        client.post = mock_post
        client.__aenter__ = AsyncMock(return_value=client)
        client.__aexit__ = AsyncMock(return_value=False)

        with patch("anki_server.httpx.AsyncClient", return_value=client):
            raw = await search_cards(query="test", deck="MyDeck")
        data = json.loads(raw)
        assert data["results"] == []
        assert data["total"] == 0


# ─── update_card ───────────────────────────────────────────────────────────────


class TestUpdateCard:
    @pytest.mark.asyncio
    async def test_update_fields_only(self):
        client = _mock_post(result=None)
        with patch("anki_server.httpx.AsyncClient", return_value=client):
            raw = await update_card(note_id=111, fields={"Front": "Updated"})
        data = json.loads(raw)
        assert data["success"] is True

    @pytest.mark.asyncio
    async def test_update_with_tags(self):
        call_actions = []

        async def mock_post(url, **kwargs):
            json_data = kwargs.get("json", {})
            action = json_data["action"]
            call_actions.append(action)
            resp = AsyncMock(spec=httpx.Response)
            resp.status_code = 200
            resp.raise_for_status = lambda: None
            if action == "notesInfo":
                resp.json.return_value = _anki_response([{"tags": ["old1", "old2"]}])
            else:
                resp.json.return_value = _anki_response(None)
            return resp

        client = AsyncMock(spec=httpx.AsyncClient)
        client.post = mock_post
        client.__aenter__ = AsyncMock(return_value=client)
        client.__aexit__ = AsyncMock(return_value=False)

        with patch("anki_server.httpx.AsyncClient", return_value=client):
            raw = await update_card(note_id=111, fields={"Front": "X"}, tags=["new1"])

        data = json.loads(raw)
        assert data["success"] is True
        assert "updateNoteFields" in call_actions
        assert "removeTags" in call_actions
        assert "addTags" in call_actions

    @pytest.mark.asyncio
    async def test_error(self):
        client = _mock_post(error="note not found")
        with patch("anki_server.httpx.AsyncClient", return_value=client):
            raw = await update_card(note_id=999, fields={"Front": "X"})
        data = json.loads(raw)
        assert data["success"] is False
        assert "not found" in data["message"]


# ─── delete_cards ──────────────────────────────────────────────────────────────


class TestDeleteCards:
    @pytest.mark.asyncio
    async def test_confirm_false(self):
        raw = await delete_cards(note_ids=[1, 2, 3], confirm=False)
        data = json.loads(raw)
        assert data["success"] is False
        assert "3 note(s)" in data["message"]

    @pytest.mark.asyncio
    async def test_confirm_true(self):
        client = _mock_post(result=None)
        with patch("anki_server.httpx.AsyncClient", return_value=client):
            raw = await delete_cards(note_ids=[1, 2], confirm=True)
        data = json.loads(raw)
        assert data["success"] is True
        assert data["deleted"] == 2


# ─── sync_anki ─────────────────────────────────────────────────────────────────


class TestSyncAnki:
    @pytest.mark.asyncio
    async def test_success(self):
        client = _mock_post(result=None)
        with patch("anki_server.httpx.AsyncClient", return_value=client):
            raw = await sync_anki()
        data = json.loads(raw)
        assert data["success"] is True

    @pytest.mark.asyncio
    async def test_error(self):
        client = _mock_post(error="sync failed: not logged in")
        with patch("anki_server.httpx.AsyncClient", return_value=client):
            raw = await sync_anki()
        data = json.loads(raw)
        assert data["success"] is False
        assert "not logged in" in data["message"]


# ═══════════════════════════════════════════════════════════════════════════════
# Phase 2: Note Types / Templates
# ═══════════════════════════════════════════════════════════════════════════════


# ─── create_note_type ──────────────────────────────────────────────────────────


class TestCreateNoteType:
    @pytest.mark.asyncio
    async def test_success_with_default_style(self):
        model_result = {"id": 12345, "name": "MyModel"}
        client = _mock_post(result=model_result)
        with patch("anki_server.httpx.AsyncClient", return_value=client):
            raw = await create_note_type(
                name="MyModel", fields=["Front", "Back"], style="default"
            )
        data = json.loads(raw)
        assert data["success"] is True
        assert data["model_id"] == "12345"
        assert "default" in data["message"]

    @pytest.mark.asyncio
    async def test_success_with_duolingo_style(self):
        client = _mock_post(result={"id": 999})
        with patch("anki_server.httpx.AsyncClient", return_value=client):
            raw = await create_note_type(
                name="Lang", fields=["Word", "Translation"], style="duolingo"
            )
        data = json.loads(raw)
        assert data["success"] is True

    @pytest.mark.asyncio
    async def test_success_with_custom_css(self):
        client = _mock_post(result={"id": 888})
        with patch("anki_server.httpx.AsyncClient", return_value=client):
            raw = await create_note_type(
                name="Custom",
                fields=["Q", "A"],
                style="custom",
                css=".card { color: red; }",
            )
        data = json.loads(raw)
        assert data["success"] is True

    @pytest.mark.asyncio
    async def test_custom_requires_css(self):
        raw = await create_note_type(name="X", fields=["F"], style="custom", css="")
        data = json.loads(raw)
        assert data["success"] is False
        assert "requires" in data["message"].lower()

    @pytest.mark.asyncio
    async def test_rejects_dangerous_css(self):
        raw = await create_note_type(
            name="X",
            fields=["F"],
            style="custom",
            css="background: url(javascript:alert(1))",
        )
        data = json.loads(raw)
        assert data["success"] is False
        assert "validation failed" in data["message"].lower()

    @pytest.mark.asyncio
    async def test_rejects_dangerous_html_template(self):
        raw = await create_note_type(
            name="X",
            fields=["F"],
            style="default",
            front_template='<div onclick="alert(1)">{{F}}</div>',
        )
        data = json.loads(raw)
        assert data["success"] is False
        assert "validation failed" in data["message"].lower()

    @pytest.mark.asyncio
    async def test_unknown_style(self):
        raw = await create_note_type(name="X", fields=["F"], style="neon")
        data = json.loads(raw)
        assert data["success"] is False
        assert "unknown style" in data["message"].lower()

    @pytest.mark.asyncio
    async def test_empty_fields_rejected(self):
        raw = await create_note_type(name="X", fields=[], style="default")
        data = json.loads(raw)
        assert data["success"] is False

    @pytest.mark.asyncio
    async def test_cloze_model(self):
        client = _mock_post(result={"id": 777})
        with patch("anki_server.httpx.AsyncClient", return_value=client):
            raw = await create_note_type(
                name="MyCloze", fields=["Text", "Extra"], style="dark", is_cloze=True
            )
        data = json.loads(raw)
        assert data["success"] is True

    @pytest.mark.asyncio
    async def test_custom_html_templates(self):
        client = _mock_post(result={"id": 666})
        with patch("anki_server.httpx.AsyncClient", return_value=client):
            raw = await create_note_type(
                name="FullCustom",
                fields=["Q", "A"],
                style="default",
                front_template='<h1>{{Q}}</h1>',
                back_template='<h1>{{Q}}</h1><hr><p>{{A}}</p>',
            )
        data = json.loads(raw)
        assert data["success"] is True


# ─── get_note_types ────────────────────────────────────────────────────────────


class TestGetNoteTypes:
    @pytest.mark.asyncio
    async def test_success(self):
        call_count = 0

        async def mock_post(url, **kwargs):
            nonlocal call_count
            json_data = kwargs.get("json", {})
            action = json_data["action"]
            resp = AsyncMock(spec=httpx.Response)
            resp.status_code = 200
            resp.raise_for_status = lambda: None
            if action == "modelNamesAndIds":
                resp.json.return_value = _anki_response({"Basic": 1, "Cloze": 2})
            elif action == "modelFieldNames":
                name = json_data["params"]["modelName"]
                fields = {"Basic": ["Front", "Back"], "Cloze": ["Text", "Extra"]}
                resp.json.return_value = _anki_response(fields.get(name, []))
            call_count += 1
            return resp

        client = AsyncMock(spec=httpx.AsyncClient)
        client.post = mock_post
        client.__aenter__ = AsyncMock(return_value=client)
        client.__aexit__ = AsyncMock(return_value=False)

        with patch("anki_server.httpx.AsyncClient", return_value=client):
            raw = await get_note_types()

        models = json.loads(raw)
        assert len(models) == 2
        basic = next(m for m in models if m["name"] == "Basic")
        assert basic["fields"] == ["Front", "Back"]
        cloze = next(m for m in models if m["name"] == "Cloze")
        assert cloze["fields"] == ["Text", "Extra"]

    @pytest.mark.asyncio
    async def test_empty(self):
        client = _mock_post(result={})
        with patch("anki_server.httpx.AsyncClient", return_value=client):
            raw = await get_note_types()
        assert json.loads(raw) == []


# ─── create_card_custom ────────────────────────────────────────────────────────


class TestCreateCardCustom:
    @pytest.mark.asyncio
    async def test_success(self):
        client = _mock_post(result=5555)
        with patch("anki_server.httpx.AsyncClient", return_value=client):
            raw = await create_card_custom(
                deck_name="MyDeck",
                model_name="CustomModel",
                fields={"Q": "What?", "A": "That.", "Tips": "Hint"},
                tags=["test"],
            )
        data = json.loads(raw)
        assert data["success"] is True
        assert data["card_id"] == "5555"
        assert "CustomModel" in data["message"]

    @pytest.mark.asyncio
    async def test_model_not_found(self):
        client = _mock_post(error="model was not found: NonExistent")
        with patch("anki_server.httpx.AsyncClient", return_value=client):
            raw = await create_card_custom(
                deck_name="D", model_name="NonExistent", fields={"F": "v"}
            )
        data = json.loads(raw)
        assert data["success"] is False
        assert "not found" in data["message"]


# ─── update_note_type_style ───────────────────────────────────────────────────


class TestUpdateNoteTypeStyle:
    @pytest.mark.asyncio
    async def test_success(self):
        client = _mock_post(result=None)
        with patch("anki_server.httpx.AsyncClient", return_value=client):
            raw = await update_note_type_style(
                model_name="Basic", css=".card { font-size: 24px; }"
            )
        data = json.loads(raw)
        assert data["success"] is True

    @pytest.mark.asyncio
    async def test_rejects_dangerous_css(self):
        raw = await update_note_type_style(
            model_name="Basic", css="background: url(javascript:void(0))"
        )
        data = json.loads(raw)
        assert data["success"] is False
        assert "validation failed" in data["message"].lower()

    @pytest.mark.asyncio
    async def test_model_not_found(self):
        client = _mock_post(error="model was not found: Ghost")
        with patch("anki_server.httpx.AsyncClient", return_value=client):
            raw = await update_note_type_style(
                model_name="Ghost", css=".card { color: red; }"
            )
        data = json.loads(raw)
        assert data["success"] is False


# ─── update_note_type_template ─────────────────────────────────────────────────


class TestUpdateNoteTypeTemplate:
    @pytest.mark.asyncio
    async def test_success(self):
        client = _mock_post(result=None)
        with patch("anki_server.httpx.AsyncClient", return_value=client):
            raw = await update_note_type_template(
                model_name="Basic",
                templates={"Card 1": {"Front": "{{Front}}", "Back": "{{Back}}"}},
            )
        data = json.loads(raw)
        assert data["success"] is True

    @pytest.mark.asyncio
    async def test_rejects_dangerous_template(self):
        raw = await update_note_type_template(
            model_name="Basic",
            templates={"Card 1": {"Front": '<script>alert(1)</script>', "Back": "ok"}},
        )
        data = json.loads(raw)
        assert data["success"] is False
        assert "validation failed" in data["message"].lower()

    @pytest.mark.asyncio
    async def test_validates_back_template_too(self):
        raw = await update_note_type_template(
            model_name="Basic",
            templates={"Card 1": {"Front": "ok", "Back": '<img onerror="x">'}},
        )
        data = json.loads(raw)
        assert data["success"] is False


# ═══════════════════════════════════════════════════════════════════════════════
# Phase 3: Media
# ═══════════════════════════════════════════════════════════════════════════════

# Helper: a tiny valid PNG (1x1 pixel) encoded as base64
_TINY_PNG_B64 = base64.b64encode(
    b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01"
    b"\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00"
    b"\x00\x00\x0cIDATx\x9cc\xf8\x0f\x00\x00\x01\x01\x00"
    b"\x05\x18\xd8N\x00\x00\x00\x00IEND\xaeB`\x82"
).decode()

_TINY_MP3_B64 = base64.b64encode(b"\xff\xfb\x90\x00" + b"\x00" * 64).decode()


# ─── add_media ─────────────────────────────────────────────────────────────────


class TestAddMedia:
    @pytest.mark.asyncio
    async def test_upload_image_success(self):
        client = _mock_post(result="diagram.png")
        with patch("anki_server.httpx.AsyncClient", return_value=client):
            raw = await add_media(
                filename="diagram.png",
                data=_TINY_PNG_B64,
                media_type="image/png",
            )
        data = json.loads(raw)
        assert data["success"] is True
        assert data["media_path"] == "diagram.png"
        assert "<img" in data["message"]

    @pytest.mark.asyncio
    async def test_upload_audio_success(self):
        client = _mock_post(result="word.mp3")
        with patch("anki_server.httpx.AsyncClient", return_value=client):
            raw = await add_media(
                filename="word.mp3",
                data=_TINY_MP3_B64,
                media_type="audio/mpeg",
            )
        data = json.loads(raw)
        assert data["success"] is True
        assert "[sound:" in data["message"]

    @pytest.mark.asyncio
    async def test_rejects_unsupported_type(self):
        raw = await add_media(
            filename="doc.pdf",
            data=_TINY_PNG_B64,
            media_type="application/pdf",
        )
        data = json.loads(raw)
        assert data["success"] is False
        assert "unsupported" in data["message"].lower()

    @pytest.mark.asyncio
    async def test_rejects_invalid_base64(self):
        raw = await add_media(
            filename="img.png",
            data="not-valid-base64!!!",
            media_type="image/png",
        )
        data = json.loads(raw)
        assert data["success"] is False
        assert "base64" in data["message"].lower()

    @pytest.mark.asyncio
    async def test_rejects_oversized_file(self):
        # 11 MB of zeros encoded as base64
        big_data = base64.b64encode(b"\x00" * (11 * 1024 * 1024)).decode()
        raw = await add_media(
            filename="huge.png",
            data=big_data,
            media_type="image/png",
        )
        data = json.loads(raw)
        assert data["success"] is False
        assert "too large" in data["message"].lower()

    @pytest.mark.asyncio
    async def test_rejects_extension_mismatch(self):
        raw = await add_media(
            filename="photo.mp3",
            data=_TINY_PNG_B64,
            media_type="image/png",
        )
        data = json.loads(raw)
        assert data["success"] is False
        assert "extension" in data["message"].lower()

    @pytest.mark.asyncio
    async def test_anki_error(self):
        client = _mock_post(error="storage error")
        with patch("anki_server.httpx.AsyncClient", return_value=client):
            raw = await add_media(
                filename="img.png",
                data=_TINY_PNG_B64,
                media_type="image/png",
            )
        data = json.loads(raw)
        assert data["success"] is False
        assert "storage error" in data["message"]


# ─── create_card_custom with media ────────────────────────────────────────────


class TestCreateCardCustomMedia:
    @pytest.mark.asyncio
    async def test_with_audio(self):
        client = _mock_post(result=7777)
        with patch("anki_server.httpx.AsyncClient", return_value=client):
            raw = await create_card_custom(
                deck_name="Lang",
                model_name="Vocab",
                fields={"Word": "hola", "Translation": "hello"},
                audio=[{
                    "url": "https://example.com/hola.mp3",
                    "filename": "hola.mp3",
                    "fields": ["Word"],
                }],
            )
        data = json.loads(raw)
        assert data["success"] is True

    @pytest.mark.asyncio
    async def test_with_picture(self):
        client = _mock_post(result=8888)
        with patch("anki_server.httpx.AsyncClient", return_value=client):
            raw = await create_card_custom(
                deck_name="Bio",
                model_name="Anatomy",
                fields={"Name": "Heart", "Description": "Pumps blood"},
                picture=[{
                    "url": "https://example.com/heart.png",
                    "filename": "heart.png",
                    "fields": ["Name"],
                }],
            )
        data = json.loads(raw)
        assert data["success"] is True

    @pytest.mark.asyncio
    async def test_with_both_audio_and_picture(self):
        client = _mock_post(result=9999)
        with patch("anki_server.httpx.AsyncClient", return_value=client):
            raw = await create_card_custom(
                deck_name="Full",
                model_name="Rich",
                fields={"Q": "q", "A": "a"},
                audio=[{"url": "https://x.com/a.mp3", "filename": "a.mp3", "fields": ["Q"]}],
                picture=[{"url": "https://x.com/p.png", "filename": "p.png", "fields": ["A"]}],
            )
        data = json.loads(raw)
        assert data["success"] is True
