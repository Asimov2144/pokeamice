from pathlib import Path
import yaml, sys

if hasattr(sys.stdout, 'reconfigure'): sys.stdout.reconfigure(encoding='utf-8')

p = Path('_posts/2016-05-12-interview-pokken-tournament-inside.md')
fm = yaml.safe_load(p.read_text(encoding='utf-8').split('---', 2)[1])
for i, it in enumerate(fm['parallel_items'][:10]):
    print(f"[{i}] speaker: {repr(it.get('speaker'))} | orig: {repr(it.get('original')[:40])}")
