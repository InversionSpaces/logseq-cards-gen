from ollama import Client

from config import OLLAMA_MODEL

class OllamaClient:
    def __init__(self):
        self.client = Client()

    def request(self, phrase: str, tags: list[str] = []) -> dict:
        prompt = f"Translate the following phrase from German to Russian: {phrase}. "
        if tags:
            prompt += f"Tags provided to help with translation: {', '.join(tags)}. "
        prompt += "Also generate an example usage of the phrase in a sentence in german. "
        prompt += "Use simple sentences, avoid complex grammar and vocabulary. "
        prompt += "In the example highlight the usage of the phrase with a double asterisk. "
        prompt += "Return the result in JSON format with the following keys: translation, example. "
        prompt += "Start the translation and the example from capital letter. "
        prompt += "Do not translate the example usage. "
        prompt += "Do not include any text before or after the JSON object. "
        
        response = self.client.generate(model=OLLAMA_MODEL, prompt=prompt)

        return response.response
        

