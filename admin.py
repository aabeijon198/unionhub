"""Admin routes (login required). Real features added in later steps."""
from flask import Blueprint, render_template
from flask_login import login_required, current_user
from sqlalchemy import func
from .models import db, Union, Dma

bp = Blueprint("admin", __name__, url_prefix="/admin")


@bp.route("/")
@login_required
def dashboard():
    total = db.session.query(func.count(Union.id)).scalar() or 0
    verified = db.session.query(func.count(Union.id)).filter(Union.admin_verified.is_(True)).scalar() or 0
    awaiting = db.session.query(func.count(Union.id)).filter(Union.awaiting_review.is_(True)).scalar() or 0
    dma_count = db.session.query(func.count(Dma.id)).scalar() or 0

    return render_template(
        "admin/dashboard.html",
        user=current_user,
        total=total,
        verified=verified,
        awaiting=awaiting,
        dma_count=dma_count,
    )
