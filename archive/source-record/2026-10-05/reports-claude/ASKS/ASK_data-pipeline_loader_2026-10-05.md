# Ask for the data-pipeline owners: automatic loader on the engine host (2026-10-05)

From: Pulso improvement-engine team (Claude), lane INFRA-A. Context: infra stacked PR claude/infra-auto-loader (docs/auto-loader.md) runs the pipeline image in a bounded container on the engine host after the operator uploads `landing/` and a marker. Nothing was run against your code; these contracts are UNVERIFIED.

1. `dbt/profiles.yml`: add `memory_limit: "{{ env_var('DUCKDB_MEMORY_LIMIT', '2GB') }}"` and `temp_directory: "{{ env_var('DUCKDB_TEMP_DIRECTORY', '/work/duckdb_tmp') }}"` to the dev and s3 targets (spill to disk instead of RAM).
2. A measured table for a full 13-table build: peak RSS and duration with memory_limit 1.5, 2 and 3 GB on 2 and 4 vCPU (README only has laptop time, 6m18s with 1 thread, and says Fargate CPU/memory is unmeasured).
3. Confirm `python -m pipeline.run --steps ingest_e0,ingest_bank,build,publish` names, `python -m pipeline.ingest_bank --tables <csv>` run per batch gives the same warehouse as one run, and that `DATASET_BUCKET`/`DATASET_PREFIX`/`DATASET_REGION` with no `DATASET_AWS_*` read our own bucket (`landing/bank`) through the standard credential chain.
4. Confirm that with `PIPELINE_ROOT=s3://<bucket>/lake` the publication is `lake/publish/<run>/...` with `latest.json` last, and that `parquet/` contains analytics-zone data only (our bucket Deny covers only `gold_restricted.duckdb`).
5. bank_cells: say who owns the producer of `cells.ndjson` (engine `scripts/aggregate/bank_cells.py` today) and provide a command/image that runs inside the loader; the loader gates it with `check_cells_k.py` (k>=10, allowed keys only) before publishing.
