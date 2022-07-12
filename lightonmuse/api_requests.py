import json
import os
from typing import Dict, List, Optional, Tuple, Union
import warnings

import requests


class BaseRequest:
    def __init__(self, model: str, endpoint: str):
        # can target different environments with `MUSE_BASE_URL`
        _base_url = os.environ.get("MUSE_BASE_URL")
        if _base_url is not None:
            self._base_url = _base_url
            # because sometimes a lazy copy-paste gets to be annoying
            if _base_url[-1] != "/":
                _base_url = _base_url + "/"
            warnings.warn(f"Bindings targeting {self._base_url}")
        else:
            # if no env variable is set, target the API
            self._base_url = "https://api.lighton.ai/muse/v1/"
        self.url = self._base_url + endpoint
        self.accept = "application/json"
        self.api_key = os.environ.get("MUSE_API_KEY")
        if self.api_key is None:
            raise RuntimeError("No API key was detected. Set your API key by running"
                               "`export MUSE_API_KEY=<YOUR-API-KEY> from the terminal.`")
        self.model = model
        self.content_type = "application/json"

    @property
    def headers(self) -> dict:
        return {'accept': self.accept, 'X-API-KEY': self.api_key,
                'X-Model': self.model, 'Content-Type': self.content_type}

    def request(self, payload) -> dict:
        response = requests.post(self.url, data=payload, headers=self.headers)
        if response.ok:
            return response.json()
        else:
            raise RuntimeError(f"The request failed with status code {response.status_code}: "
                               f"{response.content.decode('utf-8')}")


class Create(BaseRequest):
    """Create endpoint.

    Parameters
    ----------
    model: str,
        name of the model to use as intelligence engine.
        Currently supports `"orion-fr-v2"` and `"lyra-en"`.
    """
    def __init__(self, model: str = "orion-fr-v2"):
        super().__init__(model=model, endpoint="create")

    def __call__(self, text: Union[str, List[str]],
                 skill: Optional[str] = None,
                 n_tokens: int = 20,
                 n_completions: int = 1,
                 n_best: int = 1,
                 # sampling
                 mode: str = "nucleus",
                 temperature: float = 1,
                 p: float = 0.9,
                 k: int = 5,
                 # control
                 word_biases: Optional[Dict[str, float]] = None,
                 presence_penalty: float = 0.,
                 frequency_penalty: float = 0.,
                 stop_words: Optional[List[str]] = None,
                 # utilities
                 concat_prompt: bool = False,
                 return_logprobs: bool = False,
                 seed: Optional[int] = None
                 ) -> Tuple[List, int, str]:
        """
        Parameters
        -------------
        text: Union[str, List[str]],
            input prompt or list of input prompts.
        skill: Optional[str], default None,
            condition the model to perform a certain task. May be `"summarization"`.
        n_tokens: int, default 20,
            number of tokens to generate.
        n_completions: int, default 1,
            number of different completion proposals to return for each prompt.
            :warning: You will be charged for the total number of tokens generated:
            `n_completions * n_tokens`, stay reasonable!
        n_best: int, default 1,
            only return the `best_of` among `n_completions`. Completions are selected
            according to how likely they are, summing the log-likelihood over all tokens generated.
        # sampling
        mode: str, default "nucleus",
            how the model will decide which token to select at each step. Choose between:
            - `"greedy"`: the model will always select the most likely token. This generation mode
            is deterministic and only suited for applications in which there is a ground truth the
            model is expected to return (e.g. question answering).
            - `"nucleus"`: the model will only consider the most likely tokens with total
            probability mass p. We recommend this setting for most applications.
            - `"topk"`: the model will only consider the k most likely tokens.
            - `"typical"`: the model will discard high probability tokens with low expected information content.
        temperature: float, default 1.,
            controls how risky will the model be in its choice of tokens. A temperature of 0
            corresponds to greedy sampling; we recommend a value around 1 for most creative
            applications, and closer to 0 when a ground truth exists.
        p: float, default 0.9,
            total probability mass of the most likely tokens considered when sampling in
            nucleus mode.
        k: int, default 5,
            number of most likely tokens considered when sampling in top-k mode.
        # control
        word_biases: Optional[Dict[str, float]], default None,
            bias the provided words to appear more or less often in the generated text. Values
            should be comprised between -100 and +100, with negative values making words more
            unlikely to occur. Extreme values such as -100 will completely forbid a word,
            while values between 1-5 will make the word more likely to appear. We recommend playing
            around to find a good fit for your use case. We recommend using presence and frequency
            penalty when positively biasing words.
        presence_penalty: float, default 0.,
            How strongly should tokens be prevented from appearing again. This is a one-off penalty:
            tokens will be penalized after their first appearance, but not more if they appear
            repetitively -- use `frequency_penalty` if that's what you want instead.
            Values closer to 1 encourage variation of the topics generated.
        frequency_penalty: float, default 0.,
            How strongly should tokens be prevented from appearing again if they have appeared
            repetitively. Contrary to presence_penalty, this penalty scales with how often the
            token already occurs. Values closer to 1 discourage repetition, especially useful in
            combination with `word_biases`.
        stop_words: Optional[List[str]], default None,
            encountering any of the words in this list will halt generation immediately.
        # utilities
        concat_prompt: bool, default False,
            whether the original prompt will be concatenated with the generated text.
        return_logprobs: int, default 0,
            whether the log-probabilities of the generated tokens are returned.
        seed: Optional[int], default None,
            make sampling deterministic by setting a seed used for random number generation.
            Useful to perfectly reproduce `Create` calls.

        Return
        ------
        outputs: list,
            list of dicts containing the completions for the input `text`, together with scores
            and other metadata.
        cost: int,
            cost for the generation completed.
        request_id: str,
            ID string for the request.
        """
        if mode not in ["greedy", "topk", "nucleus", "typical"]:
            raise ValueError(f"mode: {mode} is not valid. Use one of `greedy`, `topk`, `nucleus` or `typical`")
        params = {"n_tokens": n_tokens, "skill": skill, "n_completions": n_completions, "n_best": n_best,
                  # sampling
                  "mode": mode, "temperature": temperature, "p": p, "k": k,
                  # control
                  "biases": word_biases, "presence_penalty": presence_penalty,
                  "frequence_penalty": frequency_penalty, "stop_words": stop_words,
                  # utilities
                  "concat_prompt": concat_prompt, "return_logprobs": return_logprobs, "seed": seed
                  }
        payload = json.dumps({"text": text, "params": params})
        response = self.request(payload)
        request_id = response["request_id"]
        cost = response["costs"]
        outputs = response["outputs"][0]
        return outputs, cost, request_id


class Analyse(BaseRequest):
    """Analyse endpoint.

    Parameters
    ----------
    model: str,
        name of the model to use as intelligence engine.
        Currently supports only `"orion-fr-v2"` and `"lyra-en"`.
    """
    def __init__(self, model: str = "orion-fr-v2"):
        super().__init__(model=model, endpoint="analyse")

    def __call__(self, text: Union[str, List[str]], skill: Optional[str] = None) -> Tuple[List, int, str]:
        """Parameters
        -------------
        text: Union[str, List[str]],
            input text or list of input texts.
        skill: Optional[str], default None,
            condition the model to perform a certain task. May be `"summarization"`.

        Return
        ------
        outputs: list,
            list of dicts containing the input `text`(s), together with scores
            and other metadata.
        cost: int,
            cost for the analysis completed.
        request_id: str,
            ID string for the request.
        """
        payload = json.dumps({"text": text})
        response = self.request(payload)
        request_id = response["request_id"]
        cost = response["costs"]
        outputs = response["outputs"][0]
        return outputs, cost, request_id


class Embed(BaseRequest):
    """Embed endpoint.

    Parameters
    ----------
    model: str,
        name of the model to use as intelligence engine.
        Currently supports only `"orion-fr-v2"` and `"lyra-en"`.
    """
    def __init__(self, model: str = "orion-fr-v2"):
        super().__init__(model=model, endpoint="embed")

    def __call__(self, text: Union[str, List[str]], skill: Optional[str] = None) -> Tuple[List, int, str]:
        """Parameters
        -------------
        text: Union[str, List[str]],
            input text or list of input texts.
        skill: Optional[str], default None,
            condition the model to perform a certain task. May be `"summarization"`.

        Return
        ------
        outputs: list,
            list of dicts containing the input `text`(s), together with embeddings
            and other metadata.
        cost: int,
            cost for the analysis completed.
        request_id: str,
            ID string for the request.
        """
        payload = json.dumps({"text": text})
        response = self.request(payload)
        request_id = response["request_id"]
        cost = response["costs"]
        outputs = response["outputs"][0]
        return outputs, cost, request_id


class Select(BaseRequest):
    """Select endpoint.

    Parameters
    ----------
    model: str,
        name of the model to use as intelligence engine.
        Currently supports only `"orion-fr-v2"` and `"lyra-en"`.
    """
    def __init__(self, model: str = "orion-fr-v2"):
        super().__init__(model=model, endpoint="select")

    def __call__(self, reference: str, candidates: List[str],
                 evaluate_reference: bool = False,
                 conjunction: str = None, skill: Optional[str] = None,
                 concat_best: bool = False) -> Tuple[List, int, str]:
        """Parameters
        -------------
        reference: str,
            reference input to compute likelihood against.
        candidates: List[str],
            input(s) that are compared to the reference and ranked based on likelihood.
        evaluate_reference: bool, default to False,
            if True, evaluates the loglikelihood of candidate given reference,
            instead of reference given candidates. Especially useful when candidates
            have very different lengths.
        conjunction: str, default to None,
            expression used to link `reference` and `candidates` to create the prompt used to
            compute the likelihood. The prompt will have the structure
            `reference + conjunction + candidate`. Finding a good conjunction can greatly increase
            the performance of `Select`.
        skill: Optional[str], default None,
            condition the model to perform a certain task. May be `"summarization"`.
        concat_best: bool, default to False,
            whether the response will contain a "best" field with the selected choice.

        Return
        ------
        outputs: list,
            list of dicts containing the reference text, the rankings of the candidates together
            with their scores and other metadata.
        cost: int,
            cost for the analysis completed.
        request_id: str,
            ID string for the request.
        """
        payload = json.dumps({"reference": reference, "candidates": candidates,
                              "evaluate_reference": evaluate_reference,
                              "conjunction": conjunction, "skill": skill, "concat_best": concat_best})
        response = self.request(payload)
        request_id = response["request_id"]
        cost = response["costs"]
        outputs = response["outputs"][0]
        return outputs, cost, request_id


class Compare(BaseRequest):
    """Compare endpoint.

    Parameters
    ----------
    model: str,
        name of the model to use as intelligence engine.
        Currently supports only `"orion-fr-v2"` and `"lyra-en"`.
    """
    def __init__(self, model: str = "orion-fr-v2"):
        super().__init__(model=model, endpoint="compare")

    def __call__(self, reference: str, candidates: List[str], skill: Optional[str] = None) -> Tuple[List, int, str]:
        """Parameters
        -------------
        reference: str,
            reference input to compute cosine similarity against.
        candidates: List[str],
            input(s) that are compared to the reference and ranked based on similarity.
        skill: Optional[str], default None,
            condition the model to perform a certain task. May be `"summarization"`.

        Return
        ------
        outputs: list,
            list of dicts containing the reference text, the rankings of the candidates together
            with their scores and other metadata.
        cost: int,
            cost for the analysis completed.
        request_id: str,
            ID string for the request.
        """
        payload = json.dumps({"reference": reference, "candidates": candidates})
        response = self.request(payload)
        request_id = response["request_id"]
        cost = response["costs"]
        outputs = response["outputs"][0]
        return outputs, cost, request_id


class Tokenize(BaseRequest):
    """Tokenize endpoint.

    Parameters
    ----------
    model: str,
        name of the model to use as intelligence engine.
        Currently supports only `"orion-fr-v2"` and `"lyra-en"`.
    """
    def __init__(self, model: str = "orion-fr-v2"):
        super().__init__(model=model, endpoint="tokenize")

    def __call__(self, text: Union[str, List[str]]) -> Tuple[List, int, str]:
        """Parameters
        -------------
        text: Union[str, List[str]],
            input text or list of input texts.

        Return
        ------
        outputs: list,
            list of dicts containing the reference text, the rankings of the candidates together
            with their scores and other metadata.
        cost: int,
            cost for the analysis completed.
        request_id: str,
            ID string for the request.
        """
        payload = json.dumps({"text": text})
        response = self.request(payload)
        request_id = response["request_id"]
        cost = response["costs"]
        outputs = response["outputs"][0]
        return outputs, cost, request_id
