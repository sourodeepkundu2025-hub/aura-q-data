"""Check retained data integrity and table means without external packages."""
from pathlib import Path
import csv
import hashlib
import json
import math
from collections import defaultdict

root = Path(__file__).resolve().parent
manifest = json.loads((root / 'DATA_MANIFEST.json').read_text(encoding='utf-8'))
summaries = {}
for item in manifest['files']:
    path = root / item['path']
    assert path.resolve().is_relative_to(root.resolve())
    raw = path.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == item['sha256'], item['path']
    reader = csv.DictReader(raw.decode('utf-8-sig').splitlines())
    rows = list(reader)
    assert len(rows) == item['rows'] and reader.fieldnames == item['columns']
    if 'physical_qpu' in reader.fieldnames:
        assert all(r['physical_qpu'].lower() == 'false' for r in rows)
    if 'preference_regret' in reader.fieldnames:
        by_policy = defaultdict(list)
        for row in rows:
            value = float(row['preference_regret'])
            assert math.isfinite(value) and value >= -1e-12
            by_policy[row['policy']].append(value)
        summaries[path.name] = {k: sum(v)/len(v) for k,v in sorted(by_policy.items())}

ablation = list(csv.DictReader((root / 'data/figure_tables/four_stage_ablation.csv').read_text().splitlines()))
gold = summaries['gold_decision_records.csv']
qwen = summaries['qwen_decision_records.csv']
expectations = [gold['shortest_queue'], gold['highest_proxy_fidelity'],
                gold['aura_q_preference'], qwen['aura_q_preference']]
for row, expected in zip(ablation, expectations):
    assert math.isclose(float(row['mean_regret']), expected, abs_tol=1e-12), row['stage']
forest = list(csv.DictReader((root / 'data/figure_tables/profile_stratified_forest.csv').read_text().splitlines()))
assert [r['profile'] for r in forest if float(r['ci_low'])*float(r['ci_high']) > 0] == ['budget_first']
print(json.dumps({'status':'PASS', 'csv_files':len(manifest['files']),
                  'total_rows':sum(x['rows'] for x in manifest['files']),
                  'checks':'hashes, schemas, row counts, nonnegative finite regret, simulator flags, four-stage means, retained profile intervals',
                  'scope':'Data validation only; no re-execution of historical simulator or language models'}, indent=2))
