"""Read-only E0 audit. Output aggregates/schema/digests, never IDs or answers."""
import hashlib
import json
import sys
from pathlib import Path

root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(root / "tmp" / "e0_audit_deps"))
import duckdb

package = root / "pulso_muestra_e0"
history = json.loads((package / "contratos/platform_history.json").read_text(encoding="utf-8"))
evaluation = json.loads((package / "contratos/evaluation.json").read_text(encoding="utf-8"))
con = duckdb.connect(":memory:")
entities = history["entities"] | evaluation["entities"]
report = {"contracts": {"history": history["version"], "evaluation": evaluation["version"]}, "files": {}, "absent_entities": []}
for name, definition in entities.items():
    path = package / "datos" / (name + ".parquet")
    if not path.exists():
        report["absent_entities"].append(name)
        continue
    quoted = str(path).replace("'", "''")
    con.execute(f'CREATE VIEW "{name}" AS SELECT * FROM read_parquet(\'{quoted}\')')
    cols = [r[0] for r in con.execute(f'DESCRIBE "{name}"').fetchall()]
    expected = set(definition["fields"])
    report["files"][name] = {"rows": con.execute(f'SELECT count(*) FROM "{name}"').fetchone()[0], "columns_missing": sorted(expected-set(cols)), "columns_extra": sorted(set(cols)-expected), "ingested_at_present": "ingested_at" in cols, "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}

queries = {
    "channels": 'SELECT channel,count(*) FROM "case" GROUP BY channel ORDER BY channel',
    "origins": 'SELECT origin,count(*) FROM "case" GROUP BY origin ORDER BY origin',
    "split": 'SELECT split,count(*) FROM labels GROUP BY split ORDER BY split',
    "identity_results": 'SELECT trigger,result,count(*) FROM identity_check GROUP BY trigger,result ORDER BY trigger,result',
    "identity_expected": 'SELECT expected_identity_check,count(*) FROM labels GROUP BY expected_identity_check ORDER BY expected_identity_check',
    "identity_sanity": 'SELECT count(*) FILTER(WHERE ended_at<started_at),count(*) FILTER(WHERE result=\'verified\' AND correct<2),count(*) FILTER(WHERE result=\'failed\' AND correct>=2) FROM identity_check',
    "identity_question_storage": 'SELECT typeof(questions), count(*),count(*) FILTER(WHERE json_valid(questions)) FROM identity_check GROUP BY typeof(questions)',
    "identity_question_count": 'SELECT json_array_length(try_cast(questions AS JSON)),count(*) FROM identity_check GROUP BY 1 ORDER BY 1',
    "identity_schema": 'DESCRIBE identity_check',
    "unverified_credit_calls": 'SELECT count(*) FROM tool_call t WHERE tool_id=\'abono_provisional\' AND NOT EXISTS(SELECT 1 FROM identity_check i WHERE i.case_id=t.case_id AND i.result=\'verified\' AND i.ended_at<=t.event_time)',
    "regulator_origin_calls": 'SELECT channel,count(*) FROM "case" WHERE origin=\'regulator\' GROUP BY channel',
    "identity_orphans": 'SELECT count(*) FROM identity_check i LEFT JOIN "case" c USING(case_id) WHERE c.case_id IS NULL',
    "identity_tools": 'SELECT tool_id,count(*) FROM tool_call GROUP BY tool_id ORDER BY tool_id',
    "timeline_identity_count": 'SELECT count(*) FROM timeline WHERE kind=\'identity_check\'',
}
for name, query in queries.items():
    try:
        report[name] = con.execute(query).fetchall()
    except duckdb.Error as error:
        report[name] = {"query_unavailable": type(error).__name__}
for relative in ["README.md", "contratos/platform_history.json", "contratos/evaluation.json", "docs/policies.md", "docs/security_questions.md", "reportes/SAMPLE.md", "reportes/COVERAGE.md"]:
    report["files"][relative] = {"sha256": hashlib.sha256((package / relative).read_bytes()).hexdigest()}
print(json.dumps(report, ensure_ascii=False, indent=2, default=str))
