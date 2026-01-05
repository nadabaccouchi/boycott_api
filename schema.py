from marshmallow import Schema, fields

class AlternativeSchema(Schema):
    name = fields.Str()
    website = fields.Str()
    logo_url = fields.Str()

class CategorySchema(Schema):
    name = fields.Str()
    slug = fields.Str()

class BrandSchema(Schema):
    name = fields.Str()
    website = fields.Str()
    logo_url = fields.Str()
    boycott_status = fields.Bool()
    reason = fields.Str()

class ProductSchema(Schema):
    name = fields.Str()
    barcode = fields.Str()
    brand = fields.Nested(BrandSchema)
    categories = fields.List(fields.Nested(CategorySchema))
    alternatives = fields.List(fields.Nested(AlternativeSchema))
