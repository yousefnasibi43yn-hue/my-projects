"""VictoriaMetrics query client (Prometheus-compatible HTTP API)."""

import os
from typing import Any

import httpx

VM_URL = os.getenv("VICTORIAMETRICS_URL", "http://localhost:8428")


async def query_instant(promql: str) -> dict[str, Any]:
    """Run an instant PromQL query against VictoriaMetrics."""
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(
            f"{VM_URL}/api/v1/query",
            params={"query": promql},
        )
        response.raise_for_status()
        return response.json()


def extract_scalar(result: dict[str, Any], default: float = 0.0) -> float:
    """Extract a single numeric value from a VictoriaMetrics query result."""
    data = result.get("data", {})
    results = data.get("result", [])
    if not results:
        return default
    value = results[0].get("value", [None, "0"])
    try:
        return float(value[1])
    except (IndexError, TypeError, ValueError):
        return default
