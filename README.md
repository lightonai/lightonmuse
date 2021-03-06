# <img src="https://muse.lighton.ai/img/logo.ed57408e.png" width=50/> lightonmuse

[![Twitter Follow](https://img.shields.io/twitter/follow/LightOnIO.svg?style=social)](https://twitter.com/LightOnIO)

Python bindings for the Muse API: production-ready intelligence primitives powered by state-of-the-art language models. By LightOn.

> Create. Process. Understand. Learn.

Uplift your product with the natural language generation & understanding capabilities of Muse. State-of-the-art large language models in French, English, Italian, and Spanish—with more to come—are just an API call away. Our models can help you build conversational AI, copywriting tools, text classifiers, semantic search, and more.

> 🛣️  Accessing the Muse API public beta
>
> The Muse API is currently in public beta. Learn more about Muse and sign up at [muse.lighton.ai](https://muse.lighton.ai/).

## Installation and documentation

You can install this package from PyPi with:

```bash
pip install lightonmuse
```

To install from source:

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

Guides and documentation can be found at the [API docs website](https://muse-docs.lighton.ai).

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

#### CalibratedSelect
```python
from lightonmuse import CalibratedSelect


selector = CalibratedSelect("orion-fr-v2")
selector.fit(
    content_free_inputs='Voici une critique : "" \n',
    candidates=["positive", "négative"],
    conjunction="Cette critique est"
)
critique = 'Voici une critique : "Ce film est super pour s\'endormir"'
print(selector(critique, candidates=["positive", "négative"], conjunction="Cette critique est"))
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

#### Tokenize

```python
from lightonmuse import Tokenize

tokenizer = Tokenize("lyra-en")
print(tokenizer("Let's discover how many tokens is this text"))
```

## Access to LightOn MUSE

Access the public beta of LightOn MUSE and try our intelligence primitives at [muse.lighton.ai](https://muse.lighton.ai/)
