from transformers import pipeline
from pathlib import Path
import re


pipe = pipeline(
    "text-classification",
    model="ProsusAI/finbert"
)

def get_sentiment(texts):
    sentences = [s.strip() for s in re.split(r"[\n.!?]", texts) if s.strip()]

    sums = {"positive": 0, "negative": 0, "neutral": 0}
    for sentence in sentences:
        result = pipe(sentence)[0]
        sums[result['label']] += result['score']

    n = len(sentences)
    
    score = {}
    for k, v in sums.items():
        score[k] = v / n
    return score


if __name__ == "__main__":
    BASE = Path(__file__).parent
    f = ["sample1.txt", "sample2.txt"]
    files = [BASE / filename for filename in f]
    texts = []
    for i, filename in enumerate(files):
        texts.append({})
        with open(filename) as f:
            text = f.read()
            texts[i]["data"] = filename
            texts[i]["text"] = [line for line in text.splitlines() if line.strip() != ""]

    print(texts)
    score = get_sentiment(texts)
    print(score)

"""
[
    {
        "data": "sample1.txt",
        "text": [
            "aaaa",
            "bbbb"
        ]
    },
    {
        "data": "sample2.txt",
        "text": [
            "cccc",
            "dddd"
        ]
    }
]
"""
