from typing import List, Tuple
from .config import RELEVANCE_MAX_DISTANCE

def is_relevant(rows: List[Tuple[int, str, float]]) -> bool:
    if not rows:
        return False
    best_dist = rows[0][2]
    return best_dist <= RELEVANCE_MAX_DISTANCE