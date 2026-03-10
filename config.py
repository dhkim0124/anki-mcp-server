"""
Server configuration and constants for Anki MCP Server.
"""

# AnkiConnect API settings
ANKI_CONNECT_URL = "http://localhost:8765"
ANKI_CONNECT_VERSION = 6

# Media upload limits
MEDIA_MAX_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB
ALLOWED_MEDIA_TYPES = {
    "image/jpeg": [".jpg", ".jpeg"],
    "image/png": [".png"],
    "audio/mpeg": [".mp3"],
    "audio/wav": [".wav"],
    "audio/ogg": [".ogg"],
}
