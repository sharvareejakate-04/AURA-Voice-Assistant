"""
AURA GUI - Purple Night Theme
Mobile-style phone UI with glowing orb, animated wave bars, wake word auto-start.
"""

import tkinter as tk
from tkinter import scrolledtext, messagebox
import threading
import re
import math
import time
import webbrowser
from pathlib import Path

try:
    from PIL import Image, ImageTk
    PIL_OK = True
except ImportError:
    PIL_OK = False

from voice_core        import VoiceCore
from web_features      import WebFeatures
from todo_manager      import TodoManager
from history_manager   import HistoryManager
from accessibility     import AccessibilityManager
from command_processor import CommandProcessor
from app_launcher      import AppLauncher
import config

# ── Purple Night Palette ──────────────────────────────────────────────
BG_VOID    = "#07071a"
BG_DEEP    = "#0d0d2b"
BG_PANEL   = "#11113a"
BG_CARD    = "#16164a"
PURPLE     = "#8b5cf6"
PURPLE_LT  = "#a78bfa"
PURPLE_DIM = "#4c1d95"
CYAN       = "#22d3ee"
GREEN      = "#10b981"
PINK       = "#ec4899"
AMBER      = "#f59e0b"
WHITE      = "#f3f0ff"
MUTED      = "#6d6d9a"
BORDER     = "#2a2a6a"


class AuraGUI:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("AURA — Accessible Universal Response Assistant")
        self.root.geometry("480x820")
        self.root.resizable(False, False)
        self.root.configure(bg=BG_VOID)

        # Modules
        self.voice     = VoiceCore(
            on_wake    = self._on_wake,
            on_command = self._on_voice_command,
            on_status  = self._set_status,
        )
        self.web       = WebFeatures()
        self.todo      = TodoManager()
        self.history   = HistoryManager()
        self.access    = AccessibilityManager()
        self.processor = CommandProcessor()
        self.launcher  = AppLauncher()

        self._sign_image_ref = None
        self._wave_running   = False
        self._orb_phase      = 0.0
        self._status_var     = tk.StringVar(value="Starting AURA...")

        self._build_ui()
        self._start_orb_animation()
        self._start_wave_animation()

        # Auto-start wake word — NO click needed
        self.voice.start_wake_word_loop()

        self._append_msg("AURA",
            "Good day! I'm AURA.\n"
            "Say  'Hey AURA'  anytime — I'm always listening.", system=True)
        self._set_status("👂  Listening for  'Hey AURA'...")

    # ==================================================================
    # BUILD UI
    # ==================================================================
    def _build_ui(self):
        # ── Header bar ────────────────────────────────────────────────
        hdr = tk.Frame(self.root, bg=BG_DEEP, height=50)
        hdr.pack(fill=tk.X)
        hdr.pack_propagate(False)

        tk.Label(hdr, text="🤖  AURA", bg=BG_DEEP,
                 fg=PURPLE_LT, font=("Courier", 16, "bold")).pack(side=tk.LEFT, padx=14)

        # Accessibility pills (top right)
        pill_frame = tk.Frame(hdr, bg=BG_DEEP)
        pill_frame.pack(side=tk.RIGHT, padx=8)
        for txt, cmd in [("🔊", self._toggle_voice),
                         ("📝", self._toggle_text),
                         ("🤟", self._toggle_sign),
                         ("⚡", self._toggle_contrast)]:
            tk.Button(pill_frame, text=txt, bg=BG_PANEL, fg=PURPLE_LT,
                      activebackground=PURPLE_DIM, activeforeground=WHITE,
                      relief="flat", bd=0, font=("Arial", 13),
                      command=cmd, cursor="hand2", padx=4
                      ).pack(side=tk.LEFT, padx=2)

        # ── Status strip ──────────────────────────────────────────────
        self.status_bar = tk.Label(
            self.root, textvariable=self._status_var,
            bg=PURPLE_DIM, fg="#d8b4fe",
            font=("Courier", 9), anchor="center", pady=3
        )
        self.status_bar.pack(fill=tk.X)

        # ── Orb section ───────────────────────────────────────────────
        orb_frame = tk.Frame(self.root, bg=BG_VOID, height=200)
        orb_frame.pack(fill=tk.X)
        orb_frame.pack_propagate(False)

        self.orb_canvas = tk.Canvas(orb_frame, width=480, height=200,
                                    bg=BG_VOID, highlightthickness=0)
        self.orb_canvas.pack()

        # Draw orb rings
        cx, cy = 240, 100
        for r, alpha_tag in [(90, "ring3"), (72, "ring2"), (54, "ring1")]:
            self.orb_canvas.create_oval(
                cx - r, cy - r, cx + r, cy + r,
                outline=PURPLE_DIM, width=1, tags=alpha_tag
            )
        # Main orb
        self.orb_canvas.create_oval(
            cx - 42, cy - 42, cx + 42, cy + 42,
            fill=PURPLE_DIM, outline=PURPLE, width=2, tags="orb_body"
        )
        self.orb_canvas.create_text(
            cx, cy, text="🤖", font=("Arial", 28), tags="orb_icon"
        )
        # Name + subtitle below orb
        self.orb_canvas.create_text(
            cx, cy + 58, text="AURA",
            fill=PURPLE_LT, font=("Courier", 15, "bold"), tags="orb_name"
        )
        self.orb_lbl = self.orb_canvas.create_text(
            cx, cy + 76, text="WAKE WORD ACTIVE",
            fill=MUTED, font=("Courier", 8), tags="orb_sub"
        )

        # ── Wave bars ─────────────────────────────────────────────────
        wave_frame = tk.Frame(self.root, bg=BG_VOID, height=44)
        wave_frame.pack(fill=tk.X)
        wave_frame.pack_propagate(False)

        self.wave_canvas = tk.Canvas(wave_frame, width=480, height=44,
                                     bg=BG_VOID, highlightthickness=0)
        self.wave_canvas.pack()
        self._wave_bars = []
        n = 28
        spacing = 480 / (n + 1)
        for i in range(n):
            x = spacing * (i + 1)
            bar = self.wave_canvas.create_rectangle(
                x - 2, 22, x + 2, 22,
                fill=PURPLE, outline="", tags="bar"
            )
            self._wave_bars.append((bar, x, i))

        # ── Conversation panel ────────────────────────────────────────
        conv_hdr = tk.Frame(self.root, bg=BG_PANEL, height=28)
        conv_hdr.pack(fill=tk.X)
        conv_hdr.pack_propagate(False)
        tk.Label(conv_hdr, text="💬  Conversation", bg=BG_PANEL,
                 fg=PURPLE_LT, font=("Courier", 9, "bold"), anchor="w"
                 ).pack(side=tk.LEFT, padx=12, pady=4)

        self.conv_text = scrolledtext.ScrolledText(
            self.root, bg=BG_DEEP, fg=WHITE,
            font=("Courier", 10), height=9,
            bd=0, relief="flat", wrap=tk.WORD,
            insertbackground=PURPLE,
            state=tk.DISABLED,
        )
        self.conv_text.pack(fill=tk.X, padx=0)
        self.conv_text.tag_config("aura_name", foreground=PURPLE_LT, font=("Courier", 10, "bold"))
        self.conv_text.tag_config("aura_text", foreground="#d8b4fe")
        self.conv_text.tag_config("user_name", foreground=CYAN, font=("Courier", 10, "bold"))
        self.conv_text.tag_config("user_text", foreground="#a5f3fc")
        self.conv_text.tag_config("system_text", foreground=MUTED, font=("Courier", 9, "italic"))

        # ── Sign language strip ───────────────────────────────────────
        sign_hdr = tk.Frame(self.root, bg=BG_PANEL, height=24)
        sign_hdr.pack(fill=tk.X)
        sign_hdr.pack_propagate(False)
        tk.Label(sign_hdr, text="🤟  Sign Language", bg=BG_PANEL,
                 fg=PURPLE_LT, font=("Courier", 8, "bold"), anchor="w"
                 ).pack(side=tk.LEFT, padx=12, pady=3)

        sign_strip = tk.Frame(self.root, bg=BG_CARD, height=72)
        sign_strip.pack(fill=tk.X)
        sign_strip.pack_propagate(False)
        self.sign_label = tk.Label(
            sign_strip, bg=BG_CARD, fg=MUTED,
            text="[ Sign image appears here ]",
            font=("Courier", 9)
        )
        self.sign_label.pack(expand=True)

        # ── Quick app buttons ─────────────────────────────────────────
        app_hdr = tk.Frame(self.root, bg=BG_PANEL, height=24)
        app_hdr.pack(fill=tk.X)
        app_hdr.pack_propagate(False)
        tk.Label(app_hdr, text="⚡  Quick Apps", bg=BG_PANEL,
                 fg=PURPLE_LT, font=("Courier", 8, "bold"), anchor="w"
                 ).pack(side=tk.LEFT, padx=12, pady=3)

        apps_frame = tk.Frame(self.root, bg=BG_VOID)
        apps_frame.pack(fill=tk.X, padx=8, pady=6)

        app_buttons = [
            ("▶\nYouTube",   "#ff0000", "open youtube"),
            ("💬\nWhatsApp", "#25d366", "open whatsapp"),
            ("📷\nInsta",    "#e1306c", "open instagram"),
            ("📧\nGmail",    "#ea4335", "open gmail"),
            ("🗺\nMaps",     "#4285f4", "open google maps"),
            ("🎵\nSpotify",  "#1db954", "open spotify"),
            ("📅\nCalendar", "#4285f4", "open calendar"),
            ("📝\nNotes",    "#fbbc04", "open notes"),
            ("📞\nPhone",    "#34a853", "open phone"),
            ("📸\nPhotos",   "#ff6d00", "open photos"),
            ("🛒\nStore",    "#01875f", "open play store"),
            ("⚙\nSettings", "#9aa0a6", "open settings"),
        ]
        for i, (label, color, cmd) in enumerate(app_buttons):
            btn = tk.Button(
                apps_frame, text=label, bg=BG_CARD,
                fg=color, activebackground=PURPLE_DIM,
                activeforeground=WHITE,
                font=("Courier", 7, "bold"), width=6, height=3,
                relief="flat", bd=0, cursor="hand2",
                command=lambda c=cmd: self._process_command(c)
            )
            btn.grid(row=i // 6, column=i % 6, padx=3, pady=2, sticky="nsew")
            # Glow border effect on hover
            btn.bind("<Enter>", lambda e, b=btn: b.config(bg=PURPLE_DIM))
            btn.bind("<Leave>", lambda e, b=btn: b.config(bg=BG_CARD))
        for c in range(6):
            apps_frame.columnconfigure(c, weight=1)

        # ── Input row ────────────────────────────────────────────────
        inp_frame = tk.Frame(self.root, bg=BG_DEEP, height=44)
        inp_frame.pack(fill=tk.X, side=tk.BOTTOM)
        inp_frame.pack_propagate(False)

        self.text_input = tk.Entry(
            inp_frame, bg=BG_PANEL, fg=WHITE,
            insertbackground=PURPLE_LT,
            font=("Courier", 11), bd=0, relief="flat",
            highlightthickness=1,
            highlightbackground=BORDER,
            highlightcolor=PURPLE
        )
        self.text_input.pack(side=tk.LEFT, fill=tk.BOTH,
                             expand=True, padx=(8, 4), pady=8)
        self.text_input.bind("<Return>", lambda e: self._send_text())
        self.text_input.insert(0, "Type or say Hey AURA...")
        self.text_input.bind("<FocusIn>",  self._clear_placeholder)
        self.text_input.bind("<FocusOut>", self._restore_placeholder)

        self.btn_send = tk.Button(
            inp_frame, text="Send", bg=PURPLE_DIM, fg=WHITE,
            activebackground=PURPLE, activeforeground=WHITE,
            font=("Courier", 9, "bold"), relief="flat", bd=0,
            cursor="hand2", padx=10,
            command=self._send_text
        )
        self.btn_send.pack(side=tk.LEFT, pady=8, padx=(0, 4))

        self.btn_mic = tk.Button(
            inp_frame, text="🎤", bg=PURPLE_DIM, fg=WHITE,
            activebackground=PURPLE, activeforeground=WHITE,
            font=("Arial", 14), relief="flat", bd=0,
            cursor="hand2", padx=8,
            command=self._manual_listen
        )
        self.btn_mic.pack(side=tk.LEFT, pady=8, padx=(0, 8))

    # ==================================================================
    # ANIMATIONS
    # ==================================================================
    def _start_orb_animation(self):
        def animate():
            self._orb_phase += 0.05
            # Pulse the orb
            scale = 1.0 + 0.06 * math.sin(self._orb_phase)
            cx, cy, r = 240, 100, int(42 * scale)
            self.orb_canvas.coords("orb_body",
                cx - r, cy - r, cx + r, cy + r)
            # Rotate rings (just pulse opacity effect via colour)
            ring_colors = [
                self._lerp_color(0.3 + 0.2 * math.sin(self._orb_phase)),
                self._lerp_color(0.3 + 0.2 * math.sin(self._orb_phase + 1)),
                self._lerp_color(0.3 + 0.2 * math.sin(self._orb_phase + 2)),
            ]
            for tag, color in zip(["ring1", "ring2", "ring3"], ring_colors):
                self.orb_canvas.itemconfig(tag, outline=color)
            self.root.after(40, animate)
        animate()

    def _lerp_color(self, t: float) -> str:
        t = max(0.0, min(1.0, t))
        r = int(76  + t * (139 - 76))
        g = int(29  + t * (92  - 29))
        b = int(149 + t * (246 - 149))
        return f"#{r:02x}{g:02x}{b:02x}"

    def _start_wave_animation(self):
        self._wave_running = True
        def animate():
            if not self._wave_running:
                return
            t = time.time() * 3.0
            for bar, x, i in self._wave_bars:
                h = 4 + 16 * abs(math.sin(t + i * 0.4))
                self.wave_canvas.coords(bar, x - 2, 22 - h, x + 2, 22 + h)
            self.root.after(40, animate)
        animate()

    def _set_wave_active(self, active: bool):
        """Make wave bars bright when listening, dim when idle."""
        color = PURPLE if not active else "#d8b4fe"
        for bar, _, _ in self._wave_bars:
            self.wave_canvas.itemconfig(bar, fill=color)

    # ==================================================================
    # WAKE WORD CALLBACKS
    # ==================================================================
    def _on_wake(self):
        self.root.after(0, self._wake_activate)

    def _wake_activate(self):
        self._set_wave_active(True)
        self.orb_canvas.itemconfig("orb_body", fill=PURPLE, outline="#d8b4fe")
        self.orb_canvas.itemconfig("orb_sub", text="ACTIVATED!", fill="#d8b4fe")
        self.status_bar.config(bg=PURPLE, fg=WHITE)
        self._set_status("🎤  AURA activated! Speak your command...")

    def _on_voice_command(self, text: str):
        self.root.after(0, self._handle_voice_cmd, text)

    def _handle_voice_cmd(self, text: str):
        self._set_wave_active(False)
        self.orb_canvas.itemconfig("orb_body", fill=PURPLE_DIM, outline=PURPLE)
        self.orb_canvas.itemconfig("orb_sub", text="WAKE WORD ACTIVE", fill=MUTED)
        self.status_bar.config(bg=PURPLE_DIM, fg="#d8b4fe")
        self._process_command(text)

    # ==================================================================
    # STATUS
    # ==================================================================
    def _set_status(self, msg: str):
        self.root.after(0, lambda: self._status_var.set(msg))

    # ==================================================================
    # MANUAL LISTEN BUTTON
    # ==================================================================
    def _manual_listen(self):
        self.btn_mic.config(text="🔴", bg="#7f1d1d")
        self._set_wave_active(True)
        self._set_status("🎤  Listening...")
        threading.Thread(target=self._manual_thread, daemon=True).start()

    def _manual_thread(self):
        text = self.voice.listen_once(timeout=6, phrase_limit=12)
        self.root.after(0, self._manual_result, text)

    def _manual_result(self, text: str):
        self.btn_mic.config(text="🎤", bg=PURPLE_DIM)
        self._set_wave_active(False)
        if text:
            self._process_command(text)
        else:
            self._set_status("❓  Didn't catch that — try again.")

    # ==================================================================
    # TEXT INPUT
    # ==================================================================
    def _send_text(self):
        text = self.text_input.get().strip()
        if not text or text == "Type or say Hey AURA...":
            return
        self.text_input.delete(0, tk.END)
        self._process_command(text)

    def _clear_placeholder(self, e):
        if self.text_input.get() == "Type or say Hey AURA...":
            self.text_input.delete(0, tk.END)
            self.text_input.config(fg=WHITE)

    def _restore_placeholder(self, e):
        if not self.text_input.get():
            self.text_input.insert(0, "Type or say Hey AURA...")
            self.text_input.config(fg=MUTED)

    # ==================================================================
    # COMMAND ROUTING
    # ==================================================================
    def _process_command(self, text: str):
        parsed  = self.processor.parse(text)
        action  = parsed["action"]
        payload = parsed["payload"]

        self.history.log(text)
        self._append_msg("YOU", text, user=True)

        response = ""

        if action == "greet":
            response = self.voice.greet()
        elif action == "time":
            response = self.voice.get_time()
        elif action == "date":
            response = self.voice.get_date()
        elif action == "open_app":
            response = self.launcher.open_app(payload)
        elif action == "close_app":
            response = self.launcher.close_app(payload)
        elif action == "yt_search":
            response = self.launcher.app_action("youtube", "search", payload)
        elif action == "yt_action":
            response = self.launcher.app_action("youtube", payload)
        elif action == "play_youtube":
            response = self.launcher.play_on_youtube(payload)
        elif action == "play_youtube_music":
            import urllib.parse
            webbrowser.open(f"https://music.youtube.com/search?q={urllib.parse.quote(payload)}")
            response = f"Playing '{payload}' on YouTube Music."
        elif action == "play_spotify":
            response = self.launcher.play_on_spotify(payload)
        elif action == "play_song":
            response = self.launcher.play_music(config.MUSIC_FOLDER, payload)
        elif action == "stop_music":
            response = self.launcher.stop_music()
        elif action == "next_track":
            response = self.launcher.next_track()
        elif action == "prev_track":
            response = self.launcher.previous_track()
        elif action == "volume_up":
            response = self.launcher.volume_up()
        elif action == "volume_down":
            response = self.launcher.volume_down()
        elif action == "mute":
            response = self.launcher.mute()
        elif action == "wa_chat":
            response = self.launcher.app_action("whatsapp", "new chat", payload)
        elif action == "wa_action":
            response = self.launcher.app_action("whatsapp", payload)
        elif action == "gmail_compose":
            response = self.launcher.app_action("gmail", "compose", payload)
        elif action == "gmail_inbox":
            response = self.launcher.app_action("gmail", "inbox")
        elif action == "gmail_action":
            response = self.launcher.app_action("gmail", payload)
        elif action == "ig_action":
            response = self.launcher.app_action("instagram", payload)
        elif action == "maps_navigate":
            response = self.launcher.app_action("google maps", "navigate", payload)
        elif action == "maps_nearby":
            response = self.launcher.app_action("google maps", "nearby", payload)
        elif action == "maps_search":
            response = self.launcher.app_action("google maps", "search", payload)
        elif action == "cal_new":
            response = self.launcher.app_action("calendar", "new event", payload)
        elif action == "cal_open":
            response = self.launcher.open_app("calendar")
        elif action == "clock_alarm":
            response = self.launcher.app_action("clock", "set alarm", payload)
        elif action == "clock_timer":
            response = self.launcher.app_action("clock", "set timer", payload)
        elif action == "clock_stopwatch":
            response = self.launcher.app_action("clock", "stopwatch")
        elif action == "notes_new":
            response = self.launcher.app_action("notes", "new note", payload)
        elif action == "notes_open":
            response = self.launcher.open_app("notes")
        elif action == "photos_open":
            response = self.launcher.open_app("photos")
        elif action == "photos_search":
            response = self.launcher.app_action("photos", "search", payload)
        elif action == "phone_call":
            response = self.launcher.app_action("contacts", "search", payload)
        elif action == "contacts_add":
            response = self.launcher.app_action("contacts", "new contact")
        elif action == "contacts_search":
            response = self.launcher.app_action("contacts", "search", payload)
        elif action == "store_search":
            response = self.launcher.app_action("play store", "search", payload)
        elif action == "store_action":
            response = self.launcher.app_action("play store", payload)
        elif action in ("settings_action", "settings_toggle"):
            response = self.launcher.open_app("settings")
        elif action in ("recorder_start", "recorder_stop"):
            response = self.launcher.open_app("recorder")
        elif action == "screenshot":
            response = self.launcher.take_screenshot()
        elif action == "lock_screen":
            response = self.launcher.lock_screen()
        elif action == "shutdown":
            response = self.launcher.shutdown()
        elif action == "restart":
            response = self.launcher.restart()
        elif action == "list_apps":
            response = self.launcher.list_apps()
        elif action == "google_search":
            response = self.web.google_search(payload)
        elif action == "wikipedia_search":
            response = self.web.wikipedia_search(payload)
        elif action in ("add_task", "add_task_alt"):
            response = self.todo.add_task(payload) if payload else "Please say the task name."
            self._refresh_tasks_silent()
        elif action == "show_tasks":
            response = self.todo.show_tasks()
        elif action == "complete_task":
            response = self.todo.complete_task(payload) if payload else "Say the task number."
            self._refresh_tasks_silent()
        elif action == "show_history":
            display, spoken = self.history.show_history()
            self._append_msg("AURA", display)
            self._speak(spoken)
            self._show_sign(spoken)
            self.history.log(text, spoken)
            self._set_status("👂  Listening for  'Hey AURA'...")
            return
        elif action == "clear_history":
            response = self.history.clear_history()
        elif action == "toggle_voice":
            response = self.access.toggle_voice()
        elif action == "toggle_text":
            response = self.access.toggle_text()
        elif action == "toggle_sign":
            response = self.access.toggle_sign()
        elif action == "toggle_high_contrast":
            response = self.access.toggle_high_contrast()
        elif action == "weather":
            city = payload or config.DEFAULT_CITY
            response = self.web.get_weather(city, config.WEATHER_API_KEY)
        elif action == "weather_default":
            response = self.web.get_weather(config.DEFAULT_CITY, config.WEATHER_API_KEY)
        elif action == "forecast":
            city = payload or config.DEFAULT_CITY
            response = self.web.get_weather_forecast(city, config.WEATHER_API_KEY)
        elif action == "news":
            response = self.web.get_news(config.NEWS_API_KEY, config.NEWS_COUNTRY)
        elif action == "news_topic":
            response = self.web.get_news_by_topic(payload, config.NEWS_API_KEY)
        elif action == "productivity":
            display, spoken = self.todo.productivity_report()
            self._append_msg("AURA", display)
            self._speak(spoken)
            self._show_sign(spoken)
            self.history.log(text, spoken)
            self._set_status("👂  Listening for  'Hey AURA'...")
            return
        elif action == "exit":
            response = "Goodbye! Have a great day!"
            self._append_msg("AURA", response)
            self._speak(response)
            self.root.after(2200, self.root.destroy)
            return
        else:
            response = (
                f"I heard: '{text}'.\n"
                "Try: 'open WhatsApp' · 'play music' · 'weather in Delhi' · 'add task buy milk'"
            )

        self._append_msg("AURA", response)
        self._speak(response)
        self._show_sign(response)
        self.history.log(text, response)
        self._set_status("👂  Listening for  'Hey AURA'...")

    # ==================================================================
    # CONVERSATION
    # ==================================================================
    def _append_msg(self, speaker: str, text: str, user=False, system=False):
        self.conv_text.config(state=tk.NORMAL)
        if system:
            self.conv_text.insert(tk.END, f"\n{text}\n", "system_text")
        elif user:
            self.conv_text.insert(tk.END, "\n👤 YOU\n", "user_name")
            self.conv_text.insert(tk.END, f"{text}\n", "user_text")
        else:
            self.conv_text.insert(tk.END, "🤖 AURA\n", "aura_name")
            self.conv_text.insert(tk.END, f"{text}\n", "aura_text")
        self.conv_text.config(state=tk.DISABLED)
        self.conv_text.see(tk.END)

    # ==================================================================
    # SIGN LANGUAGE
    # ==================================================================
    def _show_sign(self, text: str):
        if not self.access.sign_enabled:
            self.sign_label.config(image="", text="[ Sign language OFF ]")
            return
        path = self.access.get_sign_image_path(text)
        if path and PIL_OK:
            try:
                img   = Image.open(path).resize((62, 62), Image.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                self._sign_image_ref = photo
                self.sign_label.config(image=photo, text="")
                return
            except Exception:
                pass
        keyword = self._sign_keyword(text)
        disp = f"🤟  [{keyword.upper()}]" if keyword else "[ No sign available ]"
        self.sign_label.config(image="", text=disp, fg=PURPLE_LT, font=("Courier", 10, "bold"))

    def _sign_keyword(self, text: str) -> str:
        from modules.accessibility import SIGN_MAP
        for kw in SIGN_MAP:
            if kw in text.lower():
                return kw
        return ""

    # ==================================================================
    # TTS
    # ==================================================================
    def _speak(self, text: str):
        if not self.access.voice_enabled:
            return
        threading.Thread(target=self.voice.speak, args=(text,), daemon=True).start()

    # ==================================================================
    # TASKS (silent refresh, no popup)
    # ==================================================================
    def _refresh_tasks_silent(self):
        pass  # tasks stored in JSON, shown via 'show tasks' voice command

    # ==================================================================
    # ACCESSIBILITY BUTTONS
    # ==================================================================
    def _toggle_voice(self):
        self._append_msg("AURA", self.access.toggle_voice())

    def _toggle_text(self):
        self._append_msg("AURA", self.access.toggle_text())

    def _toggle_sign(self):
        self._append_msg("AURA", self.access.toggle_sign())

    def _toggle_contrast(self):
        self._append_msg("AURA", self.access.toggle_high_contrast())