"""
Recipe Matcher - core matching algorithm for WhatCanICook.
Takes user ingredients, combines with staples, scores all recipes by match %.
"""

import sys
from pathlib import Path

# So we can import from src.database
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.database.models import get_session, Recipe, Ingredient, RecipeIngredient


def get_staple_ids(session):
    """Returns a set of ingredient IDs marked as staples."""
    staples = session.query(Ingredient).filter(Ingredient.is_staple == 1).all()
    return {s.id for s in staples}


def match_user_input_to_db(session, user_ingredients):
    """
    Takes a list of ingredient strings from the user,
    matches them to ingredient IDs in the database (case-insensitive).
    Returns a set of matched IDs and a list of anything that didn't match.
    """
    matched_ids = set()
    unmatched = []

    for item in user_ingredients:
        item_clean = item.strip().lower()
        result = (
            session.query(Ingredient)
            .filter(Ingredient.name.ilike(f"%{item_clean}%"))
            .first()
        )
        if result:
            matched_ids.add(result.id)
        else:
            unmatched.append(item.strip())

    return matched_ids, unmatched


def calculate_matches(session, user_ingredient_ids):
    """
    Scores every recipe in the DB.
    User's available ingredients = their input + all staples.
    Score = (available ingredients in recipe / total ingredients in recipe) * 100
    Returns a list of dicts sorted by score descending.
    """
    available_ids = user_ingredient_ids | get_staple_ids(session)

    recipes = session.query(Recipe).all()
    results = []

    for recipe in recipes:
        # Get all ingredient IDs for this recipe
        recipe_ingredient_ids = {
            ri.ingredient_id for ri in recipe.ingredients
        }

        total = len(recipe_ingredient_ids)
        if total == 0:
            continue  # skip any recipe with no ingredients

        matched = recipe_ingredient_ids & available_ids  # set intersection
        missing = recipe_ingredient_ids - available_ids

        score = round((len(matched) / total) * 100, 1)

        # Get the names of missing ingredients for display
        missing_names = [
            session.query(Ingredient).get(mid).name for mid in missing
        ]

        results.append({
            "id": recipe.id,
            "name": recipe.name,
            "score": score,
            "matched": len(matched),
            "total": total,
            "missing": missing_names,
        })

    # Sort by score, highest first
    results.sort(key=lambda x: x["score"], reverse=True)
    return results


def find_recipes(user_ingredients, min_score=0):
    """
    Main entry point. Takes a list of ingredient strings,
    returns ranked recipe matches above the min_score threshold.
    """
    session = get_session()

    matched_ids, unmatched = match_user_input_to_db(session, user_ingredients)

    if unmatched:
        print(f"\n⚠️  These ingredients weren't found in the DB: {unmatched}")

    if not matched_ids:
        print("\n❌ None of your ingredients matched anything in the database.")
        session.close()
        return []

    results = calculate_matches(session, matched_ids)

    # Filter by minimum score
    results = [r for r in results if r["score"] >= min_score]

    session.close()
    return results


# Quick terminal test when you run this file directly
if __name__ == "__main__":
    print("=== WhatCanICook - Recipe Matcher ===\n")

    # Test with a few ingredients
    test_input = ["chicken", "rice", "garlic"]
    print(f"Searching with: {test_input}\n")

    results = find_recipes(test_input, min_score=40)

    if results:
        for r in results:
            print(f"  {r['score']:>5}%  {r['name']}")
            if r["missing"]:
                print(f"         Missing: {', '.join(r['missing'])}")
    else:
        print("No matches found.")
