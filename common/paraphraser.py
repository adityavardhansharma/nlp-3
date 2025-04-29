import torch
from transformers import T5ForConditionalGeneration, T5Tokenizer
from common.config import PARAPHRASE_MODEL

class Paraphraser:
    def __init__(self):
        self.tokenizer = T5Tokenizer.from_pretrained(PARAPHRASE_MODEL)
        self.model = T5ForConditionalGeneration.from_pretrained(PARAPHRASE_MODEL)
        # if you want GPU:
        # self.model.to("cuda")

    def paraphrase(self, text: str, num_beams: int = 4) -> str:
        prompt = f"paraphrase: {text}"
        inputs = self.tokenizer(
            prompt,
            max_length=256,
            truncation=True,
            return_tensors="pt"
        )
        # inputs = {k: v.to("cuda") for k,v in inputs.items()}
        out = self.model.generate(
            **inputs,
            max_length=256,
            num_beams=num_beams,
            early_stopping=True
        )
        return self.tokenizer.decode(out[0], skip_special_tokens=True)
