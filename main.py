import re
import uuid
import torch
import textwrap

from TTS.api import TTS

from logseq_client import LogseqClient
from mistral_client import MistralClient

from utils import blocks_from_tree

logseq = LogseqClient(base_url="http://127.0.0.1:12315", token="logseq-token-test")
mistral = MistralClient()

device = "cuda" if torch.cuda.is_available() else "cpu"
tts = TTS(model_name="tts_models/de/thorsten/vits", progress_bar=False).to(device)

graph = logseq.call("logseq.App.getCurrentGraph")
path = graph['path']
assets = path + "/assets"

print(f"Detected assets path: {assets}")

page = logseq.call("logseq.Editor.getCurrentPage")
print(f"Current page name: {page['name']}")
print(f"Current page id: {page['uuid']}")

tree = logseq.call("logseq.Editor.getPageBlocksTree", page['uuid'])
blocks = blocks_from_tree(tree)

word_re = re.compile(r"Слово:\s*\{\{c1\s+([^\}]+)\}\}")
tags_re = re.compile(r"tags::\s*([^\n]+)")

updated = []

for block in blocks:
    bid = block['uuid']
    content = block['content']

    if "#card" not in content:
        print(f"> Skipping block {bid} because it is not a card <")
        continue

    if "Перевод" in content:
        print(f"> Skipping block {bid} because it contains 'Перевод' <")
        continue

    word_match = word_re.search(block['content'])
    if not word_match:
        print(f"> Skipping block {bid} because it does not contain a word <")
        continue
    word = word_match.group(1)

    print(">" * 50)
    print(f"Word: {word}")

    tags_match = tags_re.search(content)
    tags = tags_match.group(1) if tags_match else ""
    tags = [tag.strip() for tag in tags.split(",")]
    tags = [tag.lower() for tag in tags if tag]

    print(f"Tags: {tags}")

    gen = mistral.request(word, tags)
    print(f"Translation: {gen['translation']}")
    print(f"Example: {gen['example']}")
    print(f"Form in example: {gen['form_in_example']}")

    example = gen['example'].strip().replace(gen['form_in_example'], f"{{{{c1 {gen['form_in_example']}}}}}")
    example = example + "." if not example.endswith(".") else example
    translation = gen['translation'].strip().replace(".", "")
    translation = f"{{{{c2 {translation}}}}}"

    text = f"{word}. {gen['example']}"
    print(f"Text to generate audio: {text}")
    name = word.replace(" ", "_").lower() + "-" + str(uuid.uuid4()) + ".wav"
    audio_path = f"{assets}/{name}"
    print(f"Generating audio...")
    tts.tts_to_file(text=text, file_path=audio_path)
    print(f"Audio saved to {audio_path}")

    # TODO: Better way to upload audio to assets
    new_content = content + textwrap.dedent(f"""
        Перевод: {translation}.
        Пример: {example}.
        {{{{c1 ![audio](../assets/{name})}}}}
    """)

    logseq.call("logseq.Editor.updateBlock", bid, new_content)

    updated.append(word)

    print("<" * 50)

print(f"Updated {len(updated)} words: {', '.join(updated)}")

