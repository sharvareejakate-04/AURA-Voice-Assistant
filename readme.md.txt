# 🤖 AURA — Accessible Universal Response Assistant

<div align="center">

![Python](https://img.shields.io/badge/Python-3.10+-blue?style=for-the-badge&logo=python)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-green?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-purple?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Active-success?style=for-the-badge)

**A Python-based smart voice assistant focused on accessibility and productivity.**
Say *"Hey AURA"* — no button clicking needed.

</div>

---

## ✨ Features

| Feature | Description |
|---|---|
| 🎤 Wake Word | Say **"Hey AURA"** — always listening, no click needed |
| 🔊 Female Voice | Natural TTS voice responds to every command |
| ♿ Accessibility | Voice output (blind users) + Sign language images (deaf users) |
| 📱 22 Apps | Open & close YouTube, WhatsApp, Instagram, Gmail, Maps and more |
| ✅ Smart Tasks | Add, view, complete tasks — saved to file |
| 🕑 History | Every command stored and reviewable |
| 🌤 Weather | Real-time weather for any city worldwide |
| 📰 News | Live top headlines via NewsAPI |
| 🎵 Music | Play, stop, next, previous track |
| 🌙 Purple Night UI | Beautiful dark mobile-style interface |

---

## 🖥️ Demo

> *Say "Hey AURA" → AURA activates → Say your command → AURA responds with voice + text + sign language*

**Voice Commands:**
```
Hey AURA → open WhatsApp
Hey AURA → what is the time
Hey AURA → weather in Mumbai
Hey AURA → play music
Hey AURA → add task finish the report
Hey AURA → show tasks
Hey AURA → open YouTube
Hey AURA → navigate to Delhi
Hey AURA → news headlines
Hey AURA → goodbye
```

---

## 📁 Project Structure

```
AURA/
├── main.py                    ← Run this to start
├── config.py                  ← API keys & settings
├── requirements.txt
├── data/
│   ├── tasks.json             ← Auto-created task storage
│   └── history.json           ← Auto-created command history
├── assets/
│   └── signs/                 ← Sign language images (19 words)
└── modules/
    ├── voice_core.py          ← Wake word + Speech recognition + TTS
    ├── gui.py                 ← Purple Night UI (Tkinter)
    ├── app_launcher.py        ← 22 phone apps open/close control
    ├── command_processor.py   ← Voice command parser
    ├── web_features.py        ← Google, Wikipedia, Weather, News
    ├── todo_manager.py        ← Smart to-do list
    ├── history_manager.py     ← Command history storage
    └── accessibility.py       ← Voice/Text/Sign/Contrast modes
```

---

## ⚙️ Installation

```bash
pip install -r requirements.txt
python main.py
```

---

## 🔑 Optional API Keys (Free)

Edit `config.py` with your free keys from:
- Weather: https://openweathermap.org
- News: https://newsapi.org

---

## ♿ Accessibility Features

- **Blind users** — full voice control, wake word, TTS responses
- **Deaf users** — text display + real ASL sign language images
- **High contrast mode** — yellow on black for max readability

---

## 🛠️ Tech Stack

Python · SpeechRecognition · pyttsx3 · Tkinter · Pillow · Wikipedia API · OpenWeatherMap · NewsAPI

---

## 👤 Author

**Sharvaree Jakate** — Intern @Hex Software
[LinkedIn](https://www.linkedin.com/in/sharvaree-jakate-b0294225b) · [GitHub](https://github.com/sharvareejakate-04)

---

<div align="center">Made with ❤️ for accessibility and inclusion</div>