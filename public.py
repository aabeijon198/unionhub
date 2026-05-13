"""Public-facing routes for job seekers."""
from flask import Blueprint, render_template, jsonify
from sqlalchemy import func
from .models import db, Union, Dma

bp = Blueprint("public", __name__)


@bp.route("/")
def home():
    total = db.session.query(func.count(Union.id)).scalar() or 0
    dma_count = db.session.query(func.count(Dma.id)).scalar() or 0
    return render_template("public/home.html", total=total, dma_count=dma_count)


@bp.route("/api/health")
def health():
    """Used by Railway for healthchecks and by us for smoke tests."""
    return jsonify(ok=True, unions=db.session.query(func.count(Union.id)).scalar() or 0)
