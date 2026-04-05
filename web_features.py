"""
AURA Module: Web Features
Handles YouTube, Google, web search, and Wikipedia.
"""

import webbrowser
import urllib.parse
import wikipedia


class WebFeatures:
    def __init__(self):
        wikipedia.set_lang("en")

    # ------------------------------------------------------------------
    # Browser shortcuts
    # ------------------------------------------------------------------
    def open_youtube(self) -> str:
        webbrowser.open("https://www.youtube.com")
        return "Opening YouTube for you."

    def open_google(self) -> str:
        webbrowser.open("https://www.google.com")
        return "Opening Google."

    # ------------------------------------------------------------------
    # Search
    # ------------------------------------------------------------------
    def google_search(self, query: str) -> str:
        if not query:
            return "Please tell me what to search for."
        encoded = urllib.parse.quote(query)
        webbrowser.open(f"https://www.google.com/search?q={encoded}")
        return f"Searching Google for: {query}"

    def wikipedia_search(self, query: str) -> str:
        if not query:
            return "Please tell me what to look up on Wikipedia."
        try:
            summary = wikipedia.summary(query, sentences=3, auto_suggest=True)
            return summary
        except wikipedia.DisambiguationError as e:
            options = ", ".join(e.options[:3])
            return f"Multiple results found. Did you mean: {options}?"
        except wikipedia.PageError:
            return f"Sorry, I couldn't find anything on Wikipedia for '{query}'."
        except Exception:
            return "Wikipedia search failed. Please check your internet connection."

    # ------------------------------------------------------------------
    # Optional: Weather & News (requires API keys in config)
    # ------------------------------------------------------------------
    def get_weather(self, city: str, api_key: str) -> str:
        """Fetch weather from OpenWeatherMap. Set your API key in config.py."""
        if not api_key or api_key == "1ed89b17859e0cc2f61f39722cc2cac3":
            return "Weather feature requires an OpenWeatherMap API key in config.py."
        try:
            import requests
            url = (
                f"https://api.openweathermap.org/data/2.5/weather"
                f"?q={city}&appid={api_key}&units=metric"
            )
            resp = requests.get(url, timeout=5)
            data = resp.json()
            if data.get("cod") != 200:
                return f"Couldn't get weather for {city}."
            desc = data["weather"][0]["description"].capitalize()
            temp = data["main"]["temp"]
            feels = data["main"]["feels_like"]
            humidity = data["main"]["humidity"]
            return (
                f"Weather in {city}: {desc}. "
                f"Temperature is {temp}°C, feels like {feels}°C. "
                f"Humidity: {humidity}%."
            )
        except Exception as e:
            return f"Weather fetch failed: {e}"

    def get_news(self, api_key: str, country: str = "us") -> str:
        """Fetch top headlines from NewsAPI. Set your API key in config.py."""
        if not api_key or api_key == "d4726b634a3436c930b77b83dd9f5b3":
            return "News feature requires a NewsAPI key in config.py."
        try:
            import requests
            url = (
                f"https://newsapi.org/v2/top-headlines"
                f"?country={country}&apiKey={api_key}&pageSize=5"
            )
            resp = requests.get(url, timeout=5)
            data = resp.json()
            articles = data.get("articles", [])
            if not articles:
                return "No headlines found right now."
            headlines = [f"{i+1}. {a['title']}" for i, a in enumerate(articles[:5])]
            return "Here are today's top headlines:\n" + "\n".join(headlines)
        except Exception as e:
            return f"News fetch failed: {e}"
