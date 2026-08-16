import asyncio
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST, REGISTRY

from app.metrics.metrics import (
    http_requests_total,
    http_request_duration_seconds,
)
from app.api.routes import router
from app.simulator import start_simulator


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Divar Ads Analytics starting up...")
    simulator_task = asyncio.create_task(start_simulator())
    print("All services initialized")
    yield
    simulator_task.cancel()
    try:
        await simulator_task
    except asyncio.CancelledError:
        pass
    print("Divar Ads Analytics shut down")


app = FastAPI(
    title="Divar Ads Analytics",
    description="""
    Real-time classified ads analytics service (Divar.ir-style marketplace).

    Demonstrates **Grafana + VictoriaMetrics + Python + Docker Compose**:
    - FastAPI exposes Prometheus-format metrics at `/metrics`
    - VictoriaMetrics scrapes and stores all time series
    - Grafana visualizes business KPIs and API performance via PromQL
    """,
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api")


@app.middleware("http")
async def prometheus_middleware(request: Request, call_next):
    method = request.method
    path = request.url.path
    start = time.perf_counter()
    response = await call_next(request)
    duration = time.perf_counter() - start
    status = str(response.status_code)
    route = request.scope.get("route")
    if route and hasattr(route, "path"):
        path = route.path
    http_requests_total.labels(method=method, path=path, status=status).inc()
    http_request_duration_seconds.labels(method=method, path=path).observe(duration)
    return response


@app.get("/health")
async def health():
    return {"status": "healthy", "service": "divar-ads-analytics"}


@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint — scraped by VictoriaMetrics every 3s."""
    return Response(content=generate_latest(REGISTRY), media_type=CONTENT_TYPE_LATEST)
