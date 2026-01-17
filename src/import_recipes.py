"""
Import recipes from Notion CSV export into WhatCanICook database.
"""
import csv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database.models import Base, Recipe, Ingredient, RecipeIngredient, Tag, RecipeTag

# Staples that are always available
STAPLES = {
    'Salt', 'Black Pepper', 'Paprika Sweet', 'Paprika Smoked', 
    'Tumeric', 'Curry Powder', 'Gram Masala', 'Cumin', 'Allspice',
    'Onions', 'Garlic', 'Milk', 'Pasta', 'Rice', 'Cous Cous', 
    'Quinoa', 'Polenta'
}

# Create database connection
engine = create_engine('sqlite:///whatcanicook.db')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

def normalize_ingredient_name(name):
    """Normalize ingredient names for matching staples."""
    # Handle common variations
    name = name.strip()
    
    # Map variations to standard names
    variations = {
        'Black Peppercorn': 'Black Pepper',
        'Onion': 'Onions',
        'Red Onion': 'Onions',
        'Spring Onion': 'Onions',
        'Paprika Smokey': 'Paprika Smoked',
    }
    
    return variations.get(name, name)

def get_or_create_ingredient(name):
    """Get existing ingredient or create new one."""
    # Check if ingredient exists
    ingredient = session.query(Ingredient).filter_by(name=name).first()
    
    if not ingredient:
        # Check if it's a staple
        normalized = normalize_ingredient_name(name)
        is_staple = normalized in STAPLES
        
        ingredient = Ingredient(name=name, is_staple=is_staple)
        session.add(ingredient)
        print(f"  Created ingredient: {name} (staple: {is_staple})")
    
    return ingredient

def get_or_create_tag(name):
    """Get existing tag or create new one."""
    tag = session.query(Tag).filter_by(name=name).first()
    
    if not tag:
        tag = Tag(name=name)
        session.add(tag)
        print(f"  Created tag: {name}")
    
    return tag

def import_recipes(csv_path):
    """Import all recipes from CSV."""
    recipes_imported = 0
    
    with open(csv_path, 'r', encoding='utf-8-sig') as file:
        reader = csv.DictReader(file)
        
        for row in reader:
            # Skip empty rows
            if not row['Name'] or not row['Name'].strip():
                continue
            
            recipe_name = row['Name'].strip()
            print(f"\nImporting: {recipe_name}")
            
            # Check if recipe already exists
            existing = session.query(Recipe).filter_by(name=recipe_name).first()
            if existing:
                print(f"  Recipe already exists, skipping...")
                continue
            
            # Create recipe
            recipe = Recipe(
                name=recipe_name,
                source_url=row['Files & media'].strip() if row['Files & media'] else None,
                description=row['Text'].strip() if row['Text'] else None
            )
            session.add(recipe)
            
            # Add tags
            if row['Tags'] and row['Tags'].strip():
                tag_names = [t.strip() for t in row['Tags'].split(',')]
                for tag_name in tag_names:
                    tag = get_or_create_tag(tag_name)
                    recipe_tag = RecipeTag(recipe=recipe, tag=tag)
                    session.add(recipe_tag)
            
            # Add ingredients
            if row['Select'] and row['Select'].strip():
                ingredient_names = [i.strip() for i in row['Select'].split(',')]
                for ingredient_name in ingredient_names:
                    ingredient = get_or_create_ingredient(ingredient_name)
                    recipe_ingredient = RecipeIngredient(
                        recipe=recipe,
                        ingredient=ingredient
                    )
                    session.add(recipe_ingredient)
            
            recipes_imported += 1
    
    # Commit all changes
    session.commit()
    print(f"\n{'='*50}")
    print(f"Import complete! {recipes_imported} recipes imported.")
    print(f"{'='*50}")
    
    # Print summary
    total_recipes = session.query(Recipe).count()
    total_ingredients = session.query(Ingredient).count()
    total_staples = session.query(Ingredient).filter_by(is_staple=True).count()
    total_tags = session.query(Tag).count()
    
    print(f"\nDatabase summary:")
    print(f"  Total recipes: {total_recipes}")
    print(f"  Total ingredients: {total_ingredients}")
    print(f"  Staple ingredients: {total_staples}")
    print(f"  Total tags: {total_tags}")

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python import_recipes.py <path_to_csv>")
        sys.exit(1)
    
    csv_path = sys.argv[1]
    import_recipes(csv_path)
    session.close()
