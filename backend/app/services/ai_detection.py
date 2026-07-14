from typing import Dict, Any


class AIDetectionService:

    def __init__(self):
        self.enabled = True

    def detect(self, text: str) -> Dict[str, Any]:
        """
        Enhanced lightweight AI detection (heuristic-based).
        """

        if not text:
            return {
                "is_ai": False,
                "score": 0.0,
                "confidence": 0.0,
                "label": "UNKNOWN",
                "message": "No text provided"
            }

        word_count = len(text.split())
        sentence_count = max(text.count("."), 1)
        avg_sentence_length = word_count / sentence_count

        ai_phrases = [
            "in conclusion",
            "moreover",
            "furthermore",
            "in addition",
            "significantly",
            "overall",
            "it is important to note",
        ]

        phrase_score = sum(
            1 for phrase in ai_phrases if phrase in text.lower()
        )

        score = (
            (word_count / 500) * 0.4 +
            (avg_sentence_length / 20) * 0.3 +
            (phrase_score / 5) * 0.3
        )

        score = min(score, 1.0)
        is_ai = score > 0.5

        return {
            "is_ai": is_ai,
            "score": round(score, 2),
            "confidence": round(score, 2),
            "label": "AI" if is_ai else "Human",
            "message": "Enhanced heuristic detection"
        }
