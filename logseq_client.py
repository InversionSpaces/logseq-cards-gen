import requests

class LogseqClient:
    def __init__(self, base_url: str, token: str):
        self.base_url = base_url
        self.token = token

    def call(self, method: str, *args):
        """Make a POST request to the Logseq API with JSON data."""
        url = f"{self.base_url}/api"
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        body = {"method": method}
        if args:
            body.update({"args": args})

        response = requests.post(url, json=body, headers=headers)
        response.raise_for_status()

        result = response.json()
        if result is None:
            return None
        if "error" in result:
            raise Exception(result["error"])
        
        return result