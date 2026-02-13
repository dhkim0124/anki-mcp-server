"""Unit tests for templates module — CSS/HTML templates, validation, and suggestions."""

import pytest

from templates import (
    BUILTIN_TEMPLATES,
    generate_back_template,
    generate_cloze_back_template,
    generate_cloze_front_template,
    generate_front_template,
    suggest_style,
    validate_css,
)


# ─── validate_css ──────────────────────────────────────────────────────────────


class TestValidateCSS:
    def test_valid_css(self):
        css = ".card { color: red; background-color: #1a1a1a; }"
        is_valid, error = validate_css(css)
        assert is_valid is True
        assert error == ""

    def test_valid_css_with_keyframes(self):
        css = "@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }"
        is_valid, _ = validate_css(css)
        assert is_valid is True

    def test_valid_css_with_variables(self):
        css = ":root { --accent: #00bcd4; } .card { color: var(--accent); }"
        is_valid, _ = validate_css(css)
        assert is_valid is True

    def test_rejects_javascript_url(self):
        is_valid, error = validate_css("background: url(javascript:alert(1))")
        assert is_valid is False
        assert "javascript" in error.lower()

    def test_rejects_javascript_url_case_insensitive(self):
        is_valid, _ = validate_css("background: url(JaVaScRiPt:alert(1))")
        assert is_valid is False

    def test_rejects_script_tag(self):
        is_valid, error = validate_css('<script>alert("xss")</script>')
        assert is_valid is False
        assert "script" in error.lower()

    def test_rejects_expression(self):
        is_valid, _ = validate_css("width: expression(document.body.clientWidth)")
        assert is_valid is False

    def test_rejects_moz_binding(self):
        is_valid, _ = validate_css("-moz-binding: url(evil.xml)")
        assert is_valid is False

    def test_rejects_behavior(self):
        is_valid, _ = validate_css("behavior: url(evil.htc)")
        assert is_valid is False

    def test_rejects_inline_event_handler(self):
        is_valid, error = validate_css('<div onclick="alert(1)">')
        assert is_valid is False
        assert "event handler" in error.lower()

    def test_rejects_onerror_handler(self):
        is_valid, _ = validate_css('<img onerror="alert(1)">')
        assert is_valid is False

    def test_all_builtin_templates_are_valid(self):
        for name, css in BUILTIN_TEMPLATES.items():
            is_valid, error = validate_css(css)
            assert is_valid is True, f"Builtin template '{name}' failed validation: {error}"


# ─── HTML Template Generation ──────────────────────────────────────────────────


class TestGenerateFrontTemplate:
    def test_basic_fields(self):
        html = generate_front_template(["Front", "Back"])
        assert "{{Front}}" in html
        assert "{{Back}}" not in html

    def test_single_field(self):
        html = generate_front_template(["Question"])
        assert "{{Question}}" in html

    def test_empty_fields_fallback(self):
        html = generate_front_template([])
        assert "{{Front}}" in html


class TestGenerateBackTemplate:
    def test_basic_fields(self):
        html = generate_back_template(["Front", "Back"])
        assert "{{Front}}" in html
        assert "{{Back}}" in html

    def test_multiple_extra_fields(self):
        html = generate_back_template(["Q", "A", "Example", "Tips"])
        assert "{{Q}}" in html
        assert "{{A}}" in html
        assert "{{Example}}" in html
        assert "{{Tips}}" in html
        # Extra fields use conditional rendering
        assert "{{#Example}}" in html
        assert "{{/Example}}" in html

    def test_empty_fields_fallback(self):
        html = generate_back_template([])
        assert "{{Back}}" in html


class TestGenerateClozeFrontTemplate:
    def test_basic(self):
        html = generate_cloze_front_template(["Text", "Extra"])
        assert "{{cloze:Text}}" in html
        assert "Extra" not in html

    def test_empty_fields_fallback(self):
        html = generate_cloze_front_template([])
        assert "{{cloze:Text}}" in html


class TestGenerateClozeBackTemplate:
    def test_basic(self):
        html = generate_cloze_back_template(["Text", "Extra"])
        assert "{{cloze:Text}}" in html
        assert "{{Extra}}" in html

    def test_single_field(self):
        html = generate_cloze_back_template(["Text"])
        assert "{{cloze:Text}}" in html
        assert "<hr>" not in html

    def test_empty_fields_fallback(self):
        html = generate_cloze_back_template([])
        assert "{{cloze:Text}}" in html


# ─── suggest_style (Phase 4) ──────────────────────────────────────────────────


class TestSuggestStyle:
    def test_code_keywords(self):
        style, reason = suggest_style("Python algorithms and data structures")
        assert style == "code"

    def test_language_keywords(self):
        style, reason = suggest_style("Spanish vocabulary and grammar")
        assert style == "duolingo"

    def test_dark_keywords(self):
        style, reason = suggest_style("Night study session, dark mode")
        assert style == "dark"

    def test_default_fallback(self):
        style, reason = suggest_style("General knowledge trivia")
        assert style == "default"
        assert "default" in reason.lower()

    def test_mixed_content_picks_strongest(self):
        style, _ = suggest_style("Python function for translating Japanese sentences")
        # "python", "function" → code (2 hits) vs "japanese", "sentence" → duolingo (2 hits)
        # Both tied, but code keywords come first alphabetically in dict iteration;
        # the important thing is it picks one of the relevant styles
        assert style in ("code", "duolingo")

    def test_case_insensitive(self):
        style, _ = suggest_style("JAVASCRIPT and TYPESCRIPT programming")
        assert style == "code"

    def test_empty_string(self):
        style, _ = suggest_style("")
        assert style == "default"

    def test_reason_is_nonempty(self):
        _, reason = suggest_style("SQL database queries")
        assert len(reason) > 0
