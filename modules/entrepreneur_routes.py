"""Owner-only solo endpoints: authorization enforced independently of navigation."""
import csv,io
from functools import wraps
from flask import abort,jsonify,request,Response
from flask_login import current_user,login_required
from sqlalchemy.exc import IntegrityError
from packages.database import db
from models import SoloEntry,AuditLog
from services.solo_notifications import prepare_solo_notice, dispatch_solo_email
from services.entrepreneur_service import create_record,create_entry,owned,summary

def solo_owner(fn):
    @wraps(fn)
    @login_required
    def wrapped(*args,**kwargs):
        profile=current_user.organization.workspace_profile
        if current_user.role!='owner' or not profile or profile.workspace_mode!='individual':abort(403)
        return fn(*args,**kwargs)
    return wrapped

def register_entrepreneur_routes(app):
    @app.post('/api/solo/records/<kind>')
    @solo_owner
    def solo_record_create(kind):
        return mutate(lambda p:create_record(current_user,kind,p))

    @app.post('/api/solo/record/<record_id>')
    @solo_owner
    def solo_record_update(record_id):
        row=owned(current_user,record_id,lock=True)
        if not row:abort(404)
        def update(p):
            if p.get('action') in {'complete','reopen','archive'}:
                if row.kind in {'savings','stock','debts'}:
                    from services.entrepreneur_service import balance
                    if balance(row)!=0:raise ValueError('Clear the balance before closing this record.')
                row.status={'complete':'complete','reopen':'active','archive':'archived'}[p['action']]
            else:create_record(current_user,row.kind,p,row)
            return row
        return mutate(update)

    @app.post('/api/solo/entries')
    @solo_owner
    def solo_entry_create():return mutate(lambda p:create_entry(current_user,p))

    @app.post('/api/solo/profile')
    @solo_owner
    def solo_profile_update():
        from services.organization_catalog import INDIVIDUAL_BUSINESS_TYPE_MAP,BUSINESS_TYPE_MAP
        payload=request.get_json(silent=True) or {};key=payload.get('business_type')
        if key not in INDIVIDUAL_BUSINESS_TYPE_MAP:return jsonify(ok=False,message='Choose a business category.'),400
        item=INDIVIDUAL_BUSINESS_TYPE_MAP[key];profile=current_user.organization.workspace_profile
        profile.business_category_key=key;profile.business_category_label=item['label'];profile.catalog_key=item['catalog_key']
        current_user.organization.business_type=BUSINESS_TYPE_MAP.get(item['catalog_key'],BUSINESS_TYPE_MAP['other'])['label']
        db.session.add(AuditLog(organization_id=current_user.organization_id,user_id=current_user.id,action='solo_profile',description='Updated individual business category.'))
        db.session.commit();return jsonify(ok=True)

    @app.get('/api/solo/export')
    @solo_owner
    def solo_export():
        period=request.args.get('period','monthly')
        if period not in {'daily','weekly','monthly','all'}:abort(400)
        report=summary(current_user,period);out=io.StringIO();writer=csv.writer(out)
        def safe(value):
            value=str(value)
            return "'"+value if value.lstrip().startswith(('=','+','-','@','\t','\r')) else value
        writer.writerow(['Date','Type','Description','Amount','Currency','Source'])
        for row in report['financial_rows']:writer.writerow([row.occurred_at.date(),row.record_type,safe(row.description),row.amount,current_user.organization.currency,row.source_entity_type or 'SAGE'])
        for row in report['entries']:
            if row.kind not in {'sales','costs','repayment'}:writer.writerow([row.occurred_on,row.kind,safe(row.title),row.amount,current_user.organization.currency,'Not income/expense'])
        return Response('\ufeff'+out.getvalue(),mimetype='text/csv',headers={'Content-Disposition':'attachment; filename=SAGE_my_business.csv'})

    def mutate(action):
        try:
            payload=request.get_json(silent=True) or {};row=action(payload)
            db.session.add(AuditLog(organization_id=current_user.organization_id,user_id=current_user.id,action='solo_saved',description=f'Saved {row.kind}: {row.title}'))
            db.session.flush()
            verb={'complete':'completed','reopen':'reopened','archive':'archived'}.get(payload.get('action'),'saved')
            notice=prepare_solo_notice(app,current_user,row,verb)
            db.session.commit()
            email_status=dispatch_solo_email(app,current_user,notice)
            return jsonify(ok=True,id=row.id,message=f'{row.title} {verb} successfully.',email_status=email_status)
        except (ValueError,TypeError) as exc:db.session.rollback();return jsonify(ok=False,message=str(exc)),400
        except IntegrityError:
            db.session.rollback();return jsonify(ok=False,message='This request was already recorded. Refresh before retrying.'),409
