#!/usr/bin/env python3
"""Rebuild only the three tracked, public demo outputs."""
import importlib.util
from pathlib import Path

root=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('viewer', root/'scripts/create-viewer.py')
viewer=importlib.util.module_from_spec(spec)
spec.loader.exec_module(viewer)
for source,output,line in [('docs/example.md','docs/viewer.html',9),('docs/message.md','docs/message.html',1),('SKILL.md','docs/skill.html',1)]:
    target=root/output
    if target.exists(): target.unlink()
    print(viewer.create_viewer(root/source,target,line,public=True))
