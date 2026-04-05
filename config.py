"""
AURA Configuration
Edit this file to set your API keys and preferences.

HOW TO GET FREE API KEYS:
--------------------------
WEATHER:
  1. Go to https://openweathermap.org/
  2. Click Sign Up (free)
  3. Go to My Profile -> API Keys tab
  4. Copy your key and paste below

NEWS:
  1. Go to https://newsapi.org/
  2. Click Get API Key (free)
  3. Copy your key and paste below
"""

import os

# ── Weather ───────────────────────────────────────────────────────────
WEATHER_API_KEY = "1ed89b17859e0cc2f61f39722cc2cac3"
DEFAULT_CITY    = "Mumbai"        # change to your city

# ── News ──────────────────────────────────────────────────────────────
NEWS_API_KEY = "d4726b634a3436c930b77b83dd9f5b3"
NEWS_COUNTRY = "in"              # in=India, us=USA, gb=UK, au=Australia

# ── Voice Settings ────────────────────────────────────────────────────
VOICE_RATE   = 165
VOICE_VOLUME = 1.0

# ── Wikipedia ─────────────────────────────────────────────────────────
WIKI_SENTENCES = 3

# ── History ───────────────────────────────────────────────────────────
MAX_HISTORY_ENTRIES = 500

# ── Music folder (for play music command) ─────────────────────────────
MUSIC_FOLDER = os.path.join(os.path.expanduser("~"), "Music")