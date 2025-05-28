from datasets import load_dataset
import pandas as pd
# Load the dataset from Hugging Face
dataset = load_dataset("vblagoje/PubMedQA_instruction", split="train")
print(dataset.shape)

print(dataset[:3])

