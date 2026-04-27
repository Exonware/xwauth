# REF_37 — TCO benchmark evidence

**Purpose:** REF_25 #19 — publish **reproducible** performance evidence for Appendix A / sales collateral.  
**Publish checklist:** `exonware.xwauth.connector.ops.tco_evidence.tco_benchmark_publish_checklist()`  
**Validator:** `exonware.xwauth.connector.ops.tco_evidence.validate_microbench_output`  
**Tests:** `tests/1.unit/ops_tests/test_tco_evidence.py`

---

## Workflow

1. Record environment (CPU, RAM, Python, git SHA, package versions).  
2. Run `python -m exonware.xwauth.connector.bench --json` (see [benchmarks/README.md](../benchmarks/README.md)).  
3. Pass the dict through `validate_microbench_output` before archiving.  
4. Optionally run `xwauth-connector-api/scripts/http_bench.py` and socket load per xwauth-connector-api `benchmarks/README.md`.  
5. Update [REF_25 Appendix A](REF_25_COMPETITIVE_ADVANCE_BACKLOG.md#appendix-a--tco-snapshot-stub) with summarized numbers.

---

## Git policy

Track JSON under `docs/logs/benchmarks/` only for **intentional** published baselines; local scratch runs can stay untracked.

---

*Last updated: 2026-04-03*
