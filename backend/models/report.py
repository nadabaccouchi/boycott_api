# FILE: models/report.py

from db import db
from datetime import datetime
from enum import Enum as PyEnum


class ReportStatus(PyEnum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class Report(db.Model):
    __tablename__ = "reports"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    product_id = db.Column(
        db.Integer, db.ForeignKey("products.id"), nullable=True, index=True
    )
    barcode = db.Column(db.String(14), nullable=True)
    message = db.Column(db.Text, nullable=False)
    evidence_url = db.Column(db.String(500), nullable=True)
    status = db.Column(
        db.String(20),
        default=ReportStatus.PENDING.value,
        nullable=False,
        index=True,
    )
    admin_note = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relationships
    product = db.relationship("Product", backref="reports", lazy=True)

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "product_id": self.product_id,
            "barcode": self.barcode,
            "message": self.message,
            "evidence_url": self.evidence_url,
            "status": self.status,
            "admin_note": self.admin_note,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
