#!/usr/bin/env python3
"""Read-only validation of F7Hub proposed RCA sample. Never writes to SQLite."""
import json,sys
from pathlib import Path
p=Path(__file__).with_name('priority_rca_graph.proposed.json')
a=json.loads(p.read_text(encoding='utf-8'))
assert a['authority']=='PLANNING_ONLY' and a['canonical_ids_verified'] is False
assert a['validation_contract']['auto_sqlite_write'] is False
nodes=a['symptom_anchors']+a['cause_candidates']+a['diagnostic_check_candidates']+a['finding_candidates']+a['action_candidates']
ids=[r['id'] for r in nodes]
assert len(ids)==len(set(ids)), 'Duplicate draft node ID'
byid={x['id']:x for x in nodes}
for sym in a['symptom_anchors']:
 assert sym['status']=='REQUIRES_TECHNICAL_REVIEW' and sym['canonical_id'] is None
 assert sym['label_en'] and sym['label_fr'] and sym['verification']
 assert len(sym['branches'])>=2
 for branch in sym['branches']:
  for k,kind in [('cause_ref','cause'),('check_ref','check'),('action_ref','action'),('finding_ref','finding')]:
   assert branch[k] in byid and byid[branch[k]]['kind']==kind
  assert branch['evidence_status']=='HYPOTHESIS_NOT_TESTED'
assert len(a['source_reconciliation'])==len(set(x['source_candidate_id'] for x in a['source_reconciliation']))
for row in a['source_reconciliation']:
 for ref in row['matched_draft_anchor_ids']+row['matched_related_node_ids']:
  assert ref in byid, f'Unresolved intake relationship {ref}'
print('PASS: JSON parse, unique draft IDs, typed graph references, bilingual labels, unapproved policy and source reconciliation')
print('Counts:',len(a['symptom_anchors']),'anchors,',len(a['domains']),'domains,',sum(len(x['branches']) for x in a['symptom_anchors']),'branches,',len(a['source_reconciliation']),'source candidates')
