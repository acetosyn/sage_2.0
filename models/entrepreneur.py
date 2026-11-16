"""Additive, tenant-owned tools for owner-operated businesses."""
import uuid
from datetime import datetime, timezone
from packages.database import db

class SoloRecord(db.Model):
    __tablename__ = 'solo_records'
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    organization_id = db.Column(db.String(36), db.ForeignKey('organizations.id', ondelete='CASCADE'), nullable=False, index=True)
    kind = db.Column(db.String(32), nullable=False, index=True)
    title = db.Column(db.String(180), nullable=False)
    data = db.Column(db.JSON, nullable=False, default=dict)
    status = db.Column(db.String(24), nullable=False, default='active')
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

class SoloEntry(db.Model):
    __tablename__ = 'solo_entries'
    __table_args__ = (db.UniqueConstraint('organization_id', 'request_key', name='uq_solo_retry'),)
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    organization_id = db.Column(db.String(36), db.ForeignKey('organizations.id', ondelete='CASCADE'), nullable=False, index=True)
    record_id = db.Column(db.String(36), db.ForeignKey('solo_records.id'), nullable=True, index=True)
    kind = db.Column(db.String(32), nullable=False, index=True)
    title = db.Column(db.String(180), nullable=False)
    amount = db.Column(db.Numeric(18,2), nullable=False, default=0)
    quantity = db.Column(db.Numeric(18,3), nullable=False, default=1)
    occurred_on = db.Column(db.Date, nullable=False, index=True)
    data = db.Column(db.JSON, nullable=False, default=dict)
    request_key = db.Column(db.String(80), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
