from serpapi import GoogleSearch

params = {
    "engine": "google",
    "q": "India latest news",
    "api_key": "6d602da9257d8b111907b4a9c0eb1464dd389d7d1166fb5352852e32eae1480c"
}

search = GoogleSearch(params)
results = search.get_dict()

import json
print(json.dumps(results, indent=2))
