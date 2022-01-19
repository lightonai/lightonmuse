import math
import unittest

import lightonmuse


class TestUnderstandEndpoints(unittest.TestCase):
    def test_analyse(self):
        # check types and single input
        output_keys = {'execution_metadata', 'text', 'score'}
        analyser = lightonmuse.Analyse("orion-fr")
        sentence = "Je voudrais un café et deux croissants, s'il vous plait."
        outputs, cost, rid = analyser(sentence)
        assert isinstance(outputs, list), "`outputs` is not list as expected"
        assert len(outputs) == 1, f"`len(outputs) = {len(outputs)}` despite single input."
        assert cost["orion-fr@default"]["batch_size"] == 1, f"`batch_size={cost['orion-fr@default']['batch_size']}` " \
                                                            f"despite single Analyse call."
        assert isinstance(rid, str), f"Detected type {type(rid)} for `rid`, expected `str` instead."
        assert output_keys == \
               outputs[0].keys(), f"Set of keys is different than expected. Expected {output_keys}" \
                                  f"got {outputs[0].keys()} instead."
        assert outputs[0]["text"] == sentence, f"`text` field in `outputs` does not match the" \
                                               f" input sentence."
        score, normalized_score = outputs[0]["score"]["logprob"], outputs[0]["score"]["normalized_logprob"]
        n_tokens = len(outputs[0]["score"]["token_logprobs"])
        assert score <= 0., f"Detected score > 0. This would give probability={math.exp(score)} " \
                            f"that is greater than 1."
        assert math.isclose(normalized_score, score/n_tokens), f"Normalized score isn't close to " \
                                                               f"score divided by number of tokens."

        # check list of inputs
        unlikely_sentence = "Bonjour Madame, vous allez parachute"
        sentence_list = [sentence, unlikely_sentence]
        outputs, cost, rid = analyser(sentence_list)
        assert isinstance(outputs, list), "`outputs` is not list as expected"
        assert len(outputs) == len(sentence_list), f"`len(outputs) = {len(outputs)}` despite " \
                                                   f"len(input)={len(sentence_list)}"
        assert cost["orion-fr@default"]["batch_size"] == len(sentence_list), \
            f"`cost={cost['orion-fr@default']['batch_size']}` despite len(input)={len(sentence_list)}"
        assert isinstance(rid, str), f"Detected type {type(rid)} for `rid`, expected `str` instead."

        # check correct functioning
        message = "The unlikely sentence is more likely than the normal one."
        assert outputs[0]["score"]["normalized_logprob"] > outputs[1]["score"]["normalized_logprob"], f"{message}"
        token_scores = [list(element.values())[0] for element in outputs[1]["score"]["token_logprobs"]]
        message = f"The most unlikely token is different than expected."
        assert math.isclose(min(token_scores), token_scores[-1]), f"{message}"

    def test_embed(self):
        # check types and single input
        output_keys = {'execution_metadata', 'text', 'embedding'}
        representer = lightonmuse.Embed("orion-fr")
        sentence = "Je voudrais un café et deux croissants, s'il vous plait."
        outputs, cost, rid = representer(sentence)
        assert isinstance(outputs, list), "`outputs` is not list as expected"
        assert len(outputs) == 1, f"`len(outputs) = {len(outputs)}` despite single input."
        assert cost['orion-fr@default']['batch_size'] == 1, \
            f"`cost={cost['orion-fr@default']['batch_size']}` despite single Represent call."
        assert isinstance(rid, str), f"Detected type {type(rid)} for `rid`, expected `str` instead."
        assert output_keys == \
               outputs[0].keys(), f"Set of keys is different than expected. Expected {output_keys}" \
                                  f"got {outputs[0].keys()} instead."
        assert outputs[0]["text"] == sentence, f"`text` field in `outputs` does not match the" \
                                               f" input sentence."
        embedding = outputs[0]["embedding"]
        assert isinstance(embedding, list)
        assert len(embedding) == 1600, f"Shape of the embedding is {len(embedding)}!=1600 " \
                                       f"expected for `orion-fr`."

        # test multiple inputs
        sentence_list = [sentence, "quelque chose dans cette liste"]
        outputs, cost, rid = representer(sentence_list)
        assert isinstance(outputs, list), "`outputs` is not list as expected"
        assert len(outputs) == len(sentence_list), f"`len(outputs) = {len(outputs)}` despite " \
                                                   f"len(input)={len(sentence_list)}"
        assert cost["orion-fr@default"]["batch_size"] == len(sentence_list), \
            f"`batch size={cost['orion-fr@default']['batch_size']}` despite len(input)={len(sentence_list)}"
        assert isinstance(rid, str), f"Detected type {type(rid)} for `rid`, expected `str` instead."

        first_embedding, second_embedding = outputs[0]["embedding"], outputs[1]["embedding"]
        assert len(first_embedding) == len(second_embedding), f"Shape of the embeddings differ" \
                                                              f"{len(first_embedding)}!=" \
                                                              f"{len(second_embedding)}."

    def test_select(self):
        # TODO: fix output_keys when concat_best is implemented in Select upstream
        output_keys = {"reference", "rankings", "best", "execution_metadata"}
        selecter = lightonmuse.Select("orion-fr")
        reference = "Aujourd'hui il fait beau"
        correct, wrong = "Il y a du soleil", "Il fait moche"
        candidates = [correct, wrong]
        outputs, cost, rid = selecter(reference, candidates)
        assert isinstance(outputs, list), "`outputs` is not list as expected"
        assert len(outputs) == 1, f"`len(outputs) = {len(outputs)}` despite single reference."
        assert cost["orion-fr@default"]["batch_size"] == len(candidates), \
            f"`batch size={cost['orion-fr@default']['batch_size']}` despite {len(candidates)} candidates."
        assert isinstance(rid, str), f"Detected type {type(rid)} for `rid`, expected `str` instead."
        assert output_keys == \
               outputs[0].keys(), f"Set of keys is different than expected. Expected " \
                                  f"{output_keys} got {outputs[0].keys()} instead."
        assert outputs[0]["reference"] == reference, f"`reference` field in `outputs` does not " \
                                                     f"match the input `reference` sentence."
        # TODO: update this when concat_best is implemented in Select upstream
        assert outputs[0]["best"] == correct

        rankings = outputs[0]["rankings"]
        assert len(rankings) == len(candidates), f"Got {len(rankings)}  elements in rankings " \
                                                 f"while {len(candidates)} candidates were given."

        scores = [element["score"]["logprob"] for element in rankings]
        normalized_scores = [element["score"]["normalized_logprob"] for element in rankings]
        n_tokens = [len(element["score"]["token_logprobs"]) for element in rankings]
        message = f"Normalized score isn't close to score divided by number of tokens."
        assert all([math.isclose(ns, s/n)]
                   for s, ns, n in zip(scores, normalized_scores, n_tokens)), message
        assert all([s <= 0. for s in scores]), f"Detected score > 0. This would give " \
                                               f"a probability that is greater than 1."

        # check that tuned conjunction improves the score
        best_score_no_conj = max(normalized_scores)
        conjunction = "est equivalent à"
        outputs, cost, rid = selecter(reference, candidates, conjunction=conjunction)
        rankings = outputs[0]["rankings"]
        normalized_scores = [element["score"]["normalized_logprob"] for element in rankings]
        best_score_with_conj = max(normalized_scores)
        assert best_score_with_conj > best_score_no_conj, f"Conjunction `{conjunction}` does not" \
                                                          f"improve the score."

    def test_compare(self):
        output_keys = {"reference", "similarities", "best", "execution_metadata"}
        comparer = lightonmuse.Compare("orion-fr")
        reference = "Je suis content"
        correct, wrong, out_of_context = "Je suis heureux", "Je suis triste", "Hello world adhsh"
        candidates = [wrong, correct, out_of_context]
        outputs, cost, rid = comparer(reference, candidates)
        assert isinstance(outputs, list), "`outputs` is not list as expected"
        assert len(outputs) == 1, f"`len(outputs) = {len(outputs)}` despite single reference."
        assert cost['orion-fr@default']['batch_size'] == len(candidates)+1, \
            f"`batch_size={cost['orion-fr@default']['batch_size']}` different from {candidates} candidates+1."
        assert isinstance(rid, str), f"Detected type {type(rid)} for `rid`, expected `str` instead."
        assert output_keys == \
               outputs[0].keys(), f"Set of keys is different than expected. Expected " \
                                  f"{output_keys} got {outputs[0].keys()} instead."
        assert outputs[0]["reference"] == reference, f"`reference` field in `outputs` does not " \
                                                     f"match the input `reference` sentence."

        similarities = outputs[0]["similarities"]
        similarities.sort(key=lambda x: x["similarity"], reverse=True)
        best = similarities[0]["candidate"]
        assert best == correct, f"The best candidate found is not correct."
        cos_sims = [element["similarity"] for element in similarities]
        assert all([-1. <= cossim <= 1. for cossim in cos_sims]), "Detected cosine similarity " \
                                                                "value outside of [-1, 1]."


if __name__ == '__main__':
    unittest.main()
