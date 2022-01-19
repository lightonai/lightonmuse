import random
import string
import unittest

import lightonmuse


single_input_endpoints = [lightonmuse.Analyse,
                          lightonmuse.Create,
                          lightonmuse.Embed]
double_input_endpoints = [lightonmuse.Compare,
                          lightonmuse.Select]


class TestCreateEndpoint(unittest.TestCase):
    def test_empty_string(self):
        for endpoint in single_input_endpoints:
            endpoint_obj = endpoint("orion-fr")
            with self.assertRaises(RuntimeError) as cm:
                if endpoint == lightonmuse.Create:
                    _, _, _ = endpoint_obj("", seed=0)
                else:
                    _, _, _ = endpoint_obj("")
            exception = cm.exception
            assert "Receive empty text" in str(exception), f"Exception for endpoint " \
                                                           f"{endpoint.__class__.__name__} " \
                                                           f"did not raise message about empty text."
        for endpoint in double_input_endpoints:
            endpoint_obj = endpoint("orion-fr")
            with self.assertRaises(RuntimeError) as cm:
                _, _, _ = endpoint_obj("", ["", ""])
            exception = cm.exception
            assert "Receive empty text" in str(exception), f"Exception for endpoint " \
                                                           f"{endpoint.__class__.__name__} " \
                                                           f"did not raise message about empty text."

    def test_prompt_too_long(self):
        n = 5000
        input_too_long = ''.join(random.choice(string.ascii_uppercase) for _ in range(n))
        for endpoint in single_input_endpoints:
            endpoint_obj = endpoint("orion-fr")
            with self.assertRaises(RuntimeError) as cm:
                if endpoint == lightonmuse.Create:
                    _, _, _ = endpoint_obj(input_too_long, seed=0)
                else:
                    _, _, _ = endpoint_obj(input_too_long)
            exception = cm.exception
            assert "The input is too long" in str(exception), f"Exception for endpoint " \
                                                              f"{endpoint.__class__.__name__} " \
                                                              f"did not raise message about input" \
                                                              f"too long."
        for endpoint in double_input_endpoints:
            endpoint_obj = endpoint("orion-fr")
            with self.assertRaises(RuntimeError) as cm:
                _, _, _ = endpoint_obj(input_too_long, [input_too_long, input_too_long])
            exception = cm.exception
            assert "The input is too long" in str(exception), f"Exception for endpoint " \
                                                              f"{endpoint.__class__.__name__} " \
                                                              f"did not raise message about input" \
                                                              f"too long."


if __name__ == '__main__':
    unittest.main()
