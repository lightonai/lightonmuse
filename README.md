# <img src="https://muse.lighton.ai/images/logo/lighton_logo.png" width=80/> lightonmuse

[![Twitter Follow](https://img.shields.io/twitter/follow/LightOnIO.svg?style=social)](https://twitter.com/LightOnIO)

Python bindings to production-ready intelligence primitives powered by state-of-the-art language models. 

> Create. Process. Understand. Learn.

Uplift your product with the natural language generation & understanding capabilities of Muse. State-of-the-art large language models in French, English, Italian, and Spanish—with more to come—are just an API call away. Our models can help you build conversational AI, copywriting tools, text classifiers, semantic search, and more.

> 🔒 Accessing the Muse API private beta
>
> The Muse API is currently in private beta for select customers. You can [register your interest](https://lightonmuse.typeform.com/waitlist), and we will keep you updated regarding our public launch. Stay tuned: public access is coming early 2022.

Learn more about [Muse](https://muse.lighton.ai/).

## Installation and documentation


To install:

```bash
git clone https://github.com/lightonai/lightonmuse.git
cd lightonmuse
pip install ./
```

Once the package is installed, make sure to define an environment variable
`MUSE_API_KEY` to your API key, e.g. by adding the following line to your `.bashrc`

```
export MUSE_API_KEY="<your api key>"
```

Guides and documentation can be found at the [API docs website](https://muse.lighton.ai/docs/).

## Quickstart

Using `lightonmuse` is pretty simple, the interface matches the endpoints offered by the Muse API

#### Create
```python
from lightonmuse import Create


creator = Create("lyra-en")
print(creator("Wow, the Muse API is really amazing"))
```

#### Select
```python
from lightonmuse import Select


selector = Select("orion-fr-v2")
print(selector("Quel nom est correct?", candidates=["pain au chocolat", "chocolatine"]))
```

#### Analyse
```python
from lightonmuse import Analyse

analyser = Analyse("orion-fr-v2")
print(analyser("Avec \"Analyse\" on peut toujours trouver les parties plus surprenantes d'une phrase."))
```

#### Embed
```python
from lightonmuse import Embed

embedder = Embed("lyra-en")
print(embedder("This sentence will be transformed in a nice matrix of numbers."))
```

#### Compare
```python
from lightonmuse import Compare

comparer = Compare("lyra-en")
print(comparer("This is the reference.", candidates=["This is close to the reference", "While this is most definitely not"]))
```

## Private Beta access to LightOn MUSE

To request access to LightOn MUSE in private beta and try our intelligence primitives, get in touch: customer.relations@lighton.ai
