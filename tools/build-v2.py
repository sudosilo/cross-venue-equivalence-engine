# Blue Phone
# Rebuilds index.html from the template, the dataset and the seal block.
# Run from the repo root:  python3 tools/build-v2.py
import json
t = open('tools/cross-venue-engine-v2-template.html').read()
d = json.dumps(json.load(open('data/qsr-dataset-v2.json')), separators=(',', ':'))
seal = open('tools/mtg-seal-block.html').read()
open('index.html', 'w').write(t.replace('__DATA__', d).replace('__SEAL__', seal))
print('index.html rebuilt')
