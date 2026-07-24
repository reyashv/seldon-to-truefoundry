"""
Locust load test for the two-level inference chain.
Same payload works against both Seldon (chain-default) and the TrueFoundry
orchestrator, so you can point it at either with -H and compare fairly.

PAYLOAD is the identity-node request; response should echo ndarray [[1, 2]].

Two modes:
  1. Fixed-load latency test  -> keep THROUGHPUT set (default). Paces each user
     to a steady rate so you measure real per-request latency below saturation.
  2. Max-throughput test      -> set THROUGHPUT = 0 (or env FIXED_RPS=0). Removes
     pacing so users hammer as fast as they can; watch RPS until it plateaus.

Run examples (see README notes at bottom of this file).
"""

import os
from locust import HttpUser, task, constant_throughput, between

# Per-user target requests/sec. With -u 50 and THROUGHPUT 1.0 => ~50 RPS total.
# Set to 0 to disable pacing (max-throughput mode).
THROUGHPUT = float(os.getenv("FIXED_RPS_PER_USER", "1.0"))

PAYLOAD = {"data": {"names": ["a1", "a2"], "ndarray": [[1, 2]]}}
PREDICT_PATH = "/api/v1.0/predictions"


class ChainUser(HttpUser):
    # constant_throughput paces each user to THROUGHPUT req/s.
    # If THROUGHPUT is 0, fall back to no wait (max-throughput mode).
    if THROUGHPUT > 0:
        wait_time = constant_throughput(THROUGHPUT)
    else:
        wait_time = between(0, 0)

    @task
    def predict(self):
        with self.client.post(
            PREDICT_PATH,
            json=PAYLOAD,
            name="predict",
            catch_response=True,
        ) as resp:
            if resp.status_code != 200:
                resp.failure(f"status {resp.status_code}: {resp.text[:200]}")
                return
            # Optional correctness check: identity node should echo [[1, 2]].
            try:
                nd = resp.json()["data"]["ndarray"]
                if nd != [[1, 2]]:
                    resp.failure(f"unexpected ndarray: {nd}")
            except Exception as e:  # noqa: BLE001
                resp.failure(f"bad body: {e}")
