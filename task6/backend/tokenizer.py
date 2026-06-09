# backend/tokenizer.py
# Custom subword BPE-style tokenizer that simulates SentencePiece.
# Avoids external compiled dependencies on Windows.

import re
import hashlib
from typing import List, Dict, Any

# Common prefixes and suffixes to simulate subword tokenization
PREFIXES = [
    "anti", "auto", "co", "de", "dis", "down", "extra", "fore", "hyper", 
    "ill", "im", "in", "infra", "inter", "intra", "macro", "micro", "mid", 
    "mis", "mono", "multi", "non", "over", "post", "pre", "pro", "re", 
    "semi", "sub", "super", "trans", "ultra", "un", "under", "up"
]

SUFFIXES = [
    "ation", "tional", "ing", "ely", "est", "ful", "less", "able", "ible", 
    "ment", "ness", "tion", "sion", "ance", "ence", "ship", "hood", "ward", 
    "wise", "ized", "ise", "ize", "ed", "ly", "es", "er", "al", "ic", "ty", 
    "us", "ts", "on", "in", "at", "as", "or", "an"
]

def get_token_id(token_text: str) -> int:
    """Generates a stable, unique integer ID for a token based on its text."""
    # Use MD5 to get a stable hash value between 1000 and 50000
    h = hashlib.md5(token_text.encode('utf-8')).hexdigest()
    return (int(h[:6], 16) % 49000) + 1000

def tokenize_text(text: str) -> List[Dict[str, Any]]:
    """
    Tokenizes text into a list of token dicts.
    Each dict contains:
      - text: str (the text of the token)
      - id: int (token ID)
      - color_index: int (0-5, cyclic index for styling)
      - start: int (start char index)
      - end: int (end char index)
    """
    if not text:
        return []

    # Regex to split:
    # Group 1: Whitespace sequence (spaces, tabs, newlines)
    # Group 2: Alphabetic word sequence
    # Group 3: Numeric sequence
    # Group 4: Individual punctuation/other characters
    pattern = re.compile(r"(\s+)|([a-zA-Z]+)|(\d+)|([^\w\s])")
    matches = list(pattern.finditer(text))
    
    raw_tokens = []
    
    for match in matches:
        val = match.group(0)
        start, end = match.span()
        
        # If it's an alphabetic word, we attempt subword splitting
        if match.group(2):
            word = val
            word_len = len(word)
            
            # Simple rule-based greedy subword splits
            if word_len > 4:
                split_done = False
                
                # Check for prefix split
                for pfx in PREFIXES:
                    if word.lower().startswith(pfx) and len(word) > len(pfx) + 2:
                        raw_tokens.append((pfx, start, start + len(pfx)))
                        word = word[len(pfx):]
                        start += len(pfx)
                        split_done = True
                        break
                
                # Check for suffix split
                for sfx in SUFFIXES:
                    if word.lower().endswith(sfx) and len(word) > len(sfx) + 2:
                        body = word[:-len(sfx)]
                        body_end = start + len(body)
                        
                        # Can we split body further if it is long?
                        if len(body) > 4:
                            mid = len(body) // 2
                            raw_tokens.append((body[:mid], start, start + mid))
                            raw_tokens.append((body[mid:], start + mid, body_end))
                        else:
                            raw_tokens.append((body, start, body_end))
                            
                        raw_tokens.append((sfx, body_end, end))
                        split_done = True
                        break
                
                if not split_done:
                    # No prefix/suffix matched, if word is very long split in half
                    if word_len > 7:
                        mid = word_len // 2
                        raw_tokens.append((word[:mid], start, start + mid))
                        raw_tokens.append((word[mid:], start + mid, end))
                    else:
                        raw_tokens.append((word, start, end))
            else:
                raw_tokens.append((word, start, end))
        else:
            # Whitespace, numbers, or punctuation: keep intact
            # But if there are newlines, we split them individually so we can preserve format
            if "\n" in val:
                curr_pos = start
                for char in val:
                    raw_tokens.append((char, curr_pos, curr_pos + 1))
                    curr_pos += 1
            else:
                raw_tokens.append((val, start, end))

    # Convert raw tokens to structured dicts with stable IDs and color indices
    structured_tokens = []
    color_counter = 0
    for idx, (t_text, t_start, t_end) in enumerate(raw_tokens):
        # Assign a cyclic color index for visual rendering
        # Spaces and newlines are not highlighted with background, but we keep the color index
        color_idx = color_counter
        if not t_text.isspace():
            color_counter = (color_counter + 1) % 6
            
        structured_tokens.append({
            "text": t_text,
            "id": get_token_id(t_text),
            "color_index": color_idx,
            "start": t_start,
            "end": t_end
        })
        
    return structured_tokens

# Simple CLI test
if __name__ == "__main__":
    test_str = "Hello, world! Tokenization is absolutely cool."
    res = tokenize_text(test_str)
    print(f"Text: '{test_str}'")
    print(f"Token count: {len(res)}")
    for t in res:
        print(f"  Token: {repr(t['text'])}, ID: {t['id']}, Color Index: {t['color_index']}")
