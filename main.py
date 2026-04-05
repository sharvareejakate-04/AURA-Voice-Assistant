"""
AURA - Accessible Universal Response Assistant
==============================================
HOW TO RUN:
  python main.py
  OR double-click this file (if Python is associated with .py files)
"""

import sys
import os

# Make sure we can find all modules regardless of where you run from
os.chdir(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import tkinter as tk
from gui import AuraGUI


def main():
    root = tk.Tk()
    root.iconbitmap(default="") if sys.platform == "win32" else None
    app = AuraGUI(root)
    root.protocol("WM_DELETE_WINDOW", lambda: (
        app.voice.stop_wake_word_loop(), root.destroy()
    ))
    root.mainloop()


if __name__ == "__main__":
    main()