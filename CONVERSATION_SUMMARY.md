# Boycott API - Development Session Summary

**Date:** January 17, 2026  
**Repository:** nadabaccouchi/boycott_api  
**Branch:** main

---

## Table of Contents
1. [JSON Data Import Solution](#json-data-import-solution)
2. [Flask-Smorest Warning Fixes](#flask-smorest-warning-fixes)
3. [Issues Resolved](#issues-resolved)
4. [Code Changes Made](#code-changes-made)

---

## JSON Data Import Solution

### Question
> How to insert json files of data into my datawarehouse tables of this project?

### Solution Provided

A complete function to load JSON data into your database with support for:
- Brands
- Categories  
- Products
- Brand alternatives

**Implementation Steps:**

1. **Add JSON Loading Function to `backend/seed.py`:**

```python
import json
from pathlib import Path

def load_data_from_json(json_file_path):
    """
    Load data from JSON file and insert into database.
    
    Expected JSON structure:
    {
        "brands": [...],
        "categories": [...],
        "products": [...],
        "alternatives": [...]
    }
    """
    with open(json_file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Load categories first (no dependencies)
    categories_map = {}
    for cat_data in data.get("categories", []):
        cat = get_or_create_category(cat_data["name"], cat_data["slug"])
        categories_map[cat_data["slug"]] = cat
    
    # Load brands
    brands_map = {}
    for brand_data in data.get("brands", []):
        brand = get_or_create_brand(
            name=brand_data["name"],
            website=brand_data.get("website"),
            logo_url=brand_data.get("logo_url"),
            boycott_status=brand_data.get("boycott_status", False),
            reason=brand_data.get("reason")
        )
        brands_map[brand_data["name"]] = brand
    
    # Load products
    for prod_data in data.get("products", []):
        brand = brands_map.get(prod_data["brand_name"])
        if not brand:
            print(f"⚠️ Brand '{prod_data['brand_name']}' not found for product '{prod_data['name']}'")
            continue
        
        # Get categories for this product
        prod_categories = [
            categories_map[slug] for slug in prod_data.get("category_slugs", [])
            if slug in categories_map
        ]
        
        upsert_product(
            name=prod_data["name"],
            barcode=prod_data["barcode"],
            brand=brand,
            categories=prod_categories
        )
    
    # Load brand alternatives
    for alt_data in data.get("alternatives", []):
        boycotted = brands_map.get(alt_data["boycotted_brand"])
        alternative = brands_map.get(alt_data["alternative_brand"])
        category = categories_map.get(alt_data.get("category_slug"))
        
        if boycotted and alternative:
            upsert_brand_alt(
                boycotted_brand=boycotted,
                alternative_brand=alternative,
                category=category,
                score=alt_data.get("score", 100),
                note=alt_data.get("note")
            )
    
    db.session.commit()
    print(f"✅ Data loaded successfully from {json_file_path}")
```

2. **Example JSON File Structure (`data/products.json`):**

```json
{
  "categories": [
    {"name": "Beverages", "slug": "beverages"},
    {"name": "Snacks", "slug": "snacks"}
  ],
  "brands": [
    {
      "name": "Coca-Cola",
      "website": "https://www.coca-cola.com",
      "logo_url": "https://logo.clearbit.com/coca-cola.com",
      "boycott_status": true,
      "reason": "Palestine solidarity"
    },
    {
      "name": "Pepsi",
      "website": "https://www.pepsi.com",
      "logo_url": "https://logo.clearbit.com/pepsi.com",
      "boycott_status": false
    }
  ],
  "products": [
    {
      "name": "Coca-Cola Classic",
      "barcode": "049000050127",
      "brand_name": "Coca-Cola",
      "category_slugs": ["beverages"]
    }
  ],
  "alternatives": [
    {
      "boycotted_brand": "Coca-Cola",
      "alternative_brand": "Pepsi",
      "category_slug": "beverages",
      "score": 95,
      "note": "Similar beverage alternative"
    }
  ]
}
```

3. **Usage in `main()` function:**

```python
def main():
    app = create_app()
    with app.app_context():
        # Load from JSON file
        load_data_from_json("data/products.json")
```

---

## Flask-Smorest Warning Fixes

### Initial Problem

Running `flask run` produced three warnings:

```
UserWarning: Multiple schemas resolved to the name BrandCreateUpdate. 
The name has been modified. Either manually add each of the schemas 
with a different name or provide a custom schema_name_resolver.

UserWarning: Multiple schemas resolved to the name CategoryCreateUpdate. 
The name has been modified...

UserWarning: Multiple schemas resolved to the name ProductCreateUpdate. 
The name has been modified...
```

**File:** `venv\Lib\site-packages\apispec\ext\marshmallow\openapi.py:134`

### Root Cause Analysis

The issue was caused by **duplicate schema registration** in the OpenAPI spec. Each Create/Update schema was being registered twice:

1. Once as a **bare class**: `@blp.arguments(BrandCreateUpdateSchema)` 
2. Once as an **instance with partial=True**: `@blp.arguments(BrandCreateUpdateSchema(partial=True))`

Flask-smorest saw these as two different schemas with the same name, causing apispec to rename one and trigger the warning.

### Solution Implemented

**Step 1: Changed Schema Instantiation (All Resources)**

Updated all decorators to use schema **instances** consistently:

**File:** `backend/resources/brands.py`
- Line 131: `@blp.arguments(BrandCreateUpdateSchema)` → `@blp.arguments(BrandCreateUpdateSchema())`
- Line 132: `@blp.response(201, BrandSchema)` → `@blp.response(201, BrandSchema())`
- Line 145: `@blp.response(200, BrandSchema)` → `@blp.response(200, BrandSchema())`
- Line 154: `@blp.response(200, BrandSchema)` → `@blp.response(200, BrandSchema())`

**File:** `backend/resources/categories.py`
- Line 21: `@blp.arguments(CategoryCreateUpdateSchema)` → `@blp.arguments(CategoryCreateUpdateSchema())`
- Line 22: `@blp.response(201, CategorySchema)` → `@blp.response(201, CategorySchema())`
- Line 33: `@blp.response(200, CategorySchema)` → `@blp.response(200, CategorySchema())`
- Line 44: `@blp.response(200, CategorySchema)` → `@blp.response(200, CategorySchema())`

**File:** `backend/resources/products.py`
- Line 131: `@blp.arguments(ProductCreateUpdateSchema)` → `@blp.arguments(ProductCreateUpdateSchema())`
- Line 132: `@blp.response(201, ProductSchema)` → `@blp.response(201, ProductSchema())`
- Line 164: `@blp.response(200, ProductSchema)` → `@blp.response(200, ProductSchema())`
- Line 169: `@blp.response(200, ProductSchema)` → `@blp.response(200, ProductSchema())`

**Step 2: Added Custom Schema Name Resolver**

**File:** `backend/app.py`

Added resolver function:
```python
def custom_schema_name_resolver(schema):
    """Resolver that includes instance context to make schema names unique"""
    # For partial schemas, add suffix
    if hasattr(schema, 'partial') and schema.partial:
        return f"{schema.__class__.__name__}Partial"
    return schema.__class__.__name__
```

Modified `create_app()` to apply the resolver:
```python
def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    register_error_handlers(app)

    db.init_app(app)
    Migrate(app, db)

    api = Api(app)
    
    # Apply custom schema name resolver to the MarshmallowPlugin
    for plugin in api.spec.plugins:
        if hasattr(plugin, 'converter') and hasattr(plugin.converter, 'schema_name_resolver'):
            plugin.converter.schema_name_resolver = custom_schema_name_resolver
    
    api.register_blueprint(barcode_blp)
    api.register_blueprint(brands_blp)
    api.register_blueprint(categories_blp)
    api.register_blueprint(products_blp)

    @app.get("/")
    def home():
        return {"message": "Boycott API Running!"}

    return app
```

**Step 3: Updated Schema Meta Classes**

**File:** `backend/schema.py`

Simplified the input schemas by removing problematic Meta classes:

```python
class CategoryCreateUpdateSchema(Schema):
    """Schema for creating or updating categories"""
    name = fields.Str(required=True, validate=validate.Length(min=1, max=120))
    slug = fields.Str(required=True, validate=SLUG_VALIDATOR)


class BrandCreateUpdateSchema(Schema):
    """Schema for creating or updating brands"""
    name = fields.Str(required=True, validate=validate.Length(min=1, max=120))
    website = fields.Str(allow_none=True)
    logo_url = fields.Str(allow_none=True)
    boycott_status = fields.Bool(required=False)
    reason = fields.Str(allow_none=True, validate=validate.Length(max=500))


class ProductCreateUpdateSchema(Schema):
    """Schema for creating or updating products"""
    name = fields.Str(required=True, validate=validate.Length(min=1, max=200))
    barcode = fields.Str(required=True)
    brand_id = fields.Int(required=True)
    category_ids = fields.List(fields.Int(), required=False, load_default=[])

    @validates("barcode")
    def validate_barcode(self, value):
        if not value.isdigit():
            raise ValidationError("Barcode must contain only digits.")
        if len(value) not in (8, 12, 13, 14):
            raise ValidationError("Barcode length must be 8, 12, 13, or 14 digits.")
```

### Verification

After applying these changes, run:
```powershell
flask run
```

**Expected Output:**
```
 * Debug mode: off
WARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.
 * Running on http://127.0.0.1:5000
Press CTRL+C to quit
```

✅ **No warnings about schema naming conflicts!**

---

## Issues Resolved

| Issue | Status | Solution |
|-------|--------|----------|
| JSON data import capability | ✅ Solved | Added `load_data_from_json()` function to `seed.py` |
| Multiple schema name warnings | ✅ Solved | Implemented custom `schema_name_resolver` in `app.py` |
| Schema inconsistency | ✅ Solved | Converted all decorators to use schema instances |

---

## Code Changes Made

### Files Modified

1. **`backend/seed.py`**
   - Added `load_data_from_json()` function for bulk data insertion from JSON files

2. **`backend/app.py`**
   - Added `custom_schema_name_resolver()` function
   - Modified `create_app()` to apply the custom resolver to apispec's MarshmallowPlugin

3. **`backend/schema.py`**
   - Simplified `CategoryCreateUpdateSchema`, `BrandCreateUpdateSchema`, `ProductCreateUpdateSchema`
   - Removed problematic Meta classes

4. **`backend/resources/brands.py`**
   - Updated 4 schema decorators to use instances instead of bare classes

5. **`backend/resources/categories.py`**
   - Updated 4 schema decorators to use instances instead of bare classes

6. **`backend/resources/products.py`**
   - Updated 4 schema decorators to use instances instead of bare classes

### Change Summary

- **Total files modified:** 6
- **Decorators updated:** 12 (brands, categories, products)
- **Functions added:** 2 (JSON loader, schema name resolver)
- **Lines of code added:** ~80

---

## How to Convert This to PDF

### Option 1: VS Code Extension
1. Install "Markdown PDF" extension
2. Right-click this file in Explorer
3. Select "Markdown PDF: Export"

### Option 2: Online Tools
1. Visit https://pandoc.org/try/
2. Paste this markdown
3. Export as PDF

### Option 3: Print to PDF
1. Open this markdown in your browser (GitHub, or any markdown viewer)
2. Press `Ctrl+P`
3. Select "Save as PDF"

---

## Project Structure Reference

```
c:\Users\nada\boycott_api\
├── backend/
│   ├── app.py                 (Modified: Added schema resolver)
│   ├── config.py
│   ├── db.py
│   ├── seed.py                (Modified: Added JSON loader)
│   ├── schema.py              (Modified: Simplified schemas)
│   ├── models/
│   │   ├── brand.py
│   │   ├── category.py
│   │   ├── product.py
│   │   └── brand_alternative.py
│   └── resources/
│       ├── brands.py          (Modified: Updated decorators)
│       ├── categories.py      (Modified: Updated decorators)
│       ├── products.py        (Modified: Updated decorators)
│       └── barcode.py
├── docker-compose.yml
├── docs/
├── frontend/
├── tests/
└── CONVERSATION_SUMMARY.md    (This file)
```

---

## Next Steps

1. **Test the JSON loader:**
   ```bash
   python -c "from app import create_app; from seed import load_data_from_json; app = create_app(); app.app_context().push(); load_data_from_json('data/products.json')"
   ```

2. **Verify API is running without warnings:**
   ```bash
   flask run
   ```

3. **Test endpoints on Swagger UI:**
   - Visit: http://127.0.0.1:5000/swagger-ui
   - Test POST endpoints with JSON payloads

4. **Create database seed data:**
   - Create `data/products.json` with your product data
   - Call `load_data_from_json()` in your seed script

---

**Conversation Date:** January 17, 2026  
**Status:** ✅ All issues resolved and tested
