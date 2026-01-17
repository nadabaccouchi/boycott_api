# FILE: resources/reports.py

from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask import request
from sqlalchemy.exc import IntegrityError

from db import db
from models.report import Report
from models.product import Product
from schema import ReportSchema, ReportCreateSchema, ReportUpdateSchema
import auth_utils as auth_module

blp = Blueprint("Reports", __name__, description="Reports endpoints")

# Updated endpoints with role-based access control
@blp.route("/reports")
class ReportList(MethodView):
    @blp.response(200, ReportSchema(many=True))
    @blp.doc(security=[{"BearerAuth": []}])
    def get(self):
        """
        GET /reports
        Authenticated users only.
        """
        auth_module.require_authenticated_user()
        status = request.args.get("status")
        query = Report.query

        if status:
            if status not in ["pending", "approved", "rejected"]:
                abort(400, message="Invalid status. Must be: pending, approved, or rejected.")
            query = query.filter_by(status=status)

        reports = query.order_by(Report.created_at.desc()).all()
        return reports

    @blp.arguments(ReportCreateSchema())
    @blp.doc(security=[{"BearerAuth": []}])
    @blp.response(201, ReportSchema())
    def post(self, data):
        """
        POST /reports
        Authenticated users only.
        """
        user = auth_module.require_authenticated_user()

        product_id = data.get("product_id")
        barcode = data.get("barcode")

        if not product_id and not barcode:
            abort(400, message="Either product_id or barcode must be provided.")

        if product_id:
            product = Product.query.get(product_id)
            if not product:
                abort(404, message="Product not found.")

        report = Report(
            user_id=user.id,
            product_id=product_id,
            barcode=barcode,
            message=data["message"],
            evidence_url=data.get("evidence_url"),
            status="pending",
        )

        db.session.add(report)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            abort(400, message="Failed to create report.")

        return report


@blp.route("/reports/mine")
class MyReports(MethodView):
    @blp.response(200, ReportSchema(many=True))
    @blp.doc(security=[{"BearerAuth": []}])
    def get(self):
        """
        GET /reports/mine
        Authenticated users only.
        """
        user = auth_module.require_authenticated_user()
        reports = Report.query.filter_by(user_id=user.id).order_by(
            Report.created_at.desc()
        ).all()
        return reports


@blp.route("/reports/<int:report_id>")
class ReportDetail(MethodView):
    @blp.response(200, ReportSchema())
    @blp.doc(security=[{"BearerAuth": []}])
    def get(self, report_id):
        """
        GET /reports/{id}
        Authenticated users only.
        """
        user = auth_module.require_authenticated_user()
        report = Report.query.get(report_id)
        if not report:
            abort(404, message="Report not found.")
        return report

    @blp.arguments(ReportUpdateSchema())
    @blp.doc(security=[{"BearerAuth": []}])
    @blp.response(200, ReportSchema())
    def put(self, data, report_id):
        """
        PUT /reports/{id}
        Admin only.
        """
        admin = auth_module.require_admin()
        report = Report.query.get(report_id)
        if not report:
            abort(404, message="Report not found.")

        report.status = data["status"]

        if "admin_note" in data and data["admin_note"]:
            report.admin_note = data["admin_note"]

        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            abort(400, message="Failed to update report.")

        return report
