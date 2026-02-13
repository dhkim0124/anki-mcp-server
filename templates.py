"""Predefined CSS/HTML templates and content validation for Anki MCP Server.

Provides:
- 4 builtin CSS templates: Default, Duolingo, Dark Mode, Code Style
- HTML template generation for Basic and Cloze card types
- Security validation for CSS and HTML (no JavaScript execution)

Supported CSS capabilities:
- Colors: color, background-color, background-image, border-color
- Typography: font-family, font-size, font-weight, line-height
- Layout: padding, margin, max-width, border-radius
- Animations: @keyframes, animation, transition
- CSS variables: --variable-name
- Media queries: @media (prefers-color-scheme: dark)
- Effects: box-shadow, filter, transform, opacity
"""

import re

# ─── Predefined CSS Templates ──────────────────────────────────────────────────

TEMPLATE_DEFAULT_CSS = """\
.card {
  font-family: Arial, sans-serif;
  font-size: 20px;
  text-align: center;
  color: #000;
  background-color: #fff;
}"""

TEMPLATE_DUOLINGO_CSS = """\
.card {
  font-family: 'Poppins', sans-serif;
  font-size: 18px;
  background: linear-gradient(135deg, #1f8722 0%, #28a745 100%);
  color: #fff;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 8px 16px rgba(0,0,0,0.2);
  animation: slideIn 0.3s ease-in-out;
}

.question {
  font-weight: bold;
  margin-bottom: 16px;
  font-size: 22px;
}

.answer {
  margin-top: 12px;
  font-size: 18px;
  animation: fadeIn 0.5s ease-in;
}

@keyframes slideIn {
  from { transform: translateY(10px); opacity: 0; }
  to { transform: translateY(0); opacity: 1; }
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}"""

TEMPLATE_DARK_CSS = """\
.card {
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  font-size: 18px;
  background-color: #1a1a1a;
  color: #e0e0e0;
  padding: 20px;
  border-left: 4px solid #00bcd4;
}

.question {
  color: #00bcd4;
  font-weight: 600;
  font-size: 20px;
  margin-bottom: 16px;
}

.answer {
  color: #e0e0e0;
  margin-top: 12px;
  line-height: 1.6;
}

code {
  background-color: #2a2a2a;
  color: #76ff03;
  padding: 2px 6px;
  border-radius: 3px;
}"""

TEMPLATE_CODE_CSS = """\
.card {
  font-family: 'JetBrains Mono', 'Fira Code', monospace;
  font-size: 16px;
  background-color: #282c34;
  color: #abb2bf;
  padding: 20px;
  border-radius: 8px;
  overflow-x: auto;
}

.question {
  color: #61dafb;
  font-weight: bold;
  margin-bottom: 12px;
}

.answer {
  color: #98c379;
  margin-top: 12px;
  white-space: pre-wrap;
}

code {
  color: #e06c75;
}

.keyword { color: #f92672; }
.string { color: #a6e22e; }
.function { color: #66d9ef; }
.comment { color: #75715e; }"""

BUILTIN_TEMPLATES = {
    "default": TEMPLATE_DEFAULT_CSS,
    "duolingo": TEMPLATE_DUOLINGO_CSS,
    "dark": TEMPLATE_DARK_CSS,
    "code": TEMPLATE_CODE_CSS,
}

AVAILABLE_STYLES = list(BUILTIN_TEMPLATES.keys()) + ["custom"]

# ─── Content Validation ────────────────────────────────────────────────────────

_DANGEROUS_PATTERNS = [
    (re.compile(r"javascript\s*:", re.IGNORECASE), "javascript: URL"),
    (re.compile(r"<\s*script", re.IGNORECASE), "<script> tag"),
    (re.compile(r"expression\s*\(", re.IGNORECASE), "CSS expression()"),
    (re.compile(r"-moz-binding\s*:", re.IGNORECASE), "-moz-binding property"),
    (re.compile(r"behavior\s*:", re.IGNORECASE), "behavior property"),
    (re.compile(r"\bon\w+\s*=", re.IGNORECASE), "inline event handler"),
]


def validate_css(css: str) -> tuple[bool, str]:
    """Validate CSS/HTML content for security.

    Rejects content containing JavaScript execution vectors:
    - javascript: URLs
    - <script> tags
    - CSS expression() (legacy IE)
    - -moz-binding / behavior (legacy browser XSS)
    - Inline event handlers (onclick=, onerror=, etc.)

    Returns:
        Tuple of (is_valid, error_message). error_message is empty when valid.
    """
    for pattern, description in _DANGEROUS_PATTERNS:
        if pattern.search(css):
            return False, f"Forbidden pattern detected: {description}"
    return True, ""


# ─── HTML Template Generation ──────────────────────────────────────────────────


# ─── Style Suggestion (Phase 4: Conversational Intelligence) ───────────────────

_STYLE_KEYWORDS: dict[str, list[str]] = {
    "code": [
        "code", "coding", "programming", "algorithm", "function", "class",
        "python", "javascript", "typescript", "java", "rust", "go", "c++",
        "sql", "html", "css", "api", "debug", "syntax", "compiler",
        "data structure", "leetcode", "regex",
    ],
    "duolingo": [
        "language", "idiom", "vocabulary", "vocab", "translation", "grammar",
        "verb", "noun", "conjugation", "pronunciation", "spanish", "french",
        "german", "italian", "portuguese", "japanese", "korean", "chinese",
        "english", "word", "phrase", "sentence", "dialogue",
    ],
    "dark": [
        "dark", "night", "nocturnal", "eye strain", "low light",
    ],
}


def suggest_style(content: str) -> tuple[str, str]:
    """Suggest a template style based on content keywords.

    Analyzes the provided text for topic-related keywords and returns the
    best-matching predefined style.

    Args:
        content: Text describing the deck topic or card content.

    Returns:
        Tuple of (style_name, reason). style_name is one of the BUILTIN_TEMPLATES
        keys ("default", "duolingo", "dark", "code").
    """
    content_lower = content.lower()

    scores: dict[str, int] = {style: 0 for style in _STYLE_KEYWORDS}
    for style, keywords in _STYLE_KEYWORDS.items():
        for keyword in keywords:
            if keyword in content_lower:
                scores[style] += 1

    best_style = max(scores, key=scores.get)  # type: ignore[arg-type]
    if scores[best_style] == 0:
        return "default", "No specific topic detected — using clean default style."

    reasons = {
        "code": "Content appears to be programming-related — Code Style with monospace font and syntax highlighting.",
        "duolingo": "Content appears to be language-related — Duolingo style with vibrant colors and gamified design.",
        "dark": "Content suggests night/dark preference — Dark Mode with high contrast for reduced eye strain.",
    }
    return best_style, reasons[best_style]


# ─── HTML Template Generation ──────────────────────────────────────────────────


def generate_front_template(fields: list[str]) -> str:
    """Generate a front HTML template using the first field."""
    first_field = fields[0] if fields else "Front"
    return (
        '<div class="card">\n'
        '  <div class="question">{{' + first_field + "}}</div>\n"
        "</div>"
    )


def generate_back_template(fields: list[str]) -> str:
    """Generate a back HTML template showing the first field plus all remaining fields."""
    if not fields:
        return (
            '<div class="card">\n'
            '  <div class="answer">{{Back}}</div>\n'
            "</div>"
        )

    first_field = fields[0]
    lines = ['<div class="card">']
    lines.append('  <div class="question">{{' + first_field + "}}</div>")
    lines.append("  <hr>")

    for field in fields[1:]:
        lines.append("  {{#" + field + "}}")
        lines.append('  <div class="answer">{{' + field + "}}</div>")
        lines.append("  {{/" + field + "}}")

    lines.append("</div>")
    return "\n".join(lines)


def generate_cloze_front_template(fields: list[str]) -> str:
    """Generate a front HTML template for Cloze cards."""
    first_field = fields[0] if fields else "Text"
    return (
        '<div class="card">\n'
        '  <div class="question">{{cloze:' + first_field + "}}</div>\n"
        "</div>"
    )


def generate_cloze_back_template(fields: list[str]) -> str:
    """Generate a back HTML template for Cloze cards showing cloze field plus extras."""
    first_field = fields[0] if fields else "Text"
    lines = ['<div class="card">']
    lines.append('  <div class="question">{{cloze:' + first_field + "}}</div>")

    if len(fields) > 1:
        lines.append("  <hr>")
        for field in fields[1:]:
            lines.append("  {{#" + field + "}}")
            lines.append('  <div class="answer">{{' + field + "}}</div>")
            lines.append("  {{/" + field + "}}")

    lines.append("</div>")
    return "\n".join(lines)
