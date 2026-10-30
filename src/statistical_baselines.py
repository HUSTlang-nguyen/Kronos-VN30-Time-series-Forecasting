"""Past-only statistical baselines; failures are evidence, never Naive fills."""

from __future__ import annotations

import itertools
import warnings
import numpy as np


def candidates(name):
    if name == "ridge":
        return [{"alpha": a} for a in (1.0, 10.0, 100.0, 1000.0)]
    if name == "arima":
        return [
            {"order": list(order)}
            for order in itertools.product(range(3), range(2), range(3))
        ]
    if name == "ets":
        return [
            {"trend": trend, "damped_trend": damped}
            for trend, damped in ((None, False), ("add", False), ("add", True))
        ]
    raise ValueError(name)


def statistical_predictor(name, config):
    from statsmodels.tools.sm_exceptions import ConvergenceWarning

    def predict(history, dates, seed):
        from vn30_forecast import CONTEXT, HORIZON

        if history.shape != (CONTEXT, 4):
            raise ValueError(
                "Statistical baseline needs exactly 128 historical OHLC rows"
            )
        paths = []
        for col in range(4):
            with warnings.catch_warnings():
                warnings.simplefilter("error", ConvergenceWarning)
                if name == "arima":
                    from statsmodels.tsa.arima.model import ARIMA

                    fitted = ARIMA(history[:, col], order=tuple(config["order"])).fit()
                    if not fitted.mle_retvals.get("converged", False):
                        raise RuntimeError("ARIMA did not converge")
                else:
                    from statsmodels.tsa.holtwinters import ExponentialSmoothing

                    fitted = ExponentialSmoothing(
                        history[:, col],
                        trend=config["trend"],
                        damped_trend=config["damped_trend"],
                        seasonal=None,
                        initialization_method="estimated",
                    ).fit(optimized=True)
                    result = getattr(fitted, "mle_retvals", None)
                    if result is not None and not result.get("success", True):
                        raise RuntimeError("ETS did not converge")
                paths.append(np.asarray(fitted.forecast(HORIZON)))
        result = np.stack(paths, axis=1)
        if not np.isfinite(result).all():
            raise ValueError("Statistical baseline produced non-finite forecast")
        return result

    return predict


def selection_loss(predictions, truths, train_scale):
    # Equal weights across Open/Close and h=1/5/20, scaled by TRAIN only.
    return float(
        np.mean(
            np.abs(
                predictions[:, [0, 4, 19]][:, :, [0, 3]]
                - truths[:, [0, 4, 19]][:, :, [0, 3]]
            )
            / train_scale[[0, 3]]
        )
    )
