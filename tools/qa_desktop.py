"""Isolated populated fixture for desktop visual QA; never uses the live DB."""
from datetime import datetime,timedelta,timezone
from pathlib import Path
import logging
import qa_mobile as fixture
from qa_mobile import app,db,ROOT,USERS
from models import User,Department,InventoryItem,AssetItem,CatalogItem,FinanceLedgerEntry,FinanceAccount,FinanceReceivable,FinancePayable,BudgetAllocation,BranchLocation,Supplier
from models.business import Customer,SalesInvoice,EventPlan,ImprestFund,BillPlan,ComplianceDocument,EmployeeProfile,StockProfile

with app.app_context():
    owner=db.session.get(User,USERS['owner']);staff=db.session.get(User,USERS['staff']);now=datetime.now(timezone.utc);org=owner.organization_id;dept=staff.department_id
    common=dict(organization_id=org,department_id=dept,created_by_id=staff.id)
    for i in range(6):
        db.session.add(InventoryItem(organization_id=org,department_id=dept,name=['Wireless Keyboard','Printer Paper A4','Network Switch','Safety Gloves','Office Supplies','Conference Equipment'][i],category='Office & Technology',unit='unit',quantity=[4,45,0,12,2,8][i],unit_value=12500,reorder_level=5,location='Main Store',added_by_id=staff.id))
        db.session.add(AssetItem(organization_id=org,department_id=dept,name='Workstation '+str(i+1),category='Technology',quantity=1,unit_value=185000,asset_tag='SAGE-QA-'+str(i),serial_number='SN-2026-'+str(i),condition='good' if i%2 else 'needs_repair',status='active',location='Main Office',custodian_user_id=staff.id,created_by_id=staff.id))
    for i in range(3):
        db.session.add(CatalogItem(organization_id=org,department_id=dept,name='Department Custom Item '+str(i+1),category='Office supplies',unit='unit',created_by_id=staff.id))
    account=FinanceAccount(organization_id=org,name='Operating Account',account_type='bank',currency='NGN',opening_balance=8500000,created_by_id=owner.id);db.session.add(account);db.session.flush()
    for i in range(12):
        kind='income' if i%3 else 'expense';amount=[250000,87500,365000,170000][i%4]
        db.session.add(FinanceLedgerEntry(reference=f'DESK-QA-{i:03}',organization_id=org,department_id=dept,account_id=account.id,created_by_id=staff.id,entry_type=kind,direction='in' if kind=='income' else 'out',category='Customer revenue' if kind=='income' else 'Office operations',description=['Customer invoice settlement','Department supplies and equipment','Service revenue received','Monthly operating expenditure'][i%4],counterparty='Aderonke Business Services',amount=amount,currency='NGN',payment_method=['bank_transfer','cash','pos'][i%3],status='posted',occurred_at=now-timedelta(days=i)))
    db.session.add(BudgetAllocation(organization_id=org,department_id=dept,name='Quarterly Operations',original_budget=2500000,period_start=now.date()-timedelta(days=30),period_end=now.date()+timedelta(days=60),created_by_id=owner.id))
    for i in range(4):
        customer=Customer(**common,name=['Epitome Learning Centre','Aderonke & Partners','Northgate Services','Meridian Enterprises'][i],email=f'contact{i}@example.test',phone='08012345678',business='Professional services',stage=['active','lead','prospect','active'][i],assigned_to_id=staff.id,next_follow_up=now.date()+timedelta(days=i));db.session.add(customer);db.session.flush()
        rec=FinanceReceivable(reference='REC-QA-'+str(i),organization_id=org,department_id=dept,customer_name=customer.name,invoice_number=f'INV-QA-{i}',description='Services and supplies',total_amount=250000,amount_received=50000,currency='NGN',due_date=now.date()-timedelta(days=i*15),status='partial',created_by_id=staff.id);db.session.add(rec);db.session.flush()
        db.session.add(SalesInvoice(**common,customer_id=customer.id,receivable_id=rec.id,number=f'QA-INVOICE-{i}',description='Business supplies and service invoice',currency='NGN',subtotal=250000,total=250000,paid=50000,due_date=rec.due_date,status='partial',issued_at=now-timedelta(days=i)))
        db.session.add(Supplier(organization_id=org,name='Reliable Vendor '+str(i+1),normalized_name='reliable vendor '+str(i+1),email=f'vendor{i}@example.test',phone='08012345678',status='active',created_by_id=owner.id))
        db.session.add(BranchLocation(organization_id=org,name='Branch '+str(i+1),code='QA'+str(i),address='Business district',created_by_id=owner.id))
        db.session.add(EventPlan(**common,manager_id=staff.id,name=['Customer Growth Campaign','Team Training','Annual Business Forum','Community Outreach'][i],kind='campaign' if i%2 else 'event',category='Business development',objective='Deliver measurable business outcomes.',venue='Main Office',start_at=now+timedelta(days=i*3+1),end_at=now+timedelta(days=i*3+2),status=['draft','approved','active','completed'][i],requested=250000,approved=200000,released=150000,spent=87500,expected_reach=100,expected_leads=20,expected_customers=10,expected_revenue=500000))
        db.session.add(BillPlan(**common,name=['Internet subscription','Office lease','Insurance renewal','Software subscription'][i],responsible_id=staff.id,category='Operations',first_due=now.date(),amount=75000,frequency='monthly',next_due=now.date()+timedelta(days=i*5-4),status='active'))
        db.session.add(ComplianceDocument(**common,name=['Business registration','Tax clearance','Insurance cover','Operating permit'][i],category='Corporate governance',identifier='DOC-QA-'+str(i),expiry_date=now.date()+timedelta(days=i*20-5),status='active',responsible_id=staff.id))
    db.session.commit()

@app.get('/qa-desktop-before/<page>')
def qa_desktop_before(page):
    from flask_login import current_user
    from flask import abort
    from jinja2 import FileSystemLoader
    from app import page_context
    if not current_user.is_authenticated:abort(403)
    env=app.jinja_env.overlay(loader=FileSystemLoader(str(ROOT/'.qa/desktop_before/templates')));context=page_context(page);app.update_template_context(context);return env.get_template('app_shell.html').render(context)

if __name__=='__main__':
    logging.getLogger('werkzeug').setLevel(logging.ERROR)
    try:app.run(host='127.0.0.1',port=5016,debug=False,use_reloader=False,threaded=True)
    finally:
        with app.app_context():db.session.remove();db.engine.dispose()
        fixture.QA_DIR.cleanup()
