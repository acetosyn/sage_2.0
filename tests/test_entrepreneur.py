import unittest
from flask import Flask
from packages.database import db
from models import Organization,OrganizationWorkspace,User,SoloRecord,FinancialRecord
from services.entrepreneur_service import create_record,create_entry,balance,summary
class SoloTests(unittest.TestCase):
 def setUp(self):
  self.app=Flask(__name__);self.app.config.update(SQLALCHEMY_DATABASE_URI='sqlite:///:memory:',TESTING=True);db.init_app(self.app);self.ctx=self.app.app_context();self.ctx.push();db.create_all()
  o=Organization(name='Food',slug='food',business_type='Restaurant');db.session.add(o);db.session.flush();db.session.add(OrganizationWorkspace(organization_id=o.id,workspace_mode='individual',business_category_key='restaurant_food'));self.u=User(organization_id=o.id,first_name='Test',last_name='Owner',email='test@local.test',role='owner',password_hash='test');db.session.add(self.u);db.session.commit()
 def tearDown(self):db.session.remove();db.drop_all();self.ctx.pop()
 def entry(self,kind,amount,key,**kw):return create_entry(self.u,dict(kind=kind,amount=amount,title='Test',request_key=key,**kw))
 def test_profit_and_retry(self):
  self.entry('sales','10000','sales-001');self.entry('sales','10000','sales-001');self.entry('costs','4000','costs-001');self.entry('drawings','1000','draws-001');db.session.commit();self.assertEqual(summary(self.u)['profit'],6000);self.assertEqual(FinancialRecord.query.count(),2)
 def test_savings_not_expense_and_no_overdraw(self):
  r=create_record(self.u,'savings',dict(title='Rent',target=10000,contribution=500,frequency='daily'));db.session.flush();self.entry('deposit',500,'deposit-1',record_id=r.id);db.session.flush();self.assertEqual(balance(r),500);self.assertEqual(FinancialRecord.query.count(),0)
  with self.assertRaises(ValueError):self.entry('withdraw',600,'withdraw1',record_id=r.id)
 def test_invalid_numbers(self):
  for v in ['NaN','Infinity','-2']:
   with self.assertRaises(ValueError):self.entry('sales',v,'invalid01')
 def test_all_profiles(self):
  from services.entrepreneur_catalog import PROFILES
  from services.organization_catalog import INDIVIDUAL_BUSINESS_TYPES
  self.assertGreaterEqual(len(PROFILES),30)
  self.assertTrue(all(t['key'] in PROFILES for t in INDIVIDUAL_BUSINESS_TYPES))
