import requests

def get_votd():
    url = "https://beta.ourmanna.com/api/v1/get?format=json&order=daily"
    headers = {"accept": "application/json"}
    response = requests.get(url, headers=headers)
    return response.json()

# Example usage
if __name__ == "__main__":
    print(get_votd())