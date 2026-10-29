"""Isolated mobile QA server. Run locally; never connects to the real SAGE database."""
import logging
import os
import sys
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
QA_DIR=tempfile.TemporaryDirectory(prefix='sage-mobile-qa-',ignore_cleanup_errors=True)
os.environ.update(DATABASE_URL='sqlite:///'+(Path(QA_DIR.name)/'qa.db').as_posix(),SAGE_STORAGE_DIR=QA_DIR.name,
    SAGE_AUTO_CREATE_SCHEMA='true',SAGE_DEBUG='false',EMAIL_NOTIFICATIONS_ENABLED='false',WEB_PUSH_ENABLED='false',
    SESSION_COOKIE_SECURE='false',SAGE_ENV='development',SECRET_KEY='isolated-mobile-qa',
    SAGE_ADMIN_USERNAME='mobile-qa',SAGE_ADMIN_PASSWORD='isolated-mobile-qa-only',REDIS_URL='')
from app import app
from packages.database import db
from models import Organization,OrganizationWorkspace,User,Department,FinanceLedgerEntry,StaffInvitation,ActivityEvent
from flask import g,redirect,session,abort
from flask_login import login_user
from services.operations_service import create_request

with app.app_context():
    org=Organization(name='SAGE Mobile QA Organization',slug='mobile-qa-org',business_type='Retail',currency='NGN')
    solo=Organization(name='SAGE Mobile QA Business',slug='mobile-qa-solo',business_type='Retail',currency='NGN')
    db.session.add_all([org,solo]);db.session.flush()
    db.session.add_all([OrganizationWorkspace(organization_id=org.id,workspace_mode='organization'),OrganizationWorkspace(organization_id=solo.id,workspace_mode='individual')])
    dept=Department(organization_id=org.id,name='Sales & Customer Operations');db.session.add(dept);db.session.flush()
    USERS={}
    for name,role,business,department in [('owner','owner',org,None),('staff','staff',org,dept),('finance','finance',org,dept),('solo','owner',solo,None)]:
        user=User(organization_id=business.id,department_id=department.id if department else None,first_name=name.title(),last_name='QA',email=name+'@mobile-qa.test',role=role)
        user.set_password('isolated-mobile-qa-only');db.session.add(user);db.session.flush();USERS[name]=user.id
    now=datetime.now(timezone.utc)
    for name in ('finance','solo'):
        user=db.session.get(User,USERS[name])
        for i,amount in enumerate((0,250000,12500000,987654321.99)):
            for kind,direction in [('income','in'),('expense','out')]:
                db.session.add(FinanceLedgerEntry(reference=f'QA-{name}-{kind}-{i}',organization_id=user.organization_id,department_id=user.department_id,
                    created_by_id=user.id,entry_type=kind,direction=direction,category='Business operations',description='Long transaction description for mobile ledger verification',
                    counterparty='Ada Example Supplies & Services',amount=amount,currency='NGN',payment_method='bank_transfer',status='posted',occurred_at=now))
    # Populated regression fixture: long names, departments and a full 600-event audit.
    extra_dept=Department(organization_id=org.id,name='ICT / Computer Laboratory and Learning Resources');db.session.add(extra_dept);db.session.flush()
    for i in range(30):
        person=User(organization_id=org.id,department_id=extra_dept.id if i%2 else dept.id,first_name='Nifemi Adebayo' if i%2 else 'Tayo Aderonke',last_name='Chukwuebuka '+str(i),email=f'long.staff.name.{i}@example-business.test',phone='09067788671',role='staff',password_hash='!')
        db.session.add(person)
    for i in range(600):
        db.session.add(ActivityEvent(organization_id=org.id,actor_id=USERS['owner'],department_id=dept.id,action='income_created' if i%3 else 'page_view',title='Income recorded for customer invoice' if i%3 else 'Page viewed',description='A long, attributable business activity with department context, retained reference QA-'+str(i),entity_type='finance' if i%3 else 'page',ip_address='127.0.0.1',created_at=now-timedelta(minutes=i)))
    db.session.commit()
    staff=db.session.get(User,USERS['staff'])
    for i in range(3):
        create_request(app,staff,dict(title='Customer operations supplies',description='Mobile request QA',item_name='Office supplies',quantity=2,unit_cost=125000,urgency='normal',purpose='Operations'))
    db.session.add(StaffInvitation(token='mobile-qa-invite',organization_id=org.id,department_id=dept.id,email='invite@mobile-qa.test',first_name='Ada',last_name='Example',expires_at=now+timedelta(days=7)))
    db.session.commit()

@app.get('/qa-session/<name>')
def qa_session(name):
    session.clear();g.pop('_login_user',None)
    if name=='developer':session['sage_platform_admin']=True;session['sage_platform_admin_username']='mobile-qa';return redirect('/platform-admin')
    if name not in USERS:abort(404)
    login_user(db.session.get(User,USERS[name]));return redirect('/dashboard')

@app.get('/qa-before/<page>')
def qa_before(page):
    from flask_login import current_user
    from jinja2 import FileSystemLoader
    from app import page_context
    if not current_user.is_authenticated:abort(403)
    baseline=ROOT/'.qa/revision_before/templates'
    if not baseline.is_dir():abort(404)
    env=app.jinja_env.overlay(loader=FileSystemLoader(str(baseline)))
    context=page_context(page);app.update_template_context(context)
    return env.get_template('app_shell.html').render(context)

if __name__=='__main__':
    logging.getLogger('werkzeug').setLevel(logging.ERROR)
    try:app.run(host='127.0.0.1',port=5016,debug=False,use_reloader=False,threaded=True)
    finally:
        with app.app_context():db.session.remove();db.engine.dispose()
        QA_DIR.cleanup()
