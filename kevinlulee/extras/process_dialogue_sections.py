import re
from dataclasses import dataclass


@dataclass
class DialogueSection:
    text: str
    speaker: str
    # style: str



def process_dialogue_sections(sections: list[DialogueSection]) -> list[DialogueSection]:
    all_speakers = {section.speaker for section in sections}
    
    for i, section in enumerate(sections):
        prev_speaker = sections[i - 1].speaker if i > 0 else None
        next_speaker = sections[i + 1].speaker if i < len(sections) - 1 else None
        everyone_else = ", ".join(s for s in all_speakers if s != section.speaker)
        
        if re.search(r"\$prev", section.text):
            assert prev_speaker is not None, "Cannot reference $prev in the first section"
        
        if re.search(r"\$next", section.text):
            assert next_speaker is not None, "Cannot reference $next in the last section"
        
        section.text = re.sub(r"\$prev", prev_speaker, section.text)
        section.text = re.sub(r"\$(?=[,.! ])", prev_speaker, section.text)
        section.text = re.sub(r"\$next", next_speaker, section.text)
        section.text = re.sub(r"\$everyone", everyone_else, section.text)
        section.text = re.sub(r"\$self", section.speaker, section.text)
    
    return sections

from kevinlulee.extras.extract_frontmatter import extract_frontmatter
