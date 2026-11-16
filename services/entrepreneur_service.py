"""Validated solo-business records. Savings, capital and drawings never count as profit."""
from datetime import date, datetime, time, timedelta, timezone
from decimal import Decimal, InvalidOperation
from zoneinfo import ZoneInfo
import uuid
from sqlalchemy import func
from packages.database import db
from models import SoloRecord, SoloEntry, FinancialRecord, AuditLog
from services.entrepreneur_catalog import FEATURES, profile_for

LAGOS=ZoneInfo('Africa/Lagos')
RECORD_KINDS={'offerings','savings','bookings','clients','stock','goals','tasks','debts','plans','campaigns','recurring'}
ENTRY_KINDS={'sales','costs','drawings','capital','deposit','withdraw','repayment','restock','usage'}
# Explicit field lists prevent arbitrary payloads becoming business records.
FIELDS={
 'offerings': {'price':'money','cost':'money','unit':'text'},
 'savings': {'target':'positive','contribution':'positive','frequency':'frequency','due':'date'},
 'bookings': {'client':'text','due':'date','fee':'money','notes':'text'},
 'clients': {'phone':'text','email':'text','due':'date','notes':'text'},
 'stock': {'opening':'money','reorder':'money','unit':'text','notes':'text'},
 'goals': {'target':'positive','progress':'money','due':'date'},
 'tasks': {'due':'date','notes':'text'},
 'debts': {'amount':'positive','phone':'text','due':'date','notes':'text'},
 'plans': {'budget':'money','actual':'money','due':'date','notes':'text'},
 'campaigns': {'partner':'text','fee':'money','reach':'money','due':'date','notes':'text'},
 'recurring': {'amount':'positive','frequency':'frequency','due':'date','notes':'text'}}

def number(value, positive=False):
    try: n=Decimal(str(value if value not in (None,'') else '0'))
    except (InvalidOperation,ValueError,TypeError): raise ValueError('Enter a valid number.')
    if not n.is_finite() or n<0 or n>Decimal('999999999999') or (positive and n<=0): raise ValueError('Enter a positive amount within the supported range.' if positive else 'Amounts must be finite and non-negative.')
    return n.quantize(Decimal('.01'))

def day(value, required=False):
    if not value:
        if required: return datetime.now(LAGOS).date()
        return None
    try: return date.fromisoformat(str(value))
    except ValueError: raise ValueError('Use a valid calendar date.')

def owned(user, record_id, kind=None, lock=False):
    q=SoloRecord.query.filter_by(id=record_id,organization_id=user.organization_id)
    if lock:q=q.with_for_update()
    row=q.first()
    if not row or (kind and row.kind!=kind): return None
    return row

def create_record(user,kind,payload,row=None):
    if kind not in RECORD_KINDS: raise ValueError('Unsupported record type.')
    title=str(payload.get('title') or '').strip()
    if not title or len(title)>180: raise ValueError('Enter a name of 1–180 characters.')
    data={}
    for key,typ in FIELDS[kind].items():
        v=payload.get(key,'')
        if typ in {'money','positive'}:data[key]=str(number(v,typ=='positive'))
        elif typ=='date':data[key]=day(v).isoformat() if v else ''
        elif typ=='frequency':
            if v not in {'daily','weekly','monthly'}:raise ValueError('Choose daily, weekly or monthly.')
            data[key]=v
        else:
            v=str(v).strip()
            if len(v)>1000:raise ValueError('Text fields must be at most 1,000 characters.')
            data[key]=v
    if row and kind in {'stock','debts'}:
        for fixed in ({'opening'} if kind=='stock' else {'amount'}):
            if data[fixed]!=row.data.get(fixed):raise ValueError('Opening amounts cannot be edited. Record a movement instead.')
    if not row:row=SoloRecord(organization_id=user.organization_id,kind=kind,title=title);db.session.add(row)
    row.title=title;row.data=data
    return row

def balance(row):
    entries=SoloEntry.query.filter_by(organization_id=row.organization_id,record_id=row.id).all()
    if row.kind=='savings':return sum((e.amount if e.kind=='deposit' else -e.amount for e in entries),Decimal(0))
    if row.kind=='debts':return Decimal(row.data['amount'])-sum((e.amount for e in entries if e.kind=='repayment'),Decimal(0))
    if row.kind=='stock':return Decimal(row.data['opening'])+sum((e.quantity if e.kind=='restock' else -e.quantity for e in entries),Decimal(0))
    return Decimal(0)

def create_entry(user,payload):
    kind=payload.get('kind');key=str(payload.get('request_key') or '')
    if kind not in ENTRY_KINDS:raise ValueError('Unsupported money movement.')
    if not 8<=len(key)<=80:raise ValueError('A valid retry key is required.')
    # Lock the tenant row to serialize SQLite/Postgres app writes and retry checks.
    from models import Organization
    Organization.query.filter_by(id=user.organization_id).with_for_update().first()
    existing=SoloEntry.query.filter_by(organization_id=user.organization_id,request_key=key).first()
    if existing:return existing
    title=str(payload.get('title') or '').strip();record=None
    if payload.get('record_id'):
        record=owned(user,payload['record_id'],lock=True)
        if not record or record.status!='active':raise ValueError('Choose an active record in your business.')
    expected={'deposit':'savings','withdraw':'savings','repayment':'debts','restock':'stock','usage':'stock','sales':'offerings'}
    if kind in expected and (not record or record.kind!=expected[kind]):
        if kind!='sales' or record:raise ValueError('Select the matching record first.')
    qty=number(payload.get('quantity',1),True)
    amount=number(payload.get('amount'),kind not in {'restock','usage'})
    if not title:title=record.title if record else ''
    if not title or len(title)>180:raise ValueError('Enter a description of 1–180 characters.')
    occurred=day(payload.get('date'),True)
    if occurred>datetime.now(LAGOS).date():raise ValueError('Actual transactions cannot be future dated; use a booking or plan.')
    if kind in {'withdraw','repayment'} and amount>balance(record):raise ValueError('Amount exceeds the available balance.')
    if kind=='usage' and qty>balance(record):raise ValueError('Usage exceeds stock available.')
    data={'method':str(payload.get('method') or 'cash')[:40], 'notes':str(payload.get('notes') or '')[:1000]}
    row=SoloEntry(organization_id=user.organization_id,record_id=record.id if record else None,kind=kind,title=title,amount=amount,quantity=qty,occurred_on=occurred,data=data,request_key=key)
    db.session.add(row);db.session.flush()
    # Cash-basis income/expense is posted once to the existing shared reporting engine.
    if kind in {'sales','costs','repayment'}:
        db.session.add(FinancialRecord(reference='SO-'+uuid.uuid4().hex[:24], organization_id=user.organization_id,department_id=user.department_id,created_by_id=user.id,
            record_type='expense' if kind=='costs' else 'income',category='Solo business',description=title,amount=amount,currency=user.organization.currency,
            source_entity_type='solo_entry',source_entity_id=row.id,occurred_at=datetime.combine(occurred,time(12),tzinfo=LAGOS).astimezone(timezone.utc)))
    return row

def summary(user,period='monthly'):
    today=datetime.now(LAGOS).date()
    start=today if period=='daily' else today-timedelta(days=today.weekday()) if period=='weekly' else today.replace(day=1) if period=='monthly' else date(2000,1,1)
    begin=datetime.combine(start,time.min,tzinfo=LAGOS).astimezone(timezone.utc);end=datetime.combine(today+timedelta(days=1),time.min,tzinfo=LAGOS).astimezone(timezone.utc)
    rows=FinancialRecord.query.filter(FinancialRecord.organization_id==user.organization_id,FinancialRecord.status=='posted',FinancialRecord.occurred_at>=begin,FinancialRecord.occurred_at<end).all()
    income=sum((r.amount for r in rows if r.record_type in {'income','revenue'}),Decimal(0))
    expense=sum((r.amount for r in rows if r.record_type in {'expense','expenditure','operating_cost','payroll','tax'}),Decimal(0))-sum((r.amount for r in rows if r.record_type=='expense_recovery'),Decimal(0))
    entries=SoloEntry.query.filter(SoloEntry.organization_id==user.organization_id,SoloEntry.occurred_on>=start,SoloEntry.occurred_on<=today).order_by(SoloEntry.occurred_on.desc(),SoloEntry.created_at.desc()).all()
    totals={k:sum((e.amount for e in entries if e.kind==k),Decimal(0)) for k in ENTRY_KINDS}
    offerings={r.id:r.title for r in SoloRecord.query.filter_by(organization_id=user.organization_id,kind='offerings').all()};best={}
    for e in entries:
        if e.kind=='sales':
            name=offerings.get(e.record_id,e.title);bucket=best.setdefault(name,{'name':name,'quantity':Decimal(0),'amount':Decimal(0)});bucket['quantity']+=e.quantity;bucket['amount']+=e.amount
    return dict(income=income,expense=expense,profit=income-expense,margin=(income-expense)/income*100 if income else 0,entries=entries,totals=totals,period=period,start=start,today=today,best=sorted(best.values(),key=lambda r:r['amount'],reverse=True)[:8],financial_rows=rows)

def solo_context(user,view):
    from flask import request
    from services.organization_catalog import INDIVIDUAL_BUSINESS_TYPES
    period=request.args.get('period','monthly')
    if period not in {'daily','weekly','monthly','all'}:period='monthly'
    records=SoloRecord.query.filter_by(organization_id=user.organization_id).order_by(SoloRecord.created_at.desc()).all()
    grouped={k:[r for r in records if r.kind==k and r.status=='active'] for k in RECORD_KINDS}
    balances={r.id:balance(r) for r in records if r.kind in {'stock','savings','debts'}}
    due=[r for r in records if r.status=='active' and r.data.get('due') and r.data['due']<=datetime.now(LAGOS).date().isoformat()]
    return dict(view=view,profile=profile_for(user),features=FEATURES,records=grouped,all_records=records,balances=balances,summary=summary(user,period),types=INDIVIDUAL_BUSINESS_TYPES,due=due,
                low_stock=[r for r in grouped['stock'] if balances[r.id]<=Decimal(r.data.get('reorder','0'))],saved=sum((balances[r.id] for r in grouped['savings']),Decimal(0)))
