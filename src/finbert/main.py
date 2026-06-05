from transformers import pipeline
from pathlib import Path

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

pipe = pipeline(
    "text-classification",
    model="ProsusAI/finbert"
)

for d in texts:
    sums = {"positive": 0, "negative": 0, "neutral": 0}
    for sentence in d["text"]:
        result = pipe(sentence)[0]
        sums[result['label']] += result['score']
        
        # print(f"{result['label']:8} ({result['score']:.2f})  {sentence}")
    
    print(d["data"])
    print(sums)
    score = {"positive": 0, "negative": 0, "neutral": 0}
    n = len(d["text"])
    
    for i in sums.keys():
        score[i] = sums[i] / n
    print(score)
    print()


# {'label': 'negative', 'score': 0.6651697754859924}

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
