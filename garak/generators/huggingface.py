#!/usr/bin/env python3

import logging
import re
import warnings


from garak._config import args
from garak.generators.base import Generator


models_to_deprefix = ["gpt2"]


class HFGenerator(Generator):
    def __init__(self, name, do_sample=True, generations=10, device=0):
        self.fullname, self.name = name, name.split("/")[-1]

        self.generator_family_name = "Hugging Face 🤗"
        super().__init__(name)

        from transformers import pipeline, set_seed

        set_seed(args.seed)

        logging.info("generator init: {self}")
        import torch.cuda

        if torch.cuda.is_available() == False:
            logging.debug("Using CPU, torch.cuda.is_available() returned False")
            device = -1

        self.generator = pipeline(
            "text-generation",
            model=name,
            do_sample=do_sample,
            device=device,
        )
        self.deprefix_prompt = name in models_to_deprefix
        self.max_new_tokens = 256

    def generate(self, prompt):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", category=UserWarning)
            try:
                raw_output = self.generator(
                    prompt,
                    pad_token_id=self.generator.tokenizer.eos_token_id,
                    max_new_tokens=self.max_new_tokens,
                    num_return_sequences=self.generations,
                    # max_length = 1024,
                )
            except:
                raw_output = []  # could handle better than this..
        generations = [
            i["generated_text"] for i in raw_output
        ]  # generator returns 10 outputs by default in __init__
        if not self.deprefix_prompt:
            return generations
        else:
            return [re.sub("^" + re.escape(prompt), "", i) for i in generations]


default_class = "HFGenerator"
