from transformers import pipeline
from pathlib import Path
from tqdm import tqdm
import re
import math


pipe = pipeline(
    "text-classification",
    model="ProsusAI/finbert",
    top_k=None,
    device=0
)

def get_sentiment(texts):
    sentences = [s.strip() for s in re.split(r"[\n.!?]", texts) if s.strip()]

    n = len(sentences)
    if n == 0:
        return {"positive": 0.0, "negative": 0.0, "neutral": 0.0}

    sums = {"positive": 0, "negative": 0, "neutral": 0}
    for sentence in sentences:
        result = pipe(sentence)[0]
        sums[result['label']] += result['score']
    
    score = {}
    for k, v in sums.items():
        score[k] = v / n
    return score


def process_all_articles(df):
    all_sentences = []
    boundaries = []
    for article in df.Article:
        sents = [s.strip() for s in re.split(r"[\n.!?]", str(article)) if s.strip()]
        start = len(all_sentences)
        all_sentences.extend(sents)
        boundaries.append((start, len(all_sentences)))

    results = list(
        tqdm(pipe((s for s in all_sentences), batch_size=64), total=len(all_sentences))
    )

    scores = []
    for start, end in boundaries:
        n = end - start
        if n == 0:
            scores.append({"positive": math.nan, "negative": math.nan, "neutral": math.nan})
            continue

        sums = {"positive": 0.0, "negative": 0.0, "neutral": 0.0}
        for r in results[start:end]:
            for d in r:
                sums[d["label"]] += d["score"]
        scores.append({k: v / n for k, v in sums.items()})
        
        

    return scores


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
