from serpapi import GoogleSearch

def get_search_results(query, max_results=5):

    params = {
        "engine": "google",
        "q": query,
        "api_key": "6d602da9257d8b111907b4a9c0eb1464dd389d7d1166fb5352852e32eae1480c"
    }
    search = GoogleSearch(params)
    results = search.get_dict()
    links = []
    for res in results.get("organic_results", [])[:max_results]:
        links.append({"title": res.get("title"), "link": res.get("link")})
    return links
