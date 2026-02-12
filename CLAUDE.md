# Claude Code Configuration — Anki MCP Server

## Project Overview

This is an **Anki MCP Server** — a conversational intelligent assistant that enables users to create, manage, and enrich Anki decks through natural language, without needing to interact directly with the Anki interface.

**Current Status:** In Design (PRD Complete) on branch `full-control-anki`
**Main Branch:** `main` (for PRs)

---

## Key Design Decisions

### Core Philosophy: Maximum Control

The system is built around **maximum user control** in custom deck creation:

1. **4 Predefined Templates** for common use cases:
   - Default (Anki standard)
   - Duolingo-style (gamified, green)
   - Dark Mode (nocturnal studying)
   - Code Style (programming)

2. **Custom Complete Mode** — Users define:
   - Number and names of fields (Front, Back, Image, Sound, Example, Tips, or any custom combination)
   - Complete CSS (colors, animations, layout, @keyframes, variables)
   - HTML templates with dynamic field references (`{{Field}}`)
   - Card types (Basic, Cloze, or both)
   - Media (images, audio, conditional rendering)

3. **Natural Language to CSS/HTML** — The MCP interprets user descriptions ("dark profundo, green menta, fade animations") and generates exact CSS automatically.

### No Template Names for Custom Styles

❌ **Avoid:** Creating named templates like "Tranquil Dark" — these are custom CSS examples, not fixed entities.
✅ **Instead:** Let users describe styles in natural language and generate CSS dynamically.

---

## PRD Structure

**Location:** `/PRD.md`

Main sections:
- **Section 2:** Use Cases (including Caso 4: Máximo Control)
- **Section 3:** User Flows
- **Section 4:** Functional Requirements
  - 4.1: Deck Management
  - 4.2: Card Types
  - 4.3: Style Templates (4 predefined + Custom)
  - 4.4: Conversational Intelligence
  - 4.5: CRUD Operations
  - **4.6: Customization Capabilities** (new section detailing what users can customize)
- **Section 5:** Technical Architecture
  - 5.1: MCP Tools (including `update_note_type_style`, `update_note_type_template`)
  - 5.2: Predefined CSS Templates + Custom Template explanation
  - 5.3: Configuration (4 builtin templates, no "tranquil")
- **Section 6:** Implementation Phases
  - Phase 1: CRUD Foundation
  - Phase 2: Templates & Styles (including Custom system)
  - Phase 3: Media & Rich Content
  - Phase 4: Conversational Intelligence

---

## Project Structure

```
anki-mcp-server/
├── CLAUDE.md                 # This file
├── PRD.md                    # Product Requirements Document
├── anki_server.py            # Main MCP server implementation
├── Dockerfile                # Container configuration
├── venv/                     # Python virtual environment
└── .agents/                  # Agent configuration
```

---

## Important Constraints

### Technical Limitations

1. **AnkiConnect dependency:** Requires AnkiConnect plugin running on `localhost:8765`
2. **No JavaScript in templates:** Security restriction — CSS only
3. **CSS validation required:** Must sanitize and validate custom CSS before applying
4. **No auto-generation of content:** MCP creates structure/style, not content (content comes from user or external LLMs)

### Development Guidelines

- **Read the PRD first** when implementing any feature
- **Section 5.1** lists all tools with parameters and return types
- **Section 5.2** explains template system and custom CSS capabilities
- **Phase 2** is the critical phase for templates/custom system implementation
- All custom CSS must be validated to reject `javascript:` URLs and `<script>` tags

---

## Current Branch

**Branch:** `full-control-anki`
**Latest Commit:** Full PRD refactoring — removed "Tranquil Dark" template, emphasized custom control

**Uncommitted Changes:**
- Modified: `anki_server.py` (if any)
- New: `.DS_Store`, `.agents/`, `.claude/`, `PRD.md`, `venv/`

---

## Next Steps

1. **Review PRD** — Ensure it clearly communicates the 4 predefined + Custom model
2. **Phase 1 Implementation** — Build CRUD operations foundation
3. **Phase 2 Implementation** — Build template system with natural language CSS generation
4. **Testing** — Create visual tests showing templates rendering correctly in Anki

---

## References

- **AnkiConnect API:** https://github.com/FooSoft/anki-connect
- **Anki Template Docs:** https://docs.ankiweb.net/templates/index.html
- **Anki CSS Guide:** https://docs.ankiweb.net/styling.html

---

**Last Updated:** February 2025
**Maintained by:** Claude Code
