"""Functional checks on the CURRENT PC; not a laptop benchmark."""
from pathlib import Path
import json
import numpy as np
from demo.runtime import Sample, Engine
from demo.prepare import write_json


def main():
    sample, engine = Sample(), Engine()
    origin = list(sample.origins)[-1]
    past, dates = sample.window(origin)
    outcomes = []
    for model in engine.registry:
        first = engine.predict(model, past, dates, lambda status: print(model, status, flush=True))
        second = engine.predict(model, past, dates, lambda status: None)
        a = np.array([[r[c] for c in ("open", "high", "low", "close")] for r in first["predictions"]])
        b = np.array([[r[c] for c in ("open", "high", "low", "close")] for r in second["predictions"]])
        if not np.isfinite(a).all() or not np.allclose(a, b, atol=1e-6, rtol=1e-6):
            raise AssertionError("Invalid/repeated output differs")
        outcomes.append(dict(model=model, device=first["device_name"], rows=len(a), repeated_max_difference=float(np.abs(a - b).max()), checkpoint_sha256=first["checkpoint_sha256"]))
    engine.unload()
    cpu = Engine(preferred="cpu")
    result = cpu.predict("kronos-mini", past, dates, lambda status: None)
    outcomes.append(dict(model="kronos-mini", device=result["device"], rows=len(result["predictions"])))
    cpu.unload()
    write_json(Path(__file__).parent / "checks/native_smoke.json", dict(status="pass", test="functional_current_pc_not_laptop_benchmark", laptop_benchmark="skipped_at_user_request", origin=origin, jobs=outcomes))
    print(json.dumps(outcomes, indent=2))


if __name__ == "__main__":
    main()
