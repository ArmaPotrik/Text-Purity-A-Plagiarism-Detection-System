import numpy as np

def generate_text_embedding(self, text: str) -> np.ndarray:
    chunks = self.chunk_text(text)

    embeddings = []
    for chunk in chunks:
        emb = self.model.encode(chunk)
        embeddings.append(emb)

    # Average chunk embeddings
    final_embedding = np.mean(embeddings, axis=0)

    return np.asarray(final_embedding, dtype=np.float32)
