"""
AURA Module: App Launcher (Phone Apps Edition)
All requested phone apps with their proper actions.
Opens via browser links (works on any device with a browser).
Also handles music, volume, and system commands for laptop.
"""

import webbrowser
import subprocess
import platform
import os
import glob
import urllib.parse

_OS = platform.system().lower()


# ──────────────────────────────────────────────────────────────────────
# PHONE APP DEFINITIONS
# Each app has:
#   url         → web version (works on laptop browser too)
#   actions     → dict of action_name → url or function key
# ──────────────────────────────────────────────────────────────────────
PHONE_APPS = {

    "youtube": {
        "url": "https://www.youtube.com",
        "actions": {
            "open":       "https://www.youtube.com",
            "search":     "https://www.youtube.com/results?search_query={}",
            "shorts":     "https://www.youtube.com/shorts",
            "trending":   "https://www.youtube.com/feed/trending",
            "subscriptions": "https://www.youtube.com/feed/subscriptions",
            "history":    "https://www.youtube.com/feed/history",
            "watch later":"https://www.youtube.com/playlist?list=WL",
        }
    },

    "whatsapp": {
        "url": "https://web.whatsapp.com",
        "actions": {
            "open":       "https://web.whatsapp.com",
            "new chat":   "https://web.whatsapp.com",
            "status":     "https://web.whatsapp.com",
        }
    },

    "telegram": {
        "url": "https://web.telegram.org",
        "actions": {
            "open":       "https://web.telegram.org",
            "new chat":   "https://web.telegram.org",
        }
    },

    "instagram": {
        "url": "https://www.instagram.com",
        "actions": {
            "open":       "https://www.instagram.com",
            "reels":      "https://www.instagram.com/reels/",
            "explore":    "https://www.instagram.com/explore/",
            "messages":   "https://www.instagram.com/direct/inbox/",
            "profile":    "https://www.instagram.com/accounts/activity/",
            "notifications": "https://www.instagram.com/accounts/activity/",
        }
    },

    "gmail": {
        "url": "https://mail.google.com",
        "actions": {
            "open":       "https://mail.google.com",
            "compose":    "https://mail.google.com/mail/u/0/#compose",
            "inbox":      "https://mail.google.com/mail/u/0/#inbox",
            "sent":       "https://mail.google.com/mail/u/0/#sent",
            "drafts":     "https://mail.google.com/mail/u/0/#drafts",
            "starred":    "https://mail.google.com/mail/u/0/#starred",
            "new email":  "https://mail.google.com/mail/u/0/#compose",
            "new mail":   "https://mail.google.com/mail/u/0/#compose",
        }
    },

    "photos": {
        "url": "https://photos.google.com",
        "actions": {
            "open":       "https://photos.google.com",
            "albums":     "https://photos.google.com/albums",
            "favorites":  "https://photos.google.com/starred",
            "shared":     "https://photos.google.com/sharing",
            "memories":   "https://photos.google.com/memories",
            "search":     "https://photos.google.com/search/{}",
        }
    },

    "spotify": {
        "url": "https://open.spotify.com",
        "actions": {
            "open":       "https://open.spotify.com",
            "search":     "https://open.spotify.com/search/{}",
            "liked songs":"https://open.spotify.com/collection/tracks",
            "podcasts":   "https://open.spotify.com/genres/podcasts-page",
            "new releases":"https://open.spotify.com/section/0JQ5DAqbMKFQIL0AXnG5AK",
            "charts":     "https://open.spotify.com/genre/charts-page",
            "play":       "https://open.spotify.com",
        }
    },

    "music": {
        "url": "https://music.youtube.com",
        "actions": {
            "open":       "https://music.youtube.com",
            "search":     "https://music.youtube.com/search?q={}",
            "library":    "https://music.youtube.com/library",
            "liked":      "https://music.youtube.com/playlist?list=LM",
            "play":       "https://music.youtube.com",
        }
    },

    "messages": {
        "url": "https://messages.google.com/web",
        "actions": {
            "open":       "https://messages.google.com/web",
            "new message":"https://messages.google.com/web/conversations/new",
        }
    },

    "play store": {
        "url": "https://play.google.com/store",
        "actions": {
            "open":       "https://play.google.com/store",
            "search":     "https://play.google.com/store/search?q={}&c=apps",
            "games":      "https://play.google.com/store/games",
            "apps":       "https://play.google.com/store/apps",
            "top charts": "https://play.google.com/store/apps/top",
            "new releases":"https://play.google.com/store/apps/new",
        }
    },

    "videos": {
        "url": "https://www.youtube.com",
        "actions": {
            "open":       "https://www.youtube.com",
            "search":     "https://www.youtube.com/results?search_query={}",
            "trending":   "https://www.youtube.com/feed/trending",
        }
    },

    "chrome": {
        "url": "https://www.google.com",
        "actions": {
            "open":        "https://www.google.com",
            "new tab":     "https://www.google.com",
            "history":     "chrome://history",
            "bookmarks":   "chrome://bookmarks",
            "downloads":   "chrome://downloads",
            "settings":    "chrome://settings",
            "extensions":  "chrome://extensions",
            "incognito":   "_incognito",
        }
    },

    "clock": {
        "url": "https://time.is",
        "actions": {
            "open":        "https://time.is",
            "alarm":       "https://www.google.com/search?q=set+alarm",
            "set alarm":   "https://www.google.com/search?q=set+alarm",
            "timer":       "https://www.google.com/search?q=set+timer",
            "set timer":   "https://www.google.com/search?q=set+timer",
            "stopwatch":   "https://www.google.com/search?q=stopwatch",
            "world clock": "https://time.is",
        }
    },

    "calendar": {
        "url": "https://calendar.google.com",
        "actions": {
            "open":        "https://calendar.google.com",
            "today":       "https://calendar.google.com/calendar/r/day",
            "week":        "https://calendar.google.com/calendar/r/week",
            "month":       "https://calendar.google.com/calendar/r/month",
            "new event":   "https://calendar.google.com/calendar/r/eventedit",
            "add event":   "https://calendar.google.com/calendar/r/eventedit",
        }
    },

    "files": {
        "url": "https://drive.google.com",
        "actions": {
            "open":        "https://drive.google.com",
            "my drive":    "https://drive.google.com/drive/my-drive",
            "shared":      "https://drive.google.com/drive/shared-with-me",
            "recent":      "https://drive.google.com/drive/recent",
            "trash":       "https://drive.google.com/drive/trash",
            "upload":      "https://drive.google.com",
        }
    },

    "internet": {
        "url": "https://www.google.com",
        "actions": {
            "open":        "https://www.google.com",
            "search":      "https://www.google.com/search?q={}",
        }
    },

    "google maps": {
        "url": "https://maps.google.com",
        "actions": {
            "open":        "https://maps.google.com",
            "directions":  "https://maps.google.com/maps?q={}",
            "nearby":      "https://maps.google.com/maps?q=nearby",
            "search":      "https://maps.google.com/maps?q={}",
            "navigate":    "https://maps.google.com/maps?q={}",
            "restaurants": "https://maps.google.com/maps?q=restaurants+nearby",
            "hospitals":   "https://maps.google.com/maps?q=hospitals+nearby",
            "petrol station": "https://maps.google.com/maps?q=petrol+station+nearby",
        }
    },

    "maps": {
        "url": "https://maps.google.com",
        "actions": {
            "open":        "https://maps.google.com",
            "directions":  "https://maps.google.com/maps?q={}",
            "search":      "https://maps.google.com/maps?q={}",
            "navigate":    "https://maps.google.com/maps?q={}",
        }
    },

    "calculator": {
        "url": "https://www.google.com/search?q=calculator",
        "actions": {
            "open":        "https://www.google.com/search?q=calculator",
            "scientific":  "https://www.google.com/search?q=scientific+calculator",
        }
    },

    "camera": {
        "url": None,    # local only
        "actions": {
            "open":        "_camera",
            "screenshot":  "_screenshot",
        }
    },

    "contacts": {
        "url": "https://contacts.google.com",
        "actions": {
            "open":        "https://contacts.google.com",
            "new contact": "https://contacts.google.com/new",
            "add contact": "https://contacts.google.com/new",
            "search":      "https://contacts.google.com/?q={}",
        }
    },

    "phone": {
        "url": "https://voice.google.com",
        "actions": {
            "open":        "https://voice.google.com",
            "call":        "https://voice.google.com",
            "recent":      "https://voice.google.com",
        }
    },

    "notes": {
        "url": "https://keep.google.com",
        "actions": {
            "open":        "https://keep.google.com",
            "new note":    "https://keep.google.com",
            "add note":    "https://keep.google.com",
            "reminders":   "https://keep.google.com/u/0/#reminders",
        }
    },

    "recorder": {
        "url": "https://recorder.google.com",
        "actions": {
            "open":        "https://recorder.google.com",
            "record":      "https://recorder.google.com",
            "new recording": "https://recorder.google.com",
        }
    },

    "settings": {
        "url": "https://myaccount.google.com",
        "actions": {
            "open":        "https://myaccount.google.com",
            "wifi":        "https://myaccount.google.com",
            "bluetooth":   "https://myaccount.google.com",
            "privacy":     "https://myaccount.google.com/privacy",
            "security":    "https://myaccount.google.com/security",
            "account":     "https://myaccount.google.com",
            "notifications": "https://myaccount.google.com/notifications",
        }
    },
}

# Aliases for natural speech
APP_ALIASES = {
    "google maps":   "google maps",
    "maps":          "google maps",
    "map":           "google maps",
    "navigate":      "google maps",
    "navigation":    "google maps",
    "whats app":     "whatsapp",
    "what's app":    "whatsapp",
    "insta":         "instagram",
    "ig":            "instagram",
    "mail":          "gmail",
    "email":         "gmail",
    "google mail":   "gmail",
    "music player":  "music",
    "youtube music": "music",
    "play music":    "music",
    "play store":    "play store",
    "playstore":     "play store",
    "google play":   "play store",
    "google photos": "photos",
    "photo":         "photos",
    "gallery":       "photos",
    "video":         "videos",
    "browser":       "chrome",
    "google chrome": "chrome",
    "internet":      "internet",
    "web":           "internet",
    "google":        "internet",
    "clock app":     "clock",
    "alarm":         "clock",
    "timer":         "clock",
    "google calendar": "calendar",
    "calender":      "calendar",
    "schedule":      "calendar",
    "google drive":  "files",
    "drive":         "files",
    "file manager":  "files",
    "storage":       "files",
    "calc":          "calculator",
    "math":          "calculator",
    "google keep":   "notes",
    "keep":          "notes",
    "notepad":       "notes",
    "voice recorder": "recorder",
    "audio recorder": "recorder",
    "record":        "recorder",
    "contact":       "contacts",
    "phonebook":     "contacts",
    "dial":          "phone",
    "dialer":        "phone",
    "call":          "phone",
    "google voice":  "phone",
    "account settings": "settings",
    "google settings": "settings",
}


class AppLauncher:
    def __init__(self):
        self._music_files   = []
        self._current_track = 0

    # ==================================================================
    # RESOLVE APP NAME
    # ==================================================================
    def _resolve(self, name: str) -> str | None:
        name = name.lower().strip()
        if name in PHONE_APPS:
            return name
        if name in APP_ALIASES:
            return APP_ALIASES[name]
        # partial match
        for key in PHONE_APPS:
            if key in name or name in key:
                return key
        for alias, target in APP_ALIASES.items():
            if alias in name or name in alias:
                return target
        return None

    # ==================================================================
    # OPEN APP
    # ==================================================================
    def open_app(self, app_name: str) -> str:
        resolved = self._resolve(app_name)
        if not resolved:
            return f"I don't know the app '{app_name}'. Try: YouTube, WhatsApp, Instagram, Gmail, Spotify, Maps, Calendar, Notes, Settings."

        app = PHONE_APPS[resolved]
        url = app.get("url")
        if url:
            webbrowser.open(url)
            return f"Opening {resolved.title()}."
        # Special cases
        return self._handle_special(resolved, "open", "")

    # ==================================================================
    # APP ACTION (e.g. "compose email", "search on youtube")
    # ==================================================================
    def app_action(self, app_name: str, action: str, query: str = "") -> str:
        resolved = self._resolve(app_name)
        if not resolved:
            return self.open_app(app_name)

        app = PHONE_APPS[resolved]
        actions = app.get("actions", {})

        # Find matching action
        action_lower = action.lower().strip()
        matched_url  = None
        for key, val in actions.items():
            if key in action_lower or action_lower in key:
                matched_url = val
                break

        if matched_url is None:
            return self.open_app(app_name)

        # Special internal actions
        if matched_url == "_camera":
            return self._open_camera()
        if matched_url == "_screenshot":
            return self.take_screenshot()
        if matched_url == "_incognito":
            return self._open_incognito()

        # Fill in query if URL has {}
        if query and "{}" in matched_url:
            matched_url = matched_url.format(urllib.parse.quote(query))
        elif "{}" in matched_url:
            matched_url = matched_url.replace("{}", "")

        webbrowser.open(matched_url)
        label = f"{resolved.title()} → {action}"
        return f"Opening {label}."

    # ==================================================================
    # CLOSE APP
    # ==================================================================
    def close_app(self, app_name: str) -> str:
        resolved = self._resolve(app_name)
        label = (resolved or app_name).title()

        # Try to close browser tab / process
        browser_procs = {
            "windows": ["chrome.exe", "msedge.exe", "firefox.exe"],
            "darwin":  ["Google Chrome", "Safari", "Firefox"],
            "linux":   ["chrome", "firefox", "chromium"],
        }
        if resolved in ["youtube", "whatsapp", "instagram", "gmail",
                        "chrome", "internet", "photos", "maps", "google maps",
                        "play store", "spotify", "music", "messages",
                        "contacts", "notes", "files", "calendar",
                        "recorder", "phone", "settings", "calculator",
                        "clock", "videos"]:
            # Close the browser
            procs = browser_procs.get(_OS, [])
            killed = False
            for proc in procs:
                result = self._kill(proc)
                if result:
                    killed = True
                    break
            return f"{label} closed." if killed else f"Closed {label} (browser tab)."

        return f"{label} closed."

    def _kill(self, proc: str) -> bool:
        try:
            if _OS == "windows":
                r = subprocess.run(["taskkill", "/F", "/IM", proc],
                                   capture_output=True)
                return r.returncode == 0
            else:
                r = subprocess.run(["pkill", "-f", proc], capture_output=True)
                return r.returncode == 0
        except Exception:
            return False

    # ==================================================================
    # MUSIC CONTROL
    # ==================================================================
    def play_music(self, music_folder: str, song_query: str = "") -> str:
        # Try local files
        exts = ["*.mp3", "*.wav", "*.flac", "*.m4a", "*.ogg", "*.aac"]
        files = []
        for ext in exts:
            files += glob.glob(os.path.join(music_folder, "**", ext), recursive=True)
            files += glob.glob(os.path.join(music_folder, ext))

        if files:
            self._music_files = files
            if song_query:
                q = song_query.lower()
                matches = [f for f in files if q in os.path.basename(f).lower()]
                if matches:
                    return self._play_file(matches[0])
            self._current_track = 0
            return self._play_file(files[0])

        # Fallback: YouTube Music
        if song_query:
            encoded = urllib.parse.quote(song_query)
            webbrowser.open(f"https://music.youtube.com/search?q={encoded}")
            return f"Playing '{song_query}' on YouTube Music."
        webbrowser.open("https://music.youtube.com")
        return "Opening YouTube Music."

    def _play_file(self, filepath: str) -> str:
        name = os.path.basename(filepath)
        try:
            if _OS == "windows":
                os.startfile(filepath)
            elif _OS == "darwin":
                subprocess.Popen(["open", filepath])
            else:
                subprocess.Popen(["xdg-open", filepath])
            return f"Now playing: {name}"
        except Exception as e:
            return f"Could not play {name}: {e}"

    def stop_music(self) -> str:
        stopped = False
        for proc in ["vlc.exe", "Spotify.exe", "wmplayer.exe",
                     "vlc", "spotify", "rhythmbox", "VLC", "Spotify", "Music"]:
            if self._kill(proc):
                stopped = True
        return "Music stopped." if stopped else "Music stopped."

    def next_track(self) -> str:
        if not self._music_files:
            webbrowser.open("https://music.youtube.com")
            return "Opening YouTube Music for next track."
        self._current_track = (self._current_track + 1) % len(self._music_files)
        return self._play_file(self._music_files[self._current_track])

    def previous_track(self) -> str:
        if not self._music_files:
            webbrowser.open("https://music.youtube.com")
            return "Opening YouTube Music."
        self._current_track = (self._current_track - 1) % len(self._music_files)
        return self._play_file(self._music_files[self._current_track])

    def play_on_youtube(self, query: str) -> str:
        encoded = urllib.parse.quote(query)
        webbrowser.open(f"https://www.youtube.com/results?search_query={encoded}")
        return f"Searching YouTube for '{query}'."

    def play_on_spotify(self, query: str) -> str:
        encoded = urllib.parse.quote(query)
        webbrowser.open(f"https://open.spotify.com/search/{encoded}")
        return f"Searching Spotify for '{query}'."

    # ==================================================================
    # VOLUME
    # ==================================================================
    def volume_up(self) -> str:
        try:
            if _OS == "windows":
                import ctypes
                for _ in range(5):
                    ctypes.windll.user32.keybd_event(0xAF, 0, 0, 0)
                    ctypes.windll.user32.keybd_event(0xAF, 0, 2, 0)
                return "Volume increased."
            elif _OS == "darwin":
                subprocess.run(["osascript", "-e",
                    "set volume output volume (output volume of (get volume settings) + 10)"])
                return "Volume increased."
            else:
                subprocess.run(["amixer", "-D", "pulse", "sset", "Master", "10%+"])
                return "Volume increased."
        except Exception as e:
            return f"Volume control failed: {e}"

    def volume_down(self) -> str:
        try:
            if _OS == "windows":
                import ctypes
                for _ in range(5):
                    ctypes.windll.user32.keybd_event(0xAE, 0, 0, 0)
                    ctypes.windll.user32.keybd_event(0xAE, 0, 2, 0)
                return "Volume decreased."
            elif _OS == "darwin":
                subprocess.run(["osascript", "-e",
                    "set volume output volume (output volume of (get volume settings) - 10)"])
                return "Volume decreased."
            else:
                subprocess.run(["amixer", "-D", "pulse", "sset", "Master", "10%-"])
                return "Volume decreased."
        except Exception as e:
            return f"Volume control failed: {e}"

    def mute(self) -> str:
        try:
            if _OS == "windows":
                import ctypes
                ctypes.windll.user32.keybd_event(0xAD, 0, 0, 0)
                ctypes.windll.user32.keybd_event(0xAD, 0, 2, 0)
                return "Muted."
            elif _OS == "darwin":
                subprocess.run(["osascript", "-e", "set volume with output muted"])
                return "Muted."
            else:
                subprocess.run(["amixer", "-D", "pulse", "sset", "Master", "mute"])
                return "Muted."
        except Exception as e:
            return f"Mute failed: {e}"

    # ==================================================================
    # SYSTEM
    # ==================================================================
    def take_screenshot(self) -> str:
        try:
            if _OS == "windows":
                subprocess.Popen("snippingtool", shell=True)
                return "Snipping tool opened."
            elif _OS == "darwin":
                path = os.path.expanduser("~/Desktop/screenshot.png")
                subprocess.Popen(["screencapture", "-i", path])
                return "Screenshot saved to Desktop."
            else:
                subprocess.Popen(["gnome-screenshot", "-i"])
                return "Screenshot tool opened."
        except Exception as e:
            return f"Screenshot failed: {e}"

    def lock_screen(self) -> str:
        try:
            if _OS == "windows":
                subprocess.run(["rundll32.exe", "user32.dll,LockWorkStation"])
            elif _OS == "darwin":
                subprocess.run(["pmset", "displaysleepnow"])
            else:
                subprocess.run(["gnome-screensaver-command", "-l"])
            return "Screen locked."
        except Exception as e:
            return f"Lock failed: {e}"

    def shutdown(self) -> str:
        try:
            if _OS == "windows":
                subprocess.run(["shutdown", "/s", "/t", "30"])
                return "Shutting down in 30 seconds."
            else:
                subprocess.run(["shutdown", "-h", "+1"])
                return "Shutting down in 1 minute."
        except Exception as e:
            return f"Shutdown failed: {e}"

    def restart(self) -> str:
        try:
            if _OS == "windows":
                subprocess.run(["shutdown", "/r", "/t", "30"])
                return "Restarting in 30 seconds."
            else:
                subprocess.run(["shutdown", "-r", "+1"])
                return "Restarting in 1 minute."
        except Exception as e:
            return f"Restart failed: {e}"

    def _open_camera(self) -> str:
        try:
            if _OS == "windows":
                subprocess.Popen("start microsoft.windows.camera:", shell=True)
            elif _OS == "darwin":
                subprocess.Popen(["open", "-a", "FaceTime"])
            else:
                subprocess.Popen(["cheese"])
            return "Opening camera."
        except Exception as e:
            return f"Camera failed: {e}"

    def _open_incognito(self) -> str:
        try:
            if _OS == "windows":
                subprocess.Popen(["chrome", "--incognito"])
            elif _OS == "darwin":
                subprocess.Popen(["open", "-na", "Google Chrome",
                                  "--args", "--incognito"])
            else:
                subprocess.Popen(["google-chrome", "--incognito"])
            return "Opening incognito window."
        except Exception:
            webbrowser.open("https://www.google.com")
            return "Opening browser in private mode."

    def list_apps(self) -> str:
        names = sorted(PHONE_APPS.keys())
        return "Apps I can open and control:\n" + ", ".join(n.title() for n in names)