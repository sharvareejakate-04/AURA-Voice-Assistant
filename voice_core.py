"""
AURA Voice Core - Fixed continuous listening
Wake word detection + immediate command capture with no gap.
"""

import speech_recognition as sr
import pyttsx3
import datetime
import threading
import time

WAKE_WORDS = [
    "hey aura", "aura", "hey ora", "ora",
    "ok aura", "okay aura", "hi aura", "hello aura",
]


class VoiceCore:
    def __init__(self, on_wake=None, on_command=None, on_status=None):
        self.on_wake    = on_wake    or (lambda: None)
        self.on_command = on_command or (lambda t: None)
        self.on_status  = on_status  or (lambda t: None)

        self._running    = False
        self._speak_lock = threading.Lock()

        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold         = 300
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold          = 0.6   # shorter pause = faster response

    # ------------------------------------------------------------------
    # TTS — fresh engine every call, never gets stuck
    # ------------------------------------------------------------------
    def _fix_pronunciation(self, text: str) -> str:
        import re
        text = re.sub(r'\bAURA\b', 'Ora', text)
        text = re.sub(r'\baura\b', 'Ora', text)
        return text

    def speak(self, text: str):
        with self._speak_lock:
            try:
                engine = pyttsx3.init()
                self._set_female_voice(engine)
                engine.setProperty("rate", 160)
                engine.setProperty("volume", 1.0)
                text = self._fix_pronunciation(text)
                engine.say(text)
                engine.runAndWait()
                engine.stop()
            except Exception:
                pass

    def _set_female_voice(self, engine):
        voices = engine.getProperty("voices")
        female_kw = ["female", "woman", "zira", "hazel", "susan",
                     "victoria", "karen", "samantha", "helena", "f1"]
        for v in voices:
            if any(kw in v.name.lower() for kw in female_kw):
                engine.setProperty("voice", v.id)
                return
        if len(voices) > 1:
            engine.setProperty("voice", voices[1].id)

    # ------------------------------------------------------------------
    # WAKE WORD LOOP — fixed, no gap between wake and command
    # ------------------------------------------------------------------
    def start_wake_word_loop(self):
        self._running = True
        threading.Thread(target=self._wake_loop, daemon=True).start()

    def stop_wake_word_loop(self):
        self._running = False

    def _wake_loop(self):
        """
        Single open microphone — listens for wake word,
        then immediately listens for command in SAME session.
        No mic close/reopen gap.
        """
        while self._running:
            try:
                with sr.Microphone() as source:
                    # Calibrate once per session
                    self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                    self.on_status("👂  Listening for  'Hey Ora'...")

                    while self._running:
                        # ── Step 1: Listen for wake word ──
                        try:
                            self.on_status("👂  Listening for  'Hey Ora'...")
                            audio = self.recognizer.listen(
                                source,
                                timeout=None,          # wait forever for wake word
                                phrase_time_limit=4    # max 4 sec per phrase
                            )
                        except Exception:
                            break   # mic error — restart outer loop

                        # Recognise wake word phrase
                        try:
                            heard = self.recognizer.recognize_google(audio).lower().strip()
                        except (sr.UnknownValueError, sr.RequestError):
                            continue  # nothing heard — keep waiting

                        # Check if it's the wake word
                        if not any(w in heard for w in WAKE_WORDS):
                            continue  # not wake word — keep waiting

                        # ── Wake word detected! ──
                        self.on_wake()
                        self.on_status("🎤  Listening for your command...")

                        # Speak "yes" in background — DON'T block mic
                        threading.Thread(
                            target=self.speak,
                            args=("Hey! What can I do for you?",),
                            daemon=True
                        ).start()

                        # Small pause so our "yes" doesn't get picked up as command
                        time.sleep(1.8)

                        # ── Step 2: Listen for command — SAME mic, no gap ──
                        try:
                            self.on_status("🎤  Go ahead, I'm listening...")
                            cmd_audio = self.recognizer.listen(
                                source,
                                timeout=6,             # wait up to 6s for user to start
                                phrase_time_limit=10   # up to 10s for the command
                            )
                        except sr.WaitTimeoutError:
                            self.on_status("❓  Didn't catch that. Say 'Hey Ora' again.")
                            continue
                        except Exception:
                            break

                        # Recognise command
                        try:
                            command = self.recognizer.recognize_google(cmd_audio).lower().strip()
                        except sr.UnknownValueError:
                            self.on_status("❓  Didn't catch that. Say 'Hey Ora' again.")
                            continue
                        except sr.RequestError:
                            self.on_status("⚠  Internet error. Check your connection.")
                            continue

                        if command:
                            self.on_status(f"🗣  You said: {command}")
                            self.on_command(command)
                        else:
                            self.on_status("❓  Didn't catch that. Say 'Hey Ora' again.")

            except Exception:
                time.sleep(1)   # mic unavailable — wait and retry
                continue

    # ------------------------------------------------------------------
    # Manual listen (mic button)
    # ------------------------------------------------------------------
    def listen_once(self, timeout=6, phrase_limit=12) -> str:
        try:
            with sr.Microphone() as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.3)
                audio = self.recognizer.listen(
                    source, timeout=timeout, phrase_time_limit=phrase_limit)
                return self.recognizer.recognize_google(audio).lower().strip()
        except (sr.WaitTimeoutError, sr.UnknownValueError, sr.RequestError):
            return ""
        except Exception:
            return ""

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def get_time(self) -> str:
        now    = datetime.datetime.now()
        hour   = now.strftime("%I").lstrip("0") or "12"
        minute = now.strftime("%M")
        period = now.strftime("%p")
        return f"The current time is {hour}:{minute} {period}."

    def get_date(self) -> str:
        now = datetime.datetime.now()
        return f"Today is {now.strftime('%A')}, {now.strftime('%B %d, %Y')}."

    def greet(self) -> str:
        hour   = datetime.datetime.now().hour
        period = "morning" if hour < 12 else "afternoon" if hour < 17 else "evening"
        return f"Good {period}! I'm Ora, your voice assistant. How can I help you today?"