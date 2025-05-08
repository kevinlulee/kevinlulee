from dotenv import load_dotenv
import re
import time
import os
import json
import textwrap
import yaml
from kevinlulee import writefile, split
from google import genai
import anthropic
from dataclasses import dataclass
from typing import Literal, Optional, Any

from kevinlulee.file_utils import clip

load_dotenv()

# --- Constants ---
MODELS = {
    # Using models specified in the original code or sensible defaults
    # Note: claude-3-7-sonnet-20250219 seems like a typo or future model, using standard Sonnet 3.5
    # "claude": "claude-3-5-sonnet-20240620",
    'claude': 'claude-3-7-sonnet-20250219',
    # Using standard Gemini 1.5 Pro
    "gemini": "gemini-2.5-pro-exp-03-25",
    # Placeholders for potential future use
    "deepseek": "deepseek-coder", # Replace with actual model ID when implemented
    "openai": "gpt-4o",         # Replace with actual model ID when implemented
}

# --- Dataclass for Standardized Output ---
@dataclass
class GenerativeResult:
    code: Optional[str] = None
    lang: Optional[str] = None
    text: Optional[str] = None
    summary: Optional[str] = None
    response: Optional[Any] = None # Store the raw response


# --- Core Functions ---

class ProcessResponse:
    def __init__(self):
        
    


def process_llm_response(raw: Any) -> GenerativeResult:
    """
    Processes the raw response from an LLM API call, extracts code and summary,
    and returns a standardized GenerativeResult object.

    Args:
        raw_response: The raw response object from the Anthropic or Google GenAI API.

    Returns:
        A GenerativeResult dataclass instance containing extracted code, summary,
        and the original response.
    """
    text = None
    code = None
    summary = None

    if isinstance(raw, anthropic.types.Message):
        text = raw.content[0].text
    elif isinstance(raw, genai.types.GenerateContentResponse):
        text = raw.text

    if text:
        # Use the provided split function to find code blocks
        # Pattern: ```lang\ncode\n```
        parts = split(text, r'^```(\w+)\n(.*?)\n```', flags=re.M | re.DOTALL)
        l = len(parts)

        lang = None
        if l == 3:
            # Found language, code, and summary text after code
            lang, extracted_code, extracted_summary = parts
            code = extracted_code.strip()
            summary = extracted_summary.strip()
        elif l == 2:
            # Found language and code, but no text after
            lang, extracted_code = parts
            code = extracted_code.strip()
            summary = None # Or could be empty string ""
        elif l == 1:
            # No code block found, assume the whole text is the summary
            summary = parts[0].strip()
            code = None
        elif l == 4:
            # lang_a, code_a, lang_b, code_b = parts
            # if lang_b == 'yml' or lang_b == 'yaml':
            #     return process
            
            print(f"Warning: Unexpected number of parts ({l}) after splitting text. Treating full text as summary.")
            summary = text.strip()
            code = None
            clip(text)
            return 
    else:
        # Handle cases where text extraction failed
        print("Warning: Could not extract text from the response object.")
        summary = "Error: Could not process response text."


    return GenerativeResult(code=code, summary=summary, response=raw, lang = lang, text = text)


def claude(
    query: str,
    system: Optional[str] = None
) -> GenerativeResult:
    """
    Sends a query to the Anthropic Claude model and returns a structured result.

    Args:
        query: The user's query or prompt.
        system: An optional system prompt to guide the model's behavior.

    Returns:
        A GenerativeResult object containing the processed output.
    """
    api_key = os.getenv('ANTHROPIC_API_KEY')
    client = anthropic.Anthropic(api_key=api_key)
    model_name = MODELS["claude"]

    messages = [{"role": "user", "content": query}]
    processed_system = textwrap.dedent(system).strip() if system else None

    try:
        raw_response = client.messages.create(
            model=model_name,
            system=processed_system, # Pass system prompt here
            messages=messages,
            max_tokens=4096 # Adjust max_tokens as needed
        )
        return process_llm_response(raw_response)
    # except genai.client.
    except anthropic.APIConnectionError as e:
        print(f"Anthropic API connection error: {e}")
        raise
    except anthropic.RateLimitError as e:
        print(f"Anthropic rate limit exceeded: {e}")
        raise
    except anthropic.APIStatusError as e:
        print(f"Anthropic API status error: {e.status_code} - {e.response}")
        raise


def gemini(
    query: str = "Explain the theory of relativity.", # Added default for consistency
    system: Optional[str] = None,
) -> GenerativeResult:
    """
    Sends a query to the Google Gemini model and returns a structured result.

    Args:
        query: The user's query or prompt.
        system: An optional system prompt to guide the model's behavior.

    Returns:
        A GenerativeResult object containing the processed output.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    client = genai.Client(api_key=api_key)
    config = genai.types.GenerateContentConfig()

    if system:
        config.system_instruction = textwrap.dedent(system).strip()

    model_name = MODELS["gemini"]
    r = client.models.generate_content(model=model_name, contents=[query], config=config)
    return process_llm_response(r)

# --- Agent Wrapper ---

def agent(
    query: str,
    system: Optional[str] = None,
    agent_type: Literal["claude", "gemini", "deepseek", "openai"] = 'gemini',
    capture_code: bool = True,
    **kwargs: Any # To allow for future model-specific args
) -> GenerativeResult:
    """
    A wrapper function to call different LLM agents based on the specified type.

    Args:
        agent_type: The type of agent to use ('claude', 'gemini', 'deepseek', 'openai').
        query: The user's query or prompt.
        system: An optional system prompt.
        **kwargs: Additional keyword arguments (currently unused but allows future flexibility).

    Returns:
        A GenerativeResult object from the selected agent.

    Raises:
        ValueError: If an unsupported agent_type is provided.
        NotImplementedError: If the selected agent is not yet implemented.
    """
    if capture_code:
        system += '\n'
        # system += 'do not write notes or explanations. please focus on code.'
        system += 'be detailed and meticulous in the code you write.\ndo not write notes or explanations. focus on code'
    if agent_type == "claude":
        # Pass only query and system, ignore extra kwargs for now
        return claude(query=query, system=system)
    elif agent_type == "gemini":
        # Pass only query and system, ignore extra kwargs for now
        return gemini(query=query, system=system)
    elif agent_type == "deepseek":
        raise NotImplementedError("DeepSeek agent is not yet implemented.")
    elif agent_type == "openai":
        raise NotImplementedError("OpenAI agent is not yet implemented.")
    else:
        valid_agents = ["claude", "gemini", "deepseek", "openai"]
        raise ValueError(f"Invalid agent_type '{agent_type}'. Must be one of {valid_agents}")
