from dotenv import load_dotenv
import re
import time
import os
import textwrap
from kevinlulee import myenv, writefile
import yaml
from google import genai
from google.genai import types
load_dotenv()


DEBUG_OUTPUT_DIR = myenv("generative.debugging.output_directory")

def gemini(
    query="How does AI work?",
    system_instruction=None,
    max_output_tokens=None,
    temperature=None,
    model="gemini-2.0-flash",
) -> types.GenerateContentResponseOrDict:
    api_key = os.getenv("GEMINI_API_KEY")
    client = genai.Client(api_key=api_key)
    config = types.GenerateContentConfig()

    if system_instruction:
        config.system_instruction = textwrap.dedent(system_instruction).strip()
    if max_output_tokens:
        config.max_output_tokens = max_output_tokens
    if temperature is not None:
        config.temperature = temperature

    r = client.models.generate_content(model=model, contents=[query], config=config)
    if DEBUG_OUTPUT_DIR:
        store = {
            'instruct': system_instruction,
            'query': query,
            'response': r.text,
        }
        file = os.path.join(DEBUG_OUTPUT_DIR, f'{time.time()}.json')
        writefile(file, store)
    return r

def collect_fenced_sections(text):
    pattern = re.compile(r"```(\w+)?\n(.*?)```", re.DOTALL)
    matches = pattern.findall(text)
    return [{"lang": lang or "", "code": code.strip()} for lang, code in matches]
def capture(response: types.GenerateContentResponseOrDict):

    matches = collect_fenced_sections(response.text)
    assert len(matches) < 2, "collect_fenced_sections matched more than one chunk. currently, only permitting a single chunk."
    if matches:
        base = matches[0]
        code = base.get("code")
        lang = base.get("lang")
        if lang == 'yaml':
            return yaml.safe_load(code)
    else:
        return response.text
