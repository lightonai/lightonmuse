import unittest

import lightonmuse


class TestTokenizeEndpoint(unittest.TestCase):
    def test_single_input(self):
        output_keys = ['tokens_used', 'tokens_input', 'tokens_generated', 'cost_type', 'batch_size']
        tokenizer = lightonmuse.Tokenize("orion-fr-v2")
        sentence = "C'est quand même un truc magique, se dit le livreur, que d'avoir toujours"
        outputs, cost, rid = tokenizer(sentence)
        assert len(outputs) == 1, f"Encountered output of length {len(outputs)} while expecting length=1"
        assert list(outputs[0]['execution_metadata']['cost'].keys()) == output_keys, \
            f"Output keys have changed from expected {output_keys}"

    def test_multiple_input(self):
        output_keys = ['tokens_used', 'tokens_input', 'tokens_generated', 'cost_type', 'batch_size']
        tokenizer = lightonmuse.Tokenize("orion-fr-v2")
        sentence = "C'est quand même un truc magique, se dit le livreur, que d'avoir toujours"
        n = 3
        outputs, cost, rid = tokenizer([sentence]*n)
        assert len(outputs) == n, f"Encountered output of length {len(outputs)} while expecting length={n}"
        assert list(outputs[0]['execution_metadata']['cost'].keys()) == output_keys, \
            f"Output keys have changed from expected {output_keys}"


if __name__ == '__main__':
    unittest.main()
