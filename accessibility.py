"""
AURA Module: Accessibility System
"""

import os
from pathlib import Path

# Try multiple possible sign image locations
def _find_signs_dir():
    candidates = [
        Path(__file__).parent.parent / "assets" / "signs",
        Path(__file__).parent.parent / "signs",
        Path(__file__).parent.parent / "assets",
        Path.home() / "AURA" / "assets" / "signs",
        Path.cwd() / "assets" / "signs",
        Path.cwd() / "signs",
    ]
    for p in candidates:
        if p.exists():
            # Check if it actually has PNG files
            if list(p.glob("*.png")):
                return p
    # Return default even if it doesn't exist yet
    return Path(__file__).parent.parent / "assets" / "signs"

SIGNS_DIR = _find_signs_dir()

SIGN_MAP = {
    "hello":    "hello.png",
    "yes":      "yes.png",
    "no":       "no.png",
    "thank":    "thank_you.png",
    "sorry":    "sorry.png",
    "help":     "help.png",
    "stop":     "stop.png",
    "good":     "good.png",
    "bad":      "bad.png",
    "task":     "task.png",
    "done":     "done.png",
    "add":      "add.png",
    "complete": "done.png",
    "time":     "time.png",
    "date":     "date.png",
    "weather":  "weather.png",
    "news":     "news.png",
    "search":   "search.png",
    "open":     "open.png",
    "history":  "history.png",
    "morning":  "hello.png",
    "good day": "good.png",
    "opening":  "open.png",
    "playing":  "yes.png",
    "found":    "search.png",
    "today":    "date.png",
    "current":  "time.png",
}


class AccessibilityManager:
    def __init__(self):
        self.voice_enabled  = True
        self.text_enabled   = True
        self.sign_enabled   = True
        self.high_contrast  = False
        SIGNS_DIR.mkdir(parents=True, exist_ok=True)

    def toggle_voice(self) -> str:
        self.voice_enabled = not self.voice_enabled
        return f"Voice output {'ON' if self.voice_enabled else 'OFF'}."

    def toggle_text(self) -> str:
        self.text_enabled = not self.text_enabled
        return f"Text display {'ON' if self.text_enabled else 'OFF'}."

    def toggle_sign(self) -> str:
        self.sign_enabled = not self.sign_enabled
        return f"Sign language {'ON' if self.sign_enabled else 'OFF'}."

    def toggle_high_contrast(self) -> str:
        self.high_contrast = not self.high_contrast
        return f"High contrast {'ON' if self.high_contrast else 'OFF'}."

    def get_sign_image_path(self, text: str) -> str | None:
        """
        Find a sign image for the given text.
        Searches multiple folder locations automatically.
        """
        text_lower = text.lower()

        # Re-detect signs dir each call (in case user just added images)
        signs_dir = _find_signs_dir()

        for keyword, filename in SIGN_MAP.items():
            if keyword in text_lower:
                # Try detected dir first, then common locations
                for folder in [signs_dir, SIGNS_DIR,
                                Path(__file__).parent.parent / "assets" / "signs",
                                Path.cwd() / "assets" / "signs",
                                Path.cwd() / "signs"]:
                    path = folder / filename
                    if path.exists():
                        return str(path)
        return None

    def get_theme(self) -> dict:
        if self.high_contrast:
            return {
                "bg": "#000000", "fg": "#FFFF00",
                "panel_bg": "#111111", "user_fg": "#00FFFF",
                "aura_fg": "#FFFF00", "btn_bg": "#222222",
                "btn_fg": "#FFFFFF", "status_bg": "#003300",
                "status_fg": "#00FF00",
            }
        return {
            "bg": "#07071a", "fg": "#f3f0ff",
            "panel_bg": "#0d0d2b", "user_fg": "#22d3ee",
            "aura_fg": "#a78bfa", "btn_bg": "#11113a",
            "btn_fg": "#f3f0ff", "status_bg": "#4c1d95",
            "status_fg": "#d8b4fe",
        }

    def status_text(self) -> str:
        parts = []
        parts.append("🔊 Voice" if self.voice_enabled else "🔇 Voice OFF")
        parts.append("📝 Text"  if self.text_enabled  else "📝 Text OFF")
        parts.append("🤟 Sign"  if self.sign_enabled  else "🤟 Sign OFF")
        if self.high_contrast:
            parts.append("⚡ HC")
        return "  |  ".join(parts)