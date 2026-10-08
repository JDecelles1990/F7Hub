#!/usr/bin/env python3
"""Read-only validation of an UNAPPROVED synthetic development fixture.
No F7Hub database, network calls or production files are accessed.
Install optional dependency: python -m pip install jsonschema
"""
import json
from pathlib import Path
from collections import Counter
from unicodedata import normalize

ROOT = Path(__file__).resolve().parent.parent

def read_json(path):
    return json.loads(path.read_text(encoding='utf-8'))

def main():
    from jsonschema import Draft202012Validator
    schema = read_json(ROOT / 'schemas/synthetic_case_seed_v0_1.schema.json')
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema)
    cases = [json.loads(x) for x in (ROOT / 'data/synthetic_cases.jsonl').read_text(encoding='utf-8').splitlines() if x.strip()]
    coverage = read_json(ROOT / 'data/coverage_candidates.json')
    domains = read_json(ROOT / 'data/domain_inventory.json')
    domain_keys = {d['domain_key'] for d in domains}
    errors = []
    if not cases:
        errors.append('No cases found')
    keys = set()
    for index, case in enumerate(cases, 1):
        prefix = f'case line {index}'
        for e in validator.iter_errors(case):
            errors.append(f'{prefix}: schema: {e.message} at {list(e.path)}')
        key = case.get('case_id')
        if key in keys: errors.append(f'{prefix}: duplicate case ID {key}')
        keys.add(key)
        if case.get('domain_key') not in domain_keys: errors.append(f'{prefix}: unknown domain')
        steps=case.get('diagnostic_steps', [])
        if [s.get('sequence') for s in steps] != list(range(1,len(steps)+1)):
            errors.append(f'{prefix}: non-consecutive diagnostic step numbers')
        if any(n not in [s.get('sequence') for s in steps] for n in case.get('root_cause',{}).get('evidence_step_numbers',[])):
            errors.append(f'{prefix}: invalid evidence step reference')
        if not case.get('synthetic') or case.get('training_allowed') or case.get('production_knowledge_allowed') or case.get('canonical_issue_ref') is not None:
            errors.append(f'{prefix}: unapproved case has authority/training flags')
    candidate_ids = set()
    candidate_signatures = set()
    for c in coverage:
        if c['candidate_id'] in candidate_ids:errors.append(f'duplicate candidate ID {c["candidate_id"]}')
        candidate_ids.add(c['candidate_id'])
        signature=(c['domain_key'],normalize('NFC',c['issue_label_en']).casefold().strip())
        if signature in candidate_signatures: errors.append(f'duplicate candidate within domain {signature}')
        candidate_signatures.add(signature)
        if c['domain_key'] not in domain_keys:errors.append(f'unknown domain in candidate {c["candidate_id"]}')
        if c.get('status') != 'UNREVIEWED_CANDIDATE' or c.get('canonical_id') is not None:
            errors.append(f'unapproved candidate authority marker {c["candidate_id"]}')
    manifest=read_json(ROOT/'manifest.json')
    if (manifest['cases'],manifest['domains'],manifest['issue_family_candidates'])!=(len(cases),len(domains),len(coverage)):
        errors.append('manifest totals do not match')
    print(f'Cases: {len(cases)} | Domains: {len(domains)} | Issue-family candidates: {len(coverage)}')
    print(f'JSON Schema violations / integrity problems: {len(errors)}')
    for e in errors[:20]: print(' -',e)
    if errors: raise SystemExit(1)
    print('PASS: Structural checks passed; technical accuracy and real-world effectiveness NOT validated')

if __name__ == '__main__': main()
