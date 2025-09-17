from sentence_transformers import SentenceTransformer

model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")


def create_embedding(text: str) -> list[float]:
    embedding_array = model.encode(text)
    embedding_value = embedding_array.tolist()
    return embedding_value
