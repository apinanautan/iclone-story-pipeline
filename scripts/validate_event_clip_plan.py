# EVENT_CLIP_VALIDATOR
from pathlib import Path
import json, sys

ROOT=Path(__file__).resolve().parents[1]
PLAN=ROOT/'data'/'part3_event_clips.json'
data=json.loads(PLAN.read_text(encoding='utf-8'))
errors=[]
if data.get('production_mode')!='event_clip_render_first':
    errors.append('production_mode must be event_clip_render_first')
events=data.get('events',[])
ids=[e.get('id') for e in events]
if ids[:3]!=['3.1','3.2','3.3']:
    errors.append('required first events must be 3.1, 3.2, 3.3')
if not all(e.get('render_before_next') is True for e in events):
    errors.append('every event must render/check before next event')
if any(e.get('start_sec') is not None or e.get('end_sec') is not None for e in events):
    errors.append('do not hard-code time boundaries before event alignment')
if data.get('old_fixed_audio_splits',{}).get('do_not_force') is not True:
    errors.append('old fixed audio splits must remain superseded')
if errors:
    print('FAIL')
    for e in errors: print('-',e)
    sys.exit(1)
print('PASS event-clip plan')
print('events:', ', '.join(ids))
print('boundary:', data['boundary_rule'])
