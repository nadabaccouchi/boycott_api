# FILE: schemas.py
from marshmallow import Schema, fields, validates, validates_schema, ValidationError, validate

# Common validators
SLUG_VALIDATOR = validate.Regexp(
    r"^[a-z0-9]+(?:-[a-z0-9]+)*$",
    error="Invalid slug format. Use lowercase letters/numbers and hyphens (e.g. 'soft-drinks')."
)

# ------------------------
# OUTPUT (Response) Schemas
# ------------------------

class CategorySchema(Schema):
    id = fields.Int(dump_only=True, metadata={"example": 1})
    name = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=120),
        metadata={"example": "Soft Drinks"},
    )
    slug = fields.Str(
        required=True,
        validate=SLUG_VALIDATOR,
        metadata={"example": "soft-drinks"},
    )


class BrandSchema(Schema):
    id = fields.Int(dump_only=True, metadata={"example": 10})
    name = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=120),
        metadata={"example": "Coca-Cola"},
    )
    website = fields.Str(allow_none=True, metadata={"example": "https://www.coca-cola.com"})
    logo_url = fields.Str(allow_none=True, metadata={"example": "https://example.com/logo.png"})
    boycott_status = fields.Bool(required=True, metadata={"example": True})
    reason = fields.Str(
        allow_none=True,
        validate=validate.Length(max=500),
        metadata={"example": "Supports X"},
    )


class ProductSchema(Schema):
    id = fields.Int(dump_only=True, metadata={"example": 55})
    name = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=200),
        metadata={"example": "Coca-Cola Classic"},
    )

    # Keep barcode as string (good because barcodes can start with 0)
    barcode = fields.Str(required=True, metadata={"example": "6194002400707"})

    @validates("barcode")
    def validate_barcode(self, value):
        if not value.isdigit():
            raise ValidationError("Barcode must contain only digits.")
        if len(value) not in (8, 12, 13, 14):
            raise ValidationError("Barcode length must be 8, 12, 13, or 14 digits.")

    brand = fields.Nested(BrandSchema, required=True)
    categories = fields.List(fields.Nested(CategorySchema), required=True)


class BarcodeResultSchema(Schema):
    barcode = fields.Str(required=True, metadata={"example": "6194002400707"})
    product_name = fields.Str(required=True, metadata={"example": "Coca-Cola Classic"})
    brand = fields.Nested(BrandSchema, required=True)
    alternatives = fields.List(fields.Nested(BrandSchema), required=True)

# ------------------------
# INPUT (Create/Update) Schemas
# ------------------------

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


# ========================
# USER & AUTH SCHEMAS
# ========================

class UserSchema(Schema):
    """Output schema for users"""
    id = fields.Int(dump_only=True, metadata={"example": 1})
    username = fields.Str(dump_only=True, metadata={"example": "john_doe"})
    email = fields.Email(dump_only=True, metadata={"example": "john@example.com"})
    role = fields.Str(dump_only=True, metadata={"example": "user"})
    created_at = fields.DateTime(dump_only=True, metadata={"example": "2025-01-17T10:00:00"})


class UserRegisterSchema(Schema):
    """Schema for user registration"""
    username = fields.Str(required=True, validate=validate.Length(min=3, max=80))
    email = fields.Email(required=True)
    password = fields.Str(required=True, validate=validate.Length(min=8), load_only=True)


class UserLoginSchema(Schema):
    """Schema for user login"""
    email = fields.Email(required=True)
    password = fields.Str(required=True, load_only=True)


class AuthResponseSchema(Schema):
    """Schema for login/register response"""
    access_token = fields.Str(required=True, metadata={"example": "eyJ0eXAiOiJKV1QiLCJhbGc..."})
    user = fields.Nested(UserSchema, required=True)


# ========================
# REPORT SCHEMAS
# ========================

class ReportSchema(Schema):
    """Output schema for reports"""
    id = fields.Int(dump_only=True, metadata={"example": 1})
    user_id = fields.Int(dump_only=True, metadata={"example": 1})
    product_id = fields.Int(allow_none=True, metadata={"example": 55})
    barcode = fields.Str(allow_none=True, metadata={"example": "6194002400707"})
    message = fields.Str(required=True, metadata={"example": "Product contains controversial ingredient"})
    evidence_url = fields.Str(allow_none=True, metadata={"example": "https://example.com/evidence.pdf"})
    status = fields.Str(required=True, validate=validate.OneOf(["pending", "approved", "rejected"]), metadata={"example": "pending"})
    admin_note = fields.Str(allow_none=True, metadata={"example": "Verified and approved"})
    created_at = fields.DateTime(dump_only=True, metadata={"example": "2025-01-17T10:00:00"})
    updated_at = fields.DateTime(dump_only=True, metadata={"example": "2025-01-17T10:00:00"})


class ReportCreateSchema(Schema):
    """Schema for creating a report (product_id OR barcode required)"""
    product_id = fields.Int(allow_none=True, metadata={"example": 55})
    barcode = fields.Str(allow_none=True, validate=validate.Regexp(r"^\d{8,14}$", error="Barcode must be 8-14 digits"), metadata={"example": "6194002400707"})
    message = fields.Str(required=True, validate=validate.Length(min=10, max=2000), metadata={"example": "Product contains controversial ingredient"})
    evidence_url = fields.Str(allow_none=True, validate=validate.URL(), metadata={"example": "https://example.com/evidence.pdf"})

    @validates_schema
    def validate_product_or_barcode(self, data, **kwargs):
        """Ensure either product_id or barcode is provided"""
        if not data.get("product_id") and not data.get("barcode"):
            raise ValidationError("Either product_id or barcode must be provided.")


class ReportUpdateSchema(Schema):
    """Schema for updating a report (admin only)"""
    status = fields.Str(
        required=True,
        validate=validate.OneOf(["approved", "rejected"]),
        metadata={"example": "approved"}
    )
    admin_note = fields.Str(
        allow_none=True,
        validate=validate.Length(max=500),
        metadata={"example": "Verified against official sources"}
    )
