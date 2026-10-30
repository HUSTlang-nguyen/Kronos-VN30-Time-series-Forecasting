"""Serve the compiled dashboard and a serial local inference API."""
from contextlib import asynccontextmanager
import csv
import io
import os
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, ConfigDict
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware

from demo.runtime import DEMO, DemoError, Engine, Jobs, Sample


class ForecastRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    model_id: str
    origin: str


def create_app(sample=None, engine=None):
    sample = sample or Sample()
    engine = engine or Engine(preferred=os.environ.get("VN30_DEVICE", "auto"))
    jobs = Jobs(sample, engine)

    @asynccontextmanager
    async def lifespan(app):
        yield
        jobs.pool.shutdown(wait=True)

    app = FastAPI(title="VN30 Inference Studio", lifespan=lifespan)
    app.state.jobs = jobs
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=["localhost", "127.0.0.1", "[::1]", "testserver"])
    app.add_middleware(CORSMiddleware, allow_origins=["http://127.0.0.1:5173", "http://localhost:5173"], allow_methods=["GET", "POST"], allow_headers=["Content-Type"])

    @app.exception_handler(DemoError)
    async def demo_error(request, exc):
        return JSONResponse(dict(error=exc.code), status_code=429 if exc.code == "BUSY" else 404 if exc.code == "JOB_NOT_FOUND" else 422)

    @app.get("/api/health")
    def health():
        import torch
        cuda = torch.cuda.is_available() and engine.preferred != "cpu"
        return dict(app="vn30-inference-studio", status="ready", device="cuda:0" if cuda else "cpu", device_name=torch.cuda.get_device_name(0) if cuda else "CPU", torch_version=torch.__version__)

    @app.get("/api/catalog")
    def catalog():
        return dict(models=[{k: v[k] for k in ("id", "label", "variant", "parameters", "epoch", "training_seed")} for v in engine.registry.values()], origins=list(sample.origins), default_origin=list(sample.origins)[-1], default_model="kronos-small", snapshot_end=sample.manifest["snapshot_last_date"], evidence_scope="exploratory_only", context=128, horizon=20)

    @app.get("/api/history/{origin}")
    def history(origin: str):
        past, dates = sample.window(origin)
        return dict(history=past.to_dict("records"), future_dates=dates)

    @app.get("/api/reference/{origin}")
    def reference(origin: str):
        return dict(actual=sample.reference(origin))

    @app.post("/api/forecasts", status_code=202)
    def forecast(body: ForecastRequest):
        return jobs.submit(body.model_id, body.origin)

    @app.get("/api/jobs/{key}")
    def job(key: str):
        return jobs.get(key)

    @app.get("/api/jobs/{key}/forecast.csv")
    def export(key: str):
        item = jobs.get(key)
        if item["status"] != "complete":
            raise DemoError("JOB_NOT_READY")
        out = io.StringIO(newline="")
        writer = csv.DictWriter(out, fieldnames=["model", "origin", "date", "step", "open", "high", "low", "close", "seed", "device"])
        writer.writeheader()
        for row in item["result"]["predictions"]:
            writer.writerow(dict(model=item["model_id"], origin=item["origin"], **row, seed=42, device=item["result"]["device"]))
        return Response(out.getvalue(), media_type="text/csv", headers={"Content-Disposition": f'attachment; filename="vn30-{item["model_id"]}-{item["origin"]}.csv"'})

    frontend = DEMO / "frontend/dist"
    if frontend.exists():
        app.mount("/", StaticFiles(directory=frontend, html=True), name="dashboard")
    return app
