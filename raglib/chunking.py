def chunk_text(text: str, chunk_size: int = 1200, overlap: int = 200):
    text = text.replace("\r\n", "\n")
    out = []
    i = 0
    step = max(1, chunk_size - overlap)
    while i < len(text):
        c = text[i:i+chunk_size].strip()
        if c:
            out.append(c)
        i += step
    return out