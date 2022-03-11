import math
import unittest

import lightonmuse


class TestCreateEndpoint(unittest.TestCase):
    def test_single_prompt(self):
        # check types and single input
        output_keys = {'input_text', 'completions'}
        creator = lightonmuse.Create("orion-fr")
        sentence = "C'est quand même un truc magique, se dit le livreur, que d'avoir toujours"
        n_tokens = 16
        outputs, cost, rid = creator(sentence, n_tokens=n_tokens, seed=0, return_logprobs=True)
        assert isinstance(outputs, list), "`outputs` is not list as expected"
        assert len(outputs) == 1, f"`len(outputs) = {len(outputs)}` despite single input."
        assert cost['orion-fr@default']['total_tokens_generated'] == n_tokens, \
            f"`cost={cost['orion-fr@default']['total_tokens_generated']}` despite {n_tokens} tokens requested."
        assert isinstance(rid, str), f"Detected type {type(rid)} for `rid`, expected `str` instead."
        assert output_keys == \
               outputs[0].keys(), f"Set of keys is different than expected. Expected {output_keys}" \
                                  f"got {outputs[0].keys()} instead."
        assert outputs[0]["input_text"] == sentence, f"`text` field in `outputs` does not match the" \
                                                     f" input sentence."

        # check scores logic
        completion = outputs[0]["completions"][0]
        score, normalized_score = completion["score"]["logprob"], completion["score"]["normalized_logprob"]
        token_scores = [list(element.values())[0] for element in completion["score"]["token_logprobs"]]
        n_tokens = len(token_scores)
        assert len(token_scores) == n_tokens, f"Generated ({len(token_scores)}) but" \
                                              f"requested {n_tokens} tokens."
        assert score <= 0., f"Detected score > 0. This would give probability={math.exp(score)} " \
                            f"that is greater than 1."
        assert math.isclose(sum(token_scores), score), "The score does not match the sum of " \
                                                       "the token scores "
        assert math.isclose(normalized_score, score / n_tokens), f"Normalized score isn't close to " \
                                                                 f"score divided by number of tokens."

    def test_multiple_prompts(self):
        # check types and single input
        creator = lightonmuse.Create("orion-fr")
        sentence_list = ["C'est quand même un truc magique, se dit le livreur, que d'avoir toujours",
                         "L'avion avait soudain perdu de l'altitude, il penchait dangereusement"]
        n_tokens = 10
        outputs, cost, rid = creator(sentence_list, n_tokens=n_tokens, seed=0)
        assert isinstance(outputs, list), "`outputs` is not list as expected"
        assert len(outputs) == len(sentence_list), f"`len(outputs) = {len(outputs)}` despite " \
                                                   f"{len(sentence_list)} prompts."
        assert cost['orion-fr@default']['total_tokens_generated'] == n_tokens*len(sentence_list), \
            f"`cost={cost['orion-fr@default']['total_tokens_generated']}` despite {n_tokens} tokens for " \
            f"{len(sentence_list)} prompts requested."
        assert isinstance(rid, str), f"Detected type {type(rid)} for `rid`, expected `str` instead."
        assert outputs[1]["input_text"] == sentence_list[1], f"`text` field in `outputs` does not " \
                                                             f"match the input sentence."

    def test_multiple_outputs(self):
        creator = lightonmuse.Create("orion-fr")
        sentence = "C'est quand même un truc magique, se dit le livreur, que d'avoir toujours"
        n_tokens, n_completions, n_best = 16, 4, 2
        outputs, cost, rid = creator(sentence, n_tokens=n_tokens, seed=0,
                                     n_completions=n_completions, n_best=n_best)
        assert len(outputs[0]["completions"]) == n_best, f"Returned {len(outputs[0]['completions'])}" \
                                                         f"completions instead of {n_best}."
        assert cost['orion-fr@default']["total_tokens_generated"] == n_tokens * n_completions, \
            f"Cost={cost['orion-fr@default']['total_tokens_generated']} despite asking for {n_tokens} " \
            f"tokens for {n_completions} completions."

    def test_control(self):
        # word bias
        creator = lightonmuse.Create("orion-fr")
        sentence = "La ville de"
        n_tokens = 20
        outputs, cost, rid = creator(sentence, n_tokens=n_tokens, seed=0)
        assert "Biarritz" in outputs[0]["completions"][0]["output_text"], "Biarritz is not in the output" \
                                                                          "for unbiased call: " \
                                                                          + f'{outputs[0]["completions"][0]["output_text"]}'
        biases = {"Biarritz": -100., "Marseille": 5.5}
        frequency_penalty = 1.
        biased_outputs, cost, rid = creator(sentence, n_tokens=n_tokens, seed=1, word_biases=biases,
                                            frequency_penalty=frequency_penalty)
        biased_completion = biased_outputs[0]["completions"][0]["output_text"]
        assert "Paris" not in biased_completion, "Negatively biased word is in the output for " \
                                                 "biased call."
        assert "Marseille" in biased_completion, "Positively biased word is not in the output " \
                                                 "for biased call."
        assert biased_completion.count("Marseille") > 1, "Frequence penalized word appears more " \
                                                         "than one time."

        # stopword
        creator = lightonmuse.Create("orion-fr")
        sentence = "Je m'appelle Adrien"
        n_tokens = 50
        outputs, cost, rid = creator(sentence, n_tokens=n_tokens, seed=1, stop_words=["et"],
                                     concat_prompt=True)
        assert outputs[0]["completions"][0]["output_text"][-2:] == "et", f"Completion does not " \
                                                                         f"end with stopword"
        assert cost["orion-fr@default"]["total_tokens_generated"] < n_tokens, f"Cost is higher than expected given " \
                                                                              f"that generation ended at stopword."

    def test_utilities(self):
        # check reproducibility with the seed
        creator = lightonmuse.Create("orion-fr")
        sentence = "C'est quand même un truc magique, se dit le livreur, que d'avoir toujours"
        n_tokens = 16
        outputs1, _, _ = creator(sentence, n_tokens=n_tokens, seed=0, return_logprobs=True)
        outputs2, _, _ = creator(sentence, n_tokens=n_tokens, seed=0, return_logprobs=True)
        completion1 = outputs1[0]["completions"][0]["output_text"]
        completion2 = outputs2[0]["completions"][0]["output_text"]
        assert completion1 == completion2, "Completion was not reproduced by the same seed"

        # check tokens scores
        outputs, _, _ = creator(sentence, n_tokens=n_tokens, seed=0, return_logprobs=False)
        token_scores = outputs[0]["completions"][0]['score']["token_logprobs"]
        assert token_scores is None, f"Token scores is not None, despite not asking for logprobs."

        # check concat_prompt
        outputs, _, _ = creator(sentence, n_tokens=n_tokens, seed=0, return_logprobs=False,
                                concat_prompt=True)
        assert sentence in outputs[0]["completions"][0]["output_text"], "Input sentence not in the" \
                                                                        "output despite " \
                                                                        "`concat_prompt` set to True"


if __name__ == '__main__':
    unittest.main()
