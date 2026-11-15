from pathlib import Path
import ast
ROOT = Path(__file__).resolve().parent.parent
src = (ROOT/'scripts/ic8_part7_cast.py').read_text(encoding='utf-8')
p3 = ast.parse((ROOT/'scripts/ic8_part3_build.py').read_text(encoding='utf-8'))
cast = next(n.value for n in p3.body if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'CAST' for t in n.targets))
monk = ast.literal_eval(cast.values[0].elts[0])
start = src.index('CAST = {'); end = src.index('\nONLY =', start)
src = src[:start] + 'CAST = {\n    "monk": (' + repr(monk) + ', (-860,450,0), STAND),\n    "oi": (r"5. สีกาอ๋อย\\สีกาอ๋อย หญิงหม้ายดูสาว วัย 40.iAvatar", (-860,300,180), None),\n}' + src[end:]
src = src.replace('L = 28.0','L = 13.84').replace('p7c_log.txt','p10_cast_log.txt')
# Side-sitting comes from GUI AccuPOSE; face follows pose, not before.
src = src.replace('while cur < L - 0.05:', 'while body and cur < L - 0.05:')
(ROOT/'scripts/ic8_part10_cast.py').write_text(src, encoding='utf-8')
J = Path.home()/'AppData/Local/Tidmunz Studio/snapgen_data/ic8_jobs/run'
assert J.is_dir()
(J/'p10_monk.py').write_text(src.replace('ONLY = None', 'ONLY = "monk"'), encoding='utf-8')
(J/'p10_oi.py').write_text(src.replace('ONLY = None', 'ONLY = "oi"'), encoding='utf-8')
rule = '\n- Part 10 (2026-11-07): user approved overwrite 10.iProject. Oi sits Thai side-sitting (พับเพียบ) on ground with tiffin carrier beside her; monk stands looking down at her. User finishes part 9; do not alter or save it.\n'
skill = Path.home()/'.claude/skills/iclone-key/SKILL.md'
text = skill.read_text(encoding='utf-8')
if rule.strip() not in text:
    text += rule
    skill.write_text(text, encoding='utf-8')
(ROOT/'docs/iclone-key-SKILL.md').write_text(text, encoding='utf-8')
print('Queued monk and Oi; skill updated')
