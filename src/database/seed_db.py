"""
Seed database with initial recipe data from recipes_collection.txt
"""

from src.database.models import Recipe, Ingredient, RecipeIngredient, Tag, RecipeTag, get_session
from pathlib import Path

RECIPES_FILE = Path(__file__).parent.parent.parent / "data" / "recipes_collection.txt"


def parse_recipes_file():
    """Parse recipes_collection.txt and return structured data"""
    with open(RECIPES_FILE, 'r') as f:
        content = f.read()
    
    recipes = []
    recipe_blocks = content.strip().split('---')
    
    for block in recipe_blocks:
        if not block.strip():
            continue
            
        lines = [line.strip() for line in block.strip().split('\n') if line.strip()]
        recipe_data = {}
        
        for line in lines:
            if line.startswith('Recipe:'):
                recipe_data['name'] = line.replace('Recipe:', '').strip()
            elif line.startswith('Cook Time:'):
                recipe_data['cook_time'] = int(line.replace('Cook Time:', '').strip())
            elif line.startswith('Ingredients:'):
                ingredients = line.replace('Ingredients:', '').strip()
                recipe_data['ingredients'] = [ing.strip() for ing in ingredients.split(',')]
            elif line.startswith('Tags:'):
                tags = line.replace('Tags:', '').strip()
                recipe_data['tags'] = [tag.strip() for tag in tags.split(',')]
            elif line.startswith('Source:'):
                recipe_data['source'] = line.replace('Source:', '').strip()
        
        if recipe_data.get('name'):
            recipes.append(recipe_data)
    
    return recipes


def seed_database():
    """Populate database with recipes from file"""
    session = get_session()
    
    try:
        # Parse recipes file
        recipes_data = parse_recipes_file()
        print(f"Parsed {len(recipes_data)} recipes from file\n")
        
        # Track all ingredients and tags
        all_ingredients = {}
        all_tags = {}
        
        # First pass: collect all unique ingredients and tags
        for recipe_data in recipes_data:
            for ing_name in recipe_data.get('ingredients', []):
                ing_lower = ing_name.lower()
                if ing_lower not in all_ingredients:
                    all_ingredients[ing_lower] = Ingredient(name=ing_lower, is_staple=0)
            
            for tag_name in recipe_data.get('tags', []):
                if tag_name not in all_tags:
                    all_tags[tag_name] = Tag(name=tag_name)
        
        # Insert all ingredients
        print(f"Inserting {len(all_ingredients)} unique ingredients...")
        session.add_all(all_ingredients.values())
        session.commit()
        
        # Insert all tags
        print(f"Inserting {len(all_tags)} unique tags...")
        session.add_all(all_tags.values())
        session.commit()
        
        # Second pass: insert recipes and relationships
        print(f"\nInserting recipes...")
        for recipe_data in recipes_data:
            # Create recipe
            recipe = Recipe(
                name=recipe_data['name'],
                cook_time_mins=recipe_data.get('cook_time'),
                source_url=recipe_data.get('source'),
                description=None
            )
            session.add(recipe)
            session.flush()  # Get recipe ID
            
            # Link ingredients
            for ing_name in recipe_data.get('ingredients', []):
                ing_lower = ing_name.lower()
                ingredient = all_ingredients[ing_lower]
                recipe_ing = RecipeIngredient(
                    recipe_id=recipe.id,
                    ingredient_id=ingredient.id
                )
                session.add(recipe_ing)
            
            # Link tags
            for tag_name in recipe_data.get('tags', []):
                tag = all_tags[tag_name]
                recipe_tag = RecipeTag(
                    recipe_id=recipe.id,
                    tag_id=tag.id
                )
                session.add(recipe_tag)
            
            print(f"  ✓ {recipe.name}")
        
        session.commit()
        print(f"\n✓ Successfully seeded database with {len(recipes_data)} recipes!")
        
        # Print summary
        print("\nDatabase Summary:")
        print(f"  Recipes: {session.query(Recipe).count()}")
        print(f"  Ingredients: {session.query(Ingredient).count()}")
        print(f"  Tags: {session.query(Tag).count()}")
        
    except Exception as e:
        session.rollback()
        print(f"✗ Error seeding database: {e}")
        raise
    finally:
        session.close()


if __name__ == "__main__":
    print("Seeding WhatCanICook database...\n")
    seed_database()
