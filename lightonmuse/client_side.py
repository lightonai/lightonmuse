from typing import List, Optional, Tuple, Union
import numpy as np
from .api_requests import Select


class CalibratedSelect(Select):
    """Calibrated Select endpoint.

    Parameters
    ----------
    model: str,
        name of the model to use as intelligence engine.
        Currently supports only `"orion-fr-v2"` and `"lyra-en"`.
    """

    def __init__(self, model: str = "orion-fr-v2"):
        super().__init__(model)
        self.candidates = None
        self.conjunction = None
        self.W = None
        self.b = None
        self.calib_cost = None

    def fit(
        self,
        content_free_inputs: Union[str, List[str]],
        candidates: List[str],
        conjunction: Optional[str] = None,
        calibration_mode: Optional[str] = "diagonal_W",
    ):
        """Computes the calibration matrices to be used with Select.
        Parameters
        -------------
        content_free_inputs: Union[str, List[str]],
            content-free input(s) that are to be used for calibration.
            Note that these should use the same formatting/templating as the
            references you wish to use for Select later on.
        mode: Optional[str], default to "diagonal_W",
            calibration mode to be used. Must be in ["diagonal_W", "identity_W"].
        """
        if calibration_mode not in ["diagonal_W", "identity_W"]:
            raise ValueError(
                f"calibration_mode: {calibration_mode} is not valid. Use one of `diagonal_W` or `identity_W`"
            )
        self.calibration_mode = calibration_mode
        self.candidates = candidates
        self.conjunction = conjunction

        if isinstance(content_free_inputs, str):
            content_free_inputs = [content_free_inputs]

        self.content_free_inputs = content_free_inputs
        self.W, self.b = self.get_calibration_matrices()

    def get_calibration_matrices(self) -> Tuple[np.ndarray, np.ndarray]:
        # Calculate the content-free probabilities for different content-free templates
        n_tokens_used = 0
        all_p_cf = []
        for cf_input in self.content_free_inputs:
            out_cf, _, _ = super().__call__(cf_input, self.candidates, conjunction=self.conjunction)
            all_p_cf.append(
                [
                    np.exp(element["score"]["normalized_logprob"])
                    for element in out_cf[0]["rankings"]
                ]
            )
            n_tokens_used += out_cf[0]["execution_metadata"]["cost"]["tokens_used"]
        self.calib_cost = out_cf[0]["execution_metadata"]["cost"]
        self.calib_cost["tokens_used"] = n_tokens_used
        self.calib_cost["tokens_input"] = n_tokens_used

        # Average over the different templates and normalize
        p_cf = np.mean(np.array(all_p_cf), axis=0)
        p_cf = p_cf / sum(p_cf)

        num_candidates = len(self.candidates)
        if self.calibration_mode == "diagonal_W":
            W = np.linalg.inv(np.identity(num_candidates) * p_cf)
            b = np.zeros([num_candidates, 1])
        else:
            W = np.identity(num_candidates)
            b = -1 * np.expand_dims(p_cf, axis=-1)
        return W, b

    def __call__(
        self,
        reference: str,
        candidates: List[str],
        conjunction: str = None,
        concat_best: bool = False,
    ) -> Tuple[List, int, str]:
        """Parameters
        -------------
        reference: str,
            reference input to compute likelihood against.
        candidates: List[str],
            input(s) that are compared to the reference and ranked based on likelihood.
            Must match the candidates used in the `fit` method.
        conjunction: str, default to None,
            expression used to link `reference` and `candidates` to create the prompt used to
            compute the likelihood. The prompt will have the structure
            `reference + conjunction + candidate`. Finding a good conjunction can greatly increase
            the performance of `Select`.
            Must match the conjunction used in the `fit` method.
        concat_best: bool, default to False,
            whether the response will contain a "best" field with the selected choice.

        Return
        ------
        outputs: list,
            list of dicts containing the reference text, the rankings of the candidates together
            with their scores and other metadata. The results after calibration are stored in the
            "calibrated" key.
        cost: int,
            cost for the analysis completed.
        request_id: str,
            ID string for the request.
        """
        if self.candidates is None:
            raise RuntimeError(
                f"Calibration should be initialized with the `fit` method before use."
            )
        else:
            if sorted(self.candidates) != sorted(candidates):
                raise ValueError(
                    f"Calibration initialized with candidates {self.candidates}. Please change your candidates or `fit` to your new candidates."
                )
            if conjunction != self.conjunction:
                raise ValueError(
                    f"Calibration initialized with conjunction {self.conjunction}. Please change your conjunction or `fit` to your new conjunction."
                )

        out_uncal, cost, request_id = super().__call__(
            reference,
            self.candidates,
            conjunction=self.conjunction,
            concat_best=concat_best,
        )
        # Extract and normalize the uncalibrated scores
        probs_uncal = [
            np.exp(element["score"]["normalized_logprob"]) for element in out_uncal[0]["rankings"]
        ]
        probs_uncal = probs_uncal / sum(probs_uncal)

        # Calculate the calibrated scores and get the "correct" label
        scores_cal = np.matmul(self.W, np.expand_dims(probs_uncal, axis=-1)) + self.b
        correct_label_idx = np.argmax(scores_cal)

        if concat_best:
            best = (
                f"{reference} {self.conjunction} {self.candidates[correct_label_idx]}"
                if self.conjunction is not None
                else f"{reference} {self.candidates[correct_label_idx]}"
            )
        else:
            best = self.candidates[correct_label_idx]
        out_uncal[0]["calibrated"] = {
            "best": best,
            "scores": {self.candidates[i]: scores_cal[i][0] for i in range(len(self.candidates))},
            "content_free_inputs": self.content_free_inputs,
            "calibration_mode": self.calibration_mode,
            "calibration_cost": self.calib_cost,
        }
        return out_uncal, cost, request_id
