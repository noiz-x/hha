import requests

def bible(query, version='kjv'):
    response = requests.get(f"https://bible-api.com/{query}?translation={version}")
    if response.status_code != 200:
        return requests.get(f"https://bible-api.com/{query}?translation=kjv").json()
    return response.json()

# Example usage
if __name__ == "__main__":
    print(bible('john 3:16-17', 'msg'))
