# xwauth performance benchmarks (scaffold)

**Status:** **Microbench (in-tree)** ships in `exonware.xwauth.connector.bench`; HTTP/load against `xwauth-connector-api` is still optional / manual.

## Microbench (JWT + OIDC hash hot paths)

Source: `src/exonware/xwauth.connector/bench/microbench.py` · Tests: `tests/1.unit/bench_tests/test_microbench.py`.

```bash
# From repo root (editable install) or PYTHONPATH=src
python -m exonware.xwauth.connector.bench --iterations 5000
python -m exonware.xwauth.connector.bench --iterations 5000 --json
```

```bash
pytest tests/1.unit/bench_tests/test_microbench.py -q --tb=short
```

Capture JSON to `docs/logs/benchmarks/MICROBENCH_<date>.json` when publishing numbers for REF_25 / TCO.

**HTTP stack (xwauth-connector-api):** in-process token endpoint timings via `python -m exonware.xwauth.connector_api.bench` — see [../xwauth-connector-api/benchmarks/README.md](../xwauth-connector-api/benchmarks/README.md) in a monorepo (or the published **xwauth-connector-api** repo’s `benchmarks/README.md`).

## Goals

- Reproducible **token endpoint** latency and throughput (p50/p95/p99) for `xwauth-connector-api` or minimal AS fixture.
- Comparable **methodology** section for TCO / competitive claims ([REF_25 Appendix A](../docs/REF_25_COMPETITIVE_ADVANCE_BACKLOG.md)).

## Environment (record in every run)

- OS, CPU model, RAM, Python version
- Worker model (uvicorn workers, `--loop`)
- Storage backend (in-memory vs real DB)
- Network (localhost vs remote)

## Suggested tools

- **Shipped:** `python -m exonware.xwauth.connector.bench` (wall-clock over `JWTTokenManager` + `oidc_left_half_sha256_b64url`)
- `wrk` / `hey` / `oha` against `/oauth/token` (client credentials or refresh) with warmed JWKS
- Optional: `pytest-benchmark` for regression tracking (not a default dependency)

## Reporting

1. Raw output in `docs/logs/benchmarks/TOKEN_BENCH_<date>.md`
2. One summary row in REF_25 Appendix A table after numbers exist

---

*Owner: align with REF_24 ops / REF_25 #6.*
