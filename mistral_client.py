import json
import time
from pydantic import BaseModel

from mistralai import Mistral

from config import MISTRAL_API_KEY, MISTRAL_MODEL

class TranslationResponse(BaseModel):
    translation: str
    example: str
    form_in_example: str

class MistralClient:
    def __init__(self):
        self.client = Mistral(MISTRAL_API_KEY)
        self.delay_ms = 1000
        self.last_request_time = 0

    def request(self, phrase: str, tags: list[str] = []) -> dict:
        system_prompt = """
            You are helpful language learning assistant.
            For each word or phrase user provides in German (possibly with tags to aid translation),
            you will generate a translation to Russian
            and an example usage of the phrase in one sentence in German.
            Use simple sentences, avoid complex grammar and vocabulary.
            Add form of the phrase in the example usage (without any additional words) so 
            it can be found in the example usage.
            Do not translate the example usage.
            Start the translation and the example usage from capital letter.
            Do **not** include dots at the end of the translation.
            Do **not** include any additional text before or after the translation and the example usage.
        """.strip()
        
        user_prompt = f"Translate: '{phrase}'. Tags: {', '.join(tags)}."

        since_last_request = time.time() - self.last_request_time
        if since_last_request < self.delay_ms:
            time.sleep(self.delay_ms - since_last_request)

        self.last_request_time = time.time()

        response = self.client.chat.parse(
            model=MISTRAL_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format=TranslationResponse,
            max_tokens=256
        )

        return json.loads(response.choices[0].message.content)
