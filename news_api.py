import requests

API_KEY = "ac7326b13774455583779b88227761a5"

def fetch_news(country="in", category="general", max_articles=5):
    url = f"https://newsapi.org/v2/top-headlines?country={country}&category={category}&apiKey={API_KEY}"

    try:
        response = requests.get(url, timeout=10)
        print("Status Code:", response.status_code)
        print("Raw Response:", response.text[:300])

        if response.status_code != 200:
            print("❌ Failed to fetch news from API.")
            return []

        data = response.json()
        articles = data.get("articles", [])
        headlines = []

        for article in articles[:max_articles]:
            content = article["title"]
            if article.get("description"):
                content += " - " + article["description"]
            headlines.append(content)

        return headlines

    except requests.exceptions.RequestException as e:
        print("❌ Network/API Error:", e)
        return []

    except Exception as e:
        print("❌ Unexpected Error:", e)
        return []
