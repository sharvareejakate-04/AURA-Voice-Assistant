"""
AURA Module: Command Processor (Full Edition)
Handles all voice commands including phone app actions.
"""

import re


class CommandProcessor:
    PATTERNS = [
        # --- Greetings ---
        (r"\b(hello|hi|hey|good morning|good afternoon|good evening|what's up)\b", "greet"),

        # --- Time / Date ---
        (r"\bwhat (is |'s )?(the )?time\b",  "time"),
        (r"\bwhat time\b",                    "time"),
        (r"\bwhat (is |'s )?(the )?date\b",  "date"),
        (r"\bwhat day\b",                     "date"),

        # --- CLOSE APP ---
        (r"\b(close|exit|quit|kill|stop|terminate) (the )?(app |application )?(.+)", "close_app"),

        # --- MUSIC detailed actions ---
        (r"\bplay (.+) on spotify\b",                    "play_spotify"),
        (r"\bplay (.+) on youtube\b",                    "play_youtube"),
        (r"\bplay (.+) on youtube music\b",              "play_youtube_music"),
        (r"\bplay (.+) song\b",                          "play_song"),
        (r"\bplay (.+) music\b",                         "play_song"),
        (r"\bplay (.+)\b",                               "play_song"),
        (r"\b(stop|pause) (music|song|audio|playing)\b", "stop_music"),
        (r"\b(next song|next track|skip|next)\b",        "next_track"),
        (r"\b(previous|prev|back|last song)\b",          "prev_track"),

        # --- Volume ---
        (r"\b(volume up|increase volume|louder|turn up)\b",           "volume_up"),
        (r"\b(volume down|decrease volume|quieter|lower|turn down)\b","volume_down"),
        (r"\b(mute|silent|silence)\b",                                "mute"),

        # --- System ---
        (r"\b(take|capture) (a )?(screenshot|screen)\b", "screenshot"),
        (r"\block (screen|the screen|my screen)?\b",      "lock_screen"),
        (r"\b(shutdown|shut down|turn off|power off)\b",  "shutdown"),
        (r"\b(restart|reboot)\b",                         "restart"),
        (r"\b(list apps|show apps|which apps|what apps)\b","list_apps"),

        # --- APP SPECIFIC ACTIONS ---
        # YouTube actions
        (r"\bsearch (on |in )?youtube (for )?(.+)",       "yt_search"),
        (r"\bwatch (.+) on youtube",                       "yt_search"),
        (r"\byoutube (shorts|trending|subscriptions|history|watch later)\b", "yt_action"),

        # WhatsApp actions
        (r"\b(open|start|new) (whatsapp )?chat (with )?(.+)", "wa_chat"),
        (r"\bwhatsapp (.+)",                               "wa_action"),

        # Gmail actions
        (r"\b(compose|write|send|new) (email|mail|message) (to )?(.+)", "gmail_compose"),
        (r"\b(check|open|show) (my )?(inbox|email|mail|gmail)\b",        "gmail_inbox"),
        (r"\bgmail (compose|inbox|sent|drafts|starred)\b",               "gmail_action"),

        # Instagram actions
        (r"\binstagram (reels|explore|messages|stories|dm)\b",           "ig_action"),
        (r"\bopen (my )?instagram (reels|explore|messages|dm)\b",        "ig_action"),

        # Maps / Navigate actions
        (r"\b(navigate|directions|how to get) to (.+)",  "maps_navigate"),
        (r"\bfind (.+) near(by| me)\b",                  "maps_nearby"),
        (r"\bshow (.+) on (the )?map\b",                 "maps_search"),
        (r"\bmaps? (search |find |navigate to )?(.+)",   "maps_search"),

        # Calendar actions
        (r"\b(add|create|new|set) (a )?(event|reminder|appointment|meeting)( on | for )?(.+)?", "cal_new"),
        (r"\b(show|open|check) (my )?(calendar|schedule|events|today)\b", "cal_open"),

        # Clock / Alarm / Timer actions
        (r"\bset (a |an )?(alarm|reminder) (for |at )?(.+)",  "clock_alarm"),
        (r"\bset (a )?timer (for )?(.+)",                      "clock_timer"),
        (r"\b(start )?stopwatch\b",                            "clock_stopwatch"),

        # Notes actions
        (r"\b(add|create|new|write) (a )?(note|reminder)[\s:,]*(.*)", "notes_new"),
        (r"\b(show|open|check) (my )?notes?\b",               "notes_open"),

        # Photos actions
        (r"\b(open|show) (my )?(photos?|gallery|pictures?)\b","photos_open"),
        (r"\bsearch (my )?photos? (for )?(.+)",                "photos_search"),

        # Contacts actions
        (r"\b(call|phone|dial) (.+)",                          "phone_call"),
        (r"\b(add|new|create) contact (.+)",                   "contacts_add"),
        (r"\bsearch (contacts? for |for )?(.+) (in )?contacts?","contacts_search"),

        # Play Store actions
        (r"\b(search|find|download|install) (.+) (on |in |from )?(play store|playstore|google play)\b", "store_search"),
        (r"\bplay store (games|apps|top|new)\b",               "store_action"),

        # Settings actions
        (r"\bopen (wifi|bluetooth|mobile data|notifications|battery|display|sound|privacy|security) settings?\b", "settings_action"),
        (r"\bturn (on|off) (wifi|bluetooth|mobile data|hotspot|airplane mode)\b", "settings_toggle"),

        # Recorder
        (r"\b(start|begin|new) (voice |audio )?record(ing)?\b", "recorder_start"),
        (r"\bstop record(ing)?\b",                              "recorder_stop"),

        # Generic open
        (r"\bopen (.+)",       "open_app"),

        # --- Web Search ---
        (r"\b(google|search (for|the web for)?) (.+)",          "google_search"),
        (r"\bsearch youtube for (.+)",                          "yt_search"),
        (r"\b(wikipedia|wiki) (search |about |what is )?(.+)", "wikipedia_search"),

        # --- To-Do ---
        (r"\b(add task|add a task|create task|new task|remember)[\s:,]*(.*)", "add_task"),
        (r"\badd (.+?) (to |in )?(my )?(task|to.do|list)\b",                  "add_task_alt"),
        (r"\b(show tasks?|list tasks?|my tasks?|what are my tasks?)\b",        "show_tasks"),
        (r"\b(complete|finish|mark done|done) (task )?(.*)",                   "complete_task"),

        # --- History ---
        (r"\b(show history|my history|command history|what did i say)\b", "show_history"),
        (r"\bclear history\b",          "clear_history"),

        # --- Accessibility ---
        (r"\btoggle voice\b",                     "toggle_voice"),
        (r"\btoggle text\b",                      "toggle_text"),
        (r"\btoggle sign\b",                      "toggle_sign"),
        (r"\btoggle (high contrast|contrast)\b",  "toggle_high_contrast"),

        # --- Weather ---
        (r"\bweather (in |for |of )?(.+)",        "weather"),
        (r"\b(weather|how is the weather)\b",     "weather_default"),
        (r"\b(forecast) (in |for )?(.+)",         "forecast"),

        # --- News ---
        (r"\bnews (about|on) (.+)",               "news_topic"),
        (r"\b(news|headlines|top news)\b",        "news"),

        # --- Productivity ---
        (r"\b(productivity report|task report|how am i doing)\b", "productivity"),

        # --- Exit ---
        (r"\b(bye|goodbye|stop aura|exit aura|quit aura)\b", "exit"),
    ]

    def __init__(self):
        self._compiled = [
            (re.compile(p, re.IGNORECASE), a)
            for p, a in self.PATTERNS
        ]

    def parse(self, text: str) -> dict:
        text = text.strip()
        for regex, action in self._compiled:
            m = regex.search(text)
            if m:
                payload = self._payload(action, m, text)
                return {"action": action, "payload": payload,
                        "raw": text, "match": m}
        return {"action": "unknown", "payload": text, "raw": text, "match": None}

    def _payload(self, action, m, full) -> str:
        try:
            g = m.groups()

            if action == "close_app":          return (g[3] or "").strip()
            if action == "play_spotify":       return (g[0] or "").strip()
            if action == "play_youtube":       return (g[0] or "").strip()
            if action == "play_youtube_music": return (g[0] or "").strip()
            if action == "play_song":          return (g[0] or "").strip()
            if action == "yt_search":
                return (g[-1] or g[0] or "").strip()
            if action == "yt_action":          return (g[0] or "").strip()
            if action == "wa_chat":            return (g[3] or "").strip()
            if action == "wa_action":          return (g[0] or "").strip()
            if action == "gmail_compose":      return (g[3] or "").strip()
            if action == "gmail_action":       return (g[0] or "").strip()
            if action == "ig_action":          return (g[0] or g[1] or "").strip()
            if action == "maps_navigate":      return (g[1] or "").strip()
            if action == "maps_nearby":        return (g[0] or "").strip()
            if action == "maps_search":        return (g[1] or g[0] or "").strip()
            if action == "cal_new":            return (g[4] or "").strip()
            if action == "clock_alarm":        return (g[3] or "").strip()
            if action == "clock_timer":        return (g[2] or "").strip()
            if action == "notes_new":          return (g[3] or "").strip()
            if action == "photos_search":      return (g[2] or "").strip()
            if action == "phone_call":         return (g[1] or "").strip()
            if action == "contacts_add":       return (g[0] or "").strip()
            if action == "contacts_search":    return (g[1] or "").strip()
            if action == "store_search":       return (g[1] or "").strip()
            if action == "store_action":       return (g[0] or "").strip()
            if action == "settings_action":    return (g[0] or "").strip()
            if action == "settings_toggle":    return f"{g[0]} {g[1]}".strip()
            if action == "open_app":           return (g[0] or "").strip()
            if action == "google_search":      return (g[2] or "").strip()
            if action == "wikipedia_search":   return (g[2] or "").strip()
            if action == "add_task":
                task = (g[1] or "").strip()
                if not task:
                    parts = full.lower().split("add task", 1)
                    task = parts[1].strip() if len(parts) > 1 else ""
                return task
            if action == "add_task_alt":       return (g[0] or "").strip()
            if action == "complete_task":      return (g[2] or "").strip()
            if action == "weather":            return (g[1] or "").strip()
            if action == "forecast":           return (g[2] or "").strip()
            if action == "news_topic":         return (g[1] or "").strip()
        except (IndexError, AttributeError):
            pass
        return ""