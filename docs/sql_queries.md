# WhatCanICook - Handy SQL Queries

Run these from project root using: `sqlite3 data/recipes.db "QUERY"`

## Top 5 Essential Queries

### 1. Show recipe with all ingredients
```sql
SELECT r.name as recipe, i.name as ingredient 
FROM recipes r 
JOIN recipe_ingredients ri ON r.id = ri.recipe_id 
JOIN ingredients i ON i.id = ri.ingredient_id 
WHERE r.name = 'Pasta Carbonara';
```

### 2. List all recipes with cook times
```sql
SELECT id, name, cook_time_mins 
FROM recipes 
ORDER BY cook_time_mins;
```

### 3. Show all staple ingredients
```sql
SELECT name 
FROM ingredients 
WHERE is_staple = 1;
```

### 4. Find recipes by tag (e.g., "Pasta")
```sql
SELECT r.name, r.cook_time_mins 
FROM recipes r 
JOIN recipe_tags rt ON r.id = rt.recipe_id 
JOIN tags t ON rt.tag_id = t.id 
WHERE t.name = 'Pasta';
```

### 5. Count ingredients per recipe
```sql
SELECT r.name, COUNT(ri.ingredient_id) as num_ingredients 
FROM recipes r 
JOIN recipe_ingredients ri ON r.id = ri.recipe_id 
GROUP BY r.name 
ORDER BY num_ingredients DESC;
```

## Bonus Queries

### Show recipe with ingredients AND tags
```sql
SELECT r.name as recipe, 
       GROUP_CONCAT(DISTINCT i.name) as ingredients,
       GROUP_CONCAT(DISTINCT t.name) as tags
FROM recipes r 
LEFT JOIN recipe_ingredients ri ON r.id = ri.recipe_id 
LEFT JOIN ingredients i ON ri.ingredient_id = i.id
LEFT JOIN recipe_tags rt ON r.id = rt.recipe_id
LEFT JOIN tags t ON rt.tag_id = t.id
WHERE r.name = 'Pasta Carbonara'
GROUP BY r.name;
```

### Find recipes containing specific ingredient
```sql
SELECT r.name 
FROM recipes r 
JOIN recipe_ingredients ri ON r.id = ri.recipe_id 
JOIN ingredients i ON ri.ingredient_id = i.id 
WHERE i.name = 'eggs';
```

### Show all tags with recipe counts
```sql
SELECT t.name, COUNT(rt.recipe_id) as recipe_count 
FROM tags t 
LEFT JOIN recipe_tags rt ON t.id = rt.recipe_id 
GROUP BY t.name 
ORDER BY recipe_count DESC;
```
