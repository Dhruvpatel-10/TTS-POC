from blingfire import text_to_sentences
from typing import List, Tuple


                
def split_sentences(response: str) -> List[Tuple[int, str]]:
    sentences = text_to_sentences(response).split("\n")
    clean_sentences = [s.strip() for s in sentences if s.strip()]
    return list(enumerate(clean_sentences))