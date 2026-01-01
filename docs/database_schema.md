# WhatCanICook Database Schema

## Overview
SQLite database with 5 tables to store recipes, ingredients, and their relationships.

## Tables

### 1. recipes
Stores recipe metadata.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT | Unique recipe ID |
| name | TEXT | NOT NULL | Recipe name |
| description | TEXT | NULL | Optional recipe description |
| cook_time_mins | INTEGER | NULL | Approximate cook time in minutes |
| source_url | TEXT | NULL | Instagram/web source URL |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | When recipe was added |

### 2. ingredients
Master list of all ingredients with staple flag.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT | Unique ingredient ID |
| name | TEXT | UNIQUE NOT NULL | Ingredient name (lowercase, singular) |
| is_staple | INTEGER | DEFAULT 0 | 1 = always in kitchen, 0 = not staple |

### 3. recipe_ingredients
Junction table linking recipes to ingredients (many-to-many).

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT | Unique record ID |
| recipe_id | INTEGER | FOREIGN KEY (recipes.id) | Recipe reference |
| ingredient_id | INTEGER | FOREIGN KEY (ingredients.id) | Ingredient reference |
| quantity | TEXT | NULL | Optional quantity (e.g., "2", "1/2") |
| unit | TEXT | NULL | Optional unit (e.g., "cups", "tbsp") |

### 4. tags
Categorization tags for recipes.

| Column | Type |

### 4. tags
Categorization tags for recipes.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT | Unique tag ID |
| name | TEXT | UNIQUE NOT NULL | Tag name |
| category | TEXT | NULL | Tag category (e.g., "cuisine", "speed", "meal_type") |

### 5. recipe_tags
Junction table linking recipes to tags (many-to-many).

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| recipe_id | INTEGER | FOREIGN KEY (recipes.id) | Recipe reference |
| tag_id | INTEGER | FOREIGN KEY (tags.id) | Tag reference |
| PRIMARY KEY | | (recipe_id, tag_id) | Composite primary key |

## Relationships
```
recipes ←--→ recipe_ingredients ←--→ ingredients
   ↓              (many-to-many)
   ↓
recipe_tags ←--→ tags
(many-to-many)
```

## Example Data

**Recipe: Pasta Carbonara**
- recipes: {id: 1, name: "Pasta Carbonara", cook_time_mins: 20, ...}
- ingredients: 
  - {id: 1, name: "pasta", is_staple: 1}
  - {id: 2, name: "eggs", is_staple: 0}
  - {id: 3, name: "pancetta", is_staple: 0}
  - {id: 4, name: "hard cheese", is_staple: 0}
- recipe_ingredients:
  - {recipe_id: 1, ingredient_id: 1}
  - {recipe_id: 1, ingredient_id: 2}
  - {recipe_id: 1, ingredient_id: 3}
  - {recipe_id: 1, ingredient_id: 4}
- tags:
  - {id: 1, name: "Pasta", category: "meal_type"}
  - {id: 2, name: "Quick<20mins", category: "speed"}
  - {id: 3, name: "Classics", category: "collection"}
- recipe_tags:
  - {recipe_id: 1, tag_id: 1}
  - {recipe_id: 1, tag_id: 2}
  - {recipe_id: 1, tag_id: 3}

## Design Decisions

1. **is_staple flag on ingredients**: Simpler than separate staples table, easier to query
2. **Nullable quantity/unit**: Future-proofing without forcing precision now
3. **Composite PK on recipe_tags**: No separate ID needed, natural key suffices
4. **Lowercase ingredient names**: Consistency for matching ("Eggs" vs "eggs")
5. **Tag categories**: Optional grouping for UI filtering (e.g., show all "cuisine" tags)

## Normalization
- 3NF (Third Normal Form) achieved
- No redundant data
- Proper foreign key constraints
- Many-to-many relationships handled with junction tables
