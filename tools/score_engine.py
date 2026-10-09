import json

venues = json.load(open('venues_tagged.json'))

# Weight for each match tier
EXACT_MATCH = 1.0
SAME_SUBCATEGORY = 0.85
SAME_CATEGORY = 0.4
NO_MATCH = 0.0


def get_venue(venue_id):
    for v in venues:
        if v['id'] == venue_id:
            return v
    raise ValueError(f"No venue with id {venue_id}")


def score_ingredient(target_ing, candidate_inventory):
    """
    Score how well a single target ingredient can be matched
    against a candidate venue's inventory.
    Returns (score, best_match_name, tier_label)
    """
    exact = [i for i in candidate_inventory if i['name'] == target_ing['name']]
    if exact:
        return EXACT_MATCH, exact[0]['name'], "exact"

    same_sub = [i for i in candidate_inventory if i['subcategory'] == target_ing['subcategory']]
    if same_sub:
        return SAME_SUBCATEGORY, same_sub[0]['name'], "same_subcategory"

    same_cat = [i for i in candidate_inventory if i['category'] == target_ing['category']]
    if same_cat:
        return SAME_CATEGORY, same_cat[0]['name'], "same_category"

    return NO_MATCH, None, "no_match"


def score_recipe_at_venue(target_venue_id, recipe_name, candidate_venue_id):
    """
    Given a recipe that officially exists at target_venue_id,
    score how closely candidate_venue_id could recreate it
    using only candidate_venue_id's own inventory.
    """
    target_venue = get_venue(target_venue_id)
    candidate_venue = get_venue(candidate_venue_id)

    recipe = next((r for r in target_venue['recipes'] if r['name'] == recipe_name), None)
    if recipe is None:
        raise ValueError(f"No recipe '{recipe_name}' found at {target_venue_id}")

    breakdown = []
    total = 0.0
    for ing in recipe['ingredients']:
        score, match_name, tier = score_ingredient(ing, candidate_venue['inventory'])
        breakdown.append({
            "target_ingredient": ing['name'],
            "category": ing['category'],
            "subcategory": ing['subcategory'],
            "matched_with": match_name,
            "tier": tier,
            "score": score
        })
        total += score

    overall = total / len(recipe['ingredients']) if recipe['ingredients'] else 0
    return {
        "target_venue": target_venue['name'],
        "recipe": recipe_name,
        "candidate_venue": candidate_venue['name'],
        "overall_score": round(overall, 3),
        "breakdown": breakdown
    }


def rank_all_venues_for_recipe(target_venue_id, recipe_name):
    """
    Score every other venue's ability to recreate a given recipe,
    ranked best to worst.
    """
    results = []
    for v in venues:
        if v['id'] == target_venue_id:
            continue
        result = score_recipe_at_venue(target_venue_id, recipe_name, v['id'])
        results.append((v['name'], result['overall_score']))
    results.sort(key=lambda x: x[1], reverse=True)
    return results


if __name__ == "__main__":
    # Test: how close can other venues get to a Wendy's Dave's Single?
    ranking = rank_all_venues_for_recipe('wendys', "Dave's Single")
    print("Recreating Wendy's Dave's Single, ranked by other venues:\n")
    for name, score in ranking:
        print(f"  {name:20s} {score:.1%}")

    print("\nDetailed breakdown for McDonald's attempting it:\n")
    detail = score_recipe_at_venue('wendys', "Dave's Single", 'mcdonalds')
    for item in detail['breakdown']:
        print(f"  {item['target_ingredient']:25s} -> {str(item['matched_with']):25s} [{item['tier']}] {item['score']}")
    print(f"\n  Overall: {detail['overall_score']:.1%}")
