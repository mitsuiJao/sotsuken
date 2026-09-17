import torch

print(torch.cuda.is_available())
print(torch.cuda.device_count())
print(torch.cuda.get_device_name(0))


from transformers import pipeline

pipe = pipeline(
    "text-classification",
    model="ProsusAI/finbert",
    device=0
)


print(pipe.model.device)
