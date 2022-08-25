from dataclasses import dataclass


@dataclass
class Resources:
    models = [
        "orion-fr",
        "lyra-fr",
        "orion-en",
        "lyra-en",
        "orion-ar",
        "lyra-ar",
        "auriga-de",
        "auriga-es",
        "auriga-it",
    ]
    skills = [
        "orion-fr@summarisation",
        "lyra-en@multitask",
        "auriga-de@zusammenfassung",
        "auriga-es@resumen",
    ]
