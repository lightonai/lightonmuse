from dataclasses import dataclass


@dataclass
class Resources:
    models = ["orion-fr", "orion-fr-v2", "lyra-en"]
    skills = ["orion-fr@summarisation"]
