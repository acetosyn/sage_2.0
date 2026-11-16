"""Persist solo alerts with the business transaction; dispatch mail only after commit."""
from models import Notification
from packages.database import db
from services.notification_service import record_activity, ENTITY_ROUTES
from services.entrepreneur_catalog import FEATURES
from services.email_service import send_email
for key in FEATURES: ENTITY_ROUTES['solo_'+key]='solo_'+key
MOVEMENTS={'deposit':'savings','withdraw':'savings','repayment':'debts','restock':'stock','usage':'stock'}

def prepare_solo_notice(app,user,row,verb='saved'):
    kind=MOVEMENTS.get(row.kind,row.kind);entity='solo_'+kind
    # Money entries are immutable and retry-safe: one notification per saved entry.
    if row.__tablename__=='solo_entries' and Notification.query.filter_by(organization_id=user.organization_id,user_id=user.id,entity_type=entity,entity_id=row.id).first():return None
    label=FEATURES.get(kind,(kind.replace('_',' ').title(),))[0]
    title=f'{label}: {verb}';body=f'{row.title} was {verb} in {user.organization.name}.'
    if hasattr(row,'amount'):body+=f' Amount: {user.organization.currency} {row.amount:,.2f}. Date: {row.occurred_on}.'
    notice=Notification(organization_id=user.organization_id,user_id=user.id,title=title[:180],message=body[:500],level='success',entity_type=entity,entity_id=row.id,email_attempted=False)
    db.session.add(notice);record_activity(app,user,'solo_'+verb,title,body,entity,row.id,notify_owner=False)
    return notice

def dispatch_solo_email(app,user,notice):
    if notice is None:return 'duplicate'
    if not (app.config.get('EMAIL_NOTIFICATIONS_ENABLED') and app.config.get('SMTP_HOST') and (app.config.get('SMTP_FROM_EMAIL') or app.config.get('SMTP_USERNAME'))):return 'not_configured'
    try:
        queued=send_email(app,user.email,'SAGE: '+notice.title,notice.message)
        notice.email_attempted=bool(queued);db.session.commit()
        return 'queued' if queued else 'not_queued'
    except Exception:
        db.session.rollback();app.logger.exception('Solo notification email dispatch failed');return 'failed'
