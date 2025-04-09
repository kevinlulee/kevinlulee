# aicmp 
# here are the changes id like
# capture output should return a dataclass generative result with 3 fields. code, summary, response. (the initial response)
# change capture output to a better name
# have function claude be similar to that of gemini
# both claude and gemini should return the generative result
# have their models be global constants MODELS
# write a wrapper that takes the same args/kwargs of claude and gemini called agent with an additional param agent. type of agent is a literal[claude/gemini/deepseek/openai] 

from dotenv import load_dotenv
import re
import time
import os
import json
import textwrap
import yaml
from kevinlulee import writefile, trimdent
from google import genai
import anthropic
from google.genai import types
load_dotenv()

# asd = asdf
def claude(query, system = None, capture = False):

    client = anthropic.Anthropic(api_key = os.getenv('ANTHROPIC_API_KEY'))
    message = client.messages.create(
        model="claude-3-7-sonnet-20250219",
        system=system,
        messages=[
            {"role": "user", "content": query}
        ]
    )
    return capture_output(r, capture = capture)


def gemini(
    query="How does AI work?",
    system=None,
    capture = False,
) -> types.GenerateContentResponseOrDict:

    api_key = os.getenv("GEMINI_API_KEY")
    client = genai.Client(api_key=api_key)
    config = types.GenerateContentConfig()

    if system:
        config.system_instruction = trimdent(system)

    r = client.models.generate_content(model=MODELS['gemini'], contents=[query], config=config)

    return capture_output(r, capture = capture)



def capture_output(response, capture = False):
    if capture == False: return response

    text = getattr(response, 'text', None) or getattr(response, 'content', None)
    parts = split(text, '^```(\w+)\n(.*?)```', flags = re.M | re.DOTALL)
    l = len(parts)
    if l == 3:
        lang, code, summary = parts
        return code, summary
    elif l == 2:
        lang, code = parts

        if lang == 'yaml':
            return yaml.safe_load(code)
        if lang == 'json':
            return json.loads(code)

        return code, '' 
    elif l == 4:
        # 2 code blocks
        return text
    elif l == 5:
        # 2 code blocks
        # one text block
        return text
    else:
        return text
