import unittest
import math

import lightonmuse


class TestCalibratedSelect(unittest.TestCase):
    def test_calibrated_select(self):
        output_keys = {"reference", "rankings", "best", "execution_metadata", "calibrated"}
        selector = lightonmuse.CalibratedSelect("orion-fr")
        reference = 'Voici une critique : "Un film fait par des parisiens pour des parisiens. Un accent faux et dégradant. Pour un tout sans saveur."\n'
        correct, wrong = "négative", "positive"
        candidates = [correct, wrong]
        conjunction = "Cette critique est"
        content_free_inputs = ['Voici une critique : "" \n', 'Voici une critique : " " \n']

        # check that an error is raised if calibration is not initialized
        with self.assertRaises(RuntimeError) as cm:
            _, _, _ = selector(reference, candidates, conjunction=conjunction)
        exception = cm.exception
        assert "should be initialized" in str(
            exception
        ), f"Exception for CalibratedSelect did not raise message about initializing calibration."

        selector.fit(
            content_free_inputs=content_free_inputs,
            candidates=candidates,
            conjunction=conjunction,
        )
        outputs, cost, rid = selector(reference, candidates, conjunction=conjunction)
        assert isinstance(outputs, list), "`outputs` is not list as expected"
        assert len(outputs) == 1, f"`len(outputs) = {len(outputs)}` despite single reference."
        assert cost["orion-fr@default"]["batch_size"] == len(
            candidates
        ), f"`batch size={cost['orion-fr@default']['batch_size']}` despite {len(candidates)} candidates."
        assert isinstance(rid, str), f"Detected type {type(rid)} for `rid`, expected `str` instead."
        assert output_keys == outputs[0].keys(), (
            f"Set of keys is different than expected. Expected "
            f"{output_keys} got {outputs[0].keys()} instead."
        )
        # Calibration specific errors
        assert outputs[0]["reference"] == reference, (
            f"`reference` field in `outputs` does not " f"match the input `reference` sentence."
        )
        calibrated = outputs[0]["calibrated"]
        assert calibrated["calibration_cost"]["batch_size"] == len(
            candidates
        ), f"Calibration `batch size={calibrated['calibration_cost']['batch_size']}` despite {len(candidates)} candidates."
        assert calibrated["content_free_inputs"] == content_free_inputs, (
            f"`content_free_inputs` field in `outputs` does not "
            f"match the input `content_free_inputs` used for calibration."
        )

        assert calibrated["calibration_mode"] == "diagonal_W", (
            f"`calibration_mode` field in `outputs` does not "
            f"match the input default `calibration_mode`."
        )

        assert calibrated["best"] == correct, f"{calibrated['best']} was chosen but the correct answer is {correct}"
        rankings = calibrated["scores"]
        assert len(rankings) == len(candidates), (
            f"Got {len(rankings)}  elements in calibrated rankings "
            f"while {len(candidates)} candidates were given."
        )

        scores = [element[1] for element in rankings.items()]

        # check that same candidates re-order differently give the same results
        outputs_switch, _, _ = selector(reference, candidates[::-1], conjunction=conjunction)
        scores_switch = [
            element[1] for element in outputs_switch[0]["calibrated"]["scores"].items()
        ]
        assert all(
            (math.isclose(s1, s2) for s1, s2 in zip(sorted(scores), sorted(scores_switch)))
        ), f"Calibrated scores using re-ordered candidates are not the same."

        # check that different content free inputs gives different calibrated scores
        selector.fit(
            content_free_inputs='Voici une critique : "" \n',
            candidates=candidates,
            conjunction=conjunction,
        )
        outputs_diffit, _, _ = selector(reference, candidates, conjunction=conjunction)

        scores_diffit = [
            element[1] for element in outputs_diffit[0]["calibrated"]["scores"].items()
        ]
        assert (
            scores != scores_diffit
        ), f"Calibrated scores using different content free inputs are the same."

        # check that different calibration mode gives different calibrated scores
        selector.fit(
            content_free_inputs=content_free_inputs,
            candidates=candidates,
            conjunction=conjunction,
            calibration_mode="identity_W",
        )
        outputs_mode, _, _ = selector(reference, candidates, conjunction=conjunction)

        scores_mode = [element[1] for element in outputs_mode[0]["calibrated"]["scores"]]
        assert (
            scores != scores_mode
        ), f"Calibrated scores using different calibration modes are the same."

        # check that errors are raised properly if using different candidates/conjuction
        wrong_candidates = ["positive", "négative", "neutre"]
        with self.assertRaises(ValueError) as cm:
            _, _, _ = selector(reference, wrong_candidates, conjunction=conjunction)
        exception = cm.exception
        assert "initialized with candidates" in str(
            exception
        ), f"Exception for CalibratedSelect did not raise message about calibration initialized with different candidates."

        wrong_conjunction = "Cette critique exprime un avis"
        with self.assertRaises(ValueError) as cm:
            _, _, _ = selector(reference, candidates, conjunction=wrong_conjunction)
        exception = cm.exception
        assert "initialized with conjunction" in str(
            exception
        ), f"Exception for CalibratedSelect did not raise message about calibration initialized with a different conjunction."

        # check that calibration mode error is raised
        with self.assertRaises(ValueError) as cm:
            selector.fit(
                content_free_inputs=content_free_inputs,
                candidates=candidates,
                conjunction=conjunction,
                calibration_mode="something",
            )
        exception = cm.exception
        assert "calibration_mode" in str(
            exception
        ), f"Exception for CalibratedSelect did not raise message about wrong `calibration_mode`."


if __name__ == "__main__":
    unittest.main()
