# app/services/plagiarism.py

import uuid
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from typing import List
from app.models.document import Document
from app.models.comparison import Comparison


class PlagiarismService:

    @staticmethod
    def compare_documents(documents: List[Document]) -> List[Comparison]:
        if len(documents) < 2:
            return []

        texts = [doc.text_content or "" for doc in documents]

        # TF-IDF Vectorization
        vectorizer = TfidfVectorizer(
            stop_words="english",
            lowercase=True
        )
        tfidf_matrix = vectorizer.fit_transform(texts)

        # Cosine Similarity Matrix
        similarity_matrix = cosine_similarity(tfidf_matrix)

        comparisons = []

        for i in range(len(documents)):
            for j in range(i + 1, len(documents)):

                similarity_score = similarity_matrix[i][j] * 100

                comparison = Comparison(
    id=uuid.uuid4(),                          # REAL UUID
    batch_id=documents[i].batch_id,           # REAL UUID
    doc_a=documents[i].id,                    # REAL UUID
    doc_b=documents[j].id,                    # REAL UUID
    similarity=round(float(similarity_score), 2),
    details={"method": "tfidf_cosine"}
)

                comparisons.append(comparison)

        return comparisons
