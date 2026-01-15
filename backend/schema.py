from marshmallow import Schema, fields

class CategorySchema(Schema):
    id = fields.Int()
    name = fields.Str()
    slug = fields.Str()

class BrandSchema(Schema):
    id = fields.Int()
    name = fields.Str()
    website = fields.Str(allow_none=True)
    logo_url = fields.Str(allow_none=True)
    boycott_status = fields.Bool()
    reason = fields.Str(allow_none=True)

class ProductSchema(Schema):
    id = fields.Int()
    name = fields.Str()
    barcode = fields.Str()
    brand = fields.Nested(BrandSchema)
    categories = fields.List(fields.Nested(CategorySchema))

class BarcodeResultSchema(Schema):
    barcode = fields.Str()
    product_name = fields.Str()
    brand = fields.Nested(BrandSchema)
    alternatives = fields.List(fields.Nested(BrandSchema))
