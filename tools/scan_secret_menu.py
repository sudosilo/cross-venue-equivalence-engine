# Blue Phone
# scan_secret_menu.py — plural-tolerant component extraction
# Reads scraped_items.json + ingredient_taxonomy.json from the current
# directory, scans each item's name and description text for taxonomy
# ingredient matches, and writes extracted_components.json:
# a list (same order/length as scraped_items.json) where each entry is
# that item's list of matched taxonomy ingredient names.

import json
import re
import collections

items = json.load(open('scraped_items.json'))
tax = json.load(open('ingredient_taxonomy.json'))


def singularize(word):
    """Basic English singularization, enough for menu vocabulary."""
    if len(word) > 3 and word.endswith('ies'):
        return word[:-3] + 'y'
    if len(word) > 3 and word.endswith('es') and word[-3] in 'sxzh':
        return word[:-2]
    if len(word) > 2 and word.endswith('s') and not word.endswith('ss'):
        return word[:-1]
    return word


def norm_phrase(text):
    """Lowercase, strip punctuation, singularize every word."""
    words = re.sub(r'[^a-z0-9 ]', ' ', text.lower()).split()
    return ' '.join(singularize(w) for w in words)


# normalized taxonomy name -> canonical taxonomy name
lookup = {norm_phrase(name): name for name in tax}
# longest phrases first so "Big Mac Sauce" wins before "Sauce" ever could
keys = sorted(lookup, key=len, reverse=True)


def extract(text):
    padded = ' ' + norm_phrase(text) + ' '
    found = []
    for key in keys:
        needle = ' ' + key + ' '
        if needle in padded:
            found.append(lookup[key])
            # blank out the matched span so shorter keys can't re-match it
            padded = padded.replace(needle, ' # ')
    return found


results = []
matched = 0
for item in items:
    text = item['item_name'] + ' . ' + ' '.join(item.get('paragraphs', []))
    components = extract(text)
    results.append(components)
    if components:
        matched += 1

json.dump(results, open('extracted_components.json', 'w'), indent=1)

print(f'{matched}/{len(items)} items matched at least one component')
print(f'{sum(len(r) for r in results)} total component matches')
print()
print('per-venue coverage:')
per = collections.defaultdict(lambda: [0, 0])
for item, comps in zip(items, results):
    venue = item['category_label'].replace(' Secret Menu', '').strip()
    per[venue][0] += 1
    if comps:
        per[venue][1] += 1
for venue, (total, hit) in sorted(per.items(), key=lambda x: -x[1][1]):
    print(f'  {venue:18s} {hit:3d}/{total}')
