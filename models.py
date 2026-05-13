"""SQLAlchemy models for UnionHub."""
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password: str):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)


class Dma(db.Model):
    __tablename__ = "dmas"
    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(50), unique=True, nullable=False, index=True)
    name = db.Column(db.String(200), nullable=False)
    display_order = db.Column(db.Integer, default=100)

    unions = db.relationship("Union", back_populates="dma", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "slug": self.slug,
            "name": self.name,
            "count": len(self.unions),
        }


class Union(db.Model):
    __tablename__ = "unions"
    id = db.Column(db.Integer, primary_key=True)
    dma_id = db.Column(db.Integer, db.ForeignKey("dmas.id"), nullable=False, index=True)
    dma = db.relationship("Dma", back_populates="unions")

    # Core fields (from spreadsheet)
    name = db.Column(db.String(500), nullable=False)
    category = db.Column(db.String(200), index=True)
    website = db.Column(db.String(500))
    media_emails = db.Column(db.JSON, default=list)
    media_linkedin = db.Column(db.String(500))
    apprenticeship_emails = db.Column(db.JSON, default=list)
    apprenticeship_linkedin = db.Column(db.String(500))
    apprenticeship_phone = db.Column(db.String(200))
    general_phone = db.Column(db.String(200))
    notes = db.Column(db.Text)
    application_window = db.Column(db.String(500))  # sheet text, e.g. "Rolling" or "Feb 9-20, 2026"

    # Scraped / enriched fields
    next_application_window = db.Column(db.String(500))
    application_window_status = db.Column(db.String(50))  # open|upcoming|closed|rolling|unknown
    application_url = db.Column(db.String(1000))
    application_instructions = db.Column(db.Text)
    apprentice_starting_wage = db.Column(db.String(200))
    journeyman_wage = db.Column(db.String(200))
    wage_notes = db.Column(db.Text)
    program_length = db.Column(db.String(200))
    requirements_summary = db.Column(db.Text)
    extraction_confidence = db.Column(db.String(20))  # high|medium|low
    extraction_notes = db.Column(db.Text)

    # Workflow meta
    last_scraped_at = db.Column(db.DateTime)
    scrape_status = db.Column(db.String(30))  # success|partial|failed|skipped
    admin_verified = db.Column(db.Boolean, default=False, index=True)
    awaiting_review = db.Column(db.Boolean, default=False, index=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self, public=False):
        """Public version omits internal workflow fields."""
        d = {
            "id": self.id,
            "name": self.name,
            "category": self.category,
            "dma_slug": self.dma.slug if self.dma else None,
            "dma": self.dma.name if self.dma else None,
            "website": self.website,
            "apprenticeship_emails": self.apprenticeship_emails or [],
            "apprenticeship_phone": self.apprenticeship_phone,
            "general_phone": self.general_phone,
            "notes": self.notes,
            "application_window": self.application_window,
            "next_application_window": self.next_application_window,
            "application_window_status": self.application_window_status,
            "application_url": self.application_url,
            "application_instructions": self.application_instructions,
            "apprentice_starting_wage": self.apprentice_starting_wage,
            "journeyman_wage": self.journeyman_wage,
            "wage_notes": self.wage_notes,
            "program_length": self.program_length,
            "requirements_summary": self.requirements_summary,
            "admin_verified": self.admin_verified,
        }
        if not public:
            d.update({
                "media_emails": self.media_emails or [],
                "media_linkedin": self.media_linkedin,
                "apprenticeship_linkedin": self.apprenticeship_linkedin,
                "extraction_confidence": self.extraction_confidence,
                "extraction_notes": self.extraction_notes,
                "last_scraped_at": self.last_scraped_at.isoformat() if self.last_scraped_at else None,
                "scrape_status": self.scrape_status,
                "awaiting_review": self.awaiting_review,
            })
        return d


class ScrapeJob(db.Model):
    __tablename__ = "scrape_jobs"
    id = db.Column(db.Integer, primary_key=True)
    union_id = db.Column(db.Integer, db.ForeignKey("unions.id"), nullable=False, index=True)
    union = db.relationship("Union", backref="scrape_jobs")

    status = db.Column(db.String(30), default="pending", index=True)  # pending|running|done|failed
    result = db.Column(db.JSON)  # raw LLM extraction
    error = db.Column(db.Text)

    requested_by_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    requested_by = db.relationship("User")
    requested_at = db.Column(db.DateTime, default=datetime.utcnow)
    started_at = db.Column(db.DateTime)
    finished_at = db.Column(db.DateTime)
