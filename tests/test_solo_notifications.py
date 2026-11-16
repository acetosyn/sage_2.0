from test_entrepreneur import SoloTests
from services.solo_notifications import prepare_solo_notice,dispatch_solo_email
from models import Notification
from packages.database import db
from unittest.mock import patch
class SoloNotificationTests(SoloTests):
 def test_notice_once(self):
  row=self.entry('sales','100','notice-001');notice=prepare_solo_notice(self.app,self.u,row);db.session.commit()
  self.assertEqual(Notification.query.count(),1);self.assertEqual(notice.entity_type,'solo_sales');self.assertIsNone(prepare_solo_notice(self.app,self.u,row));self.assertEqual(dispatch_solo_email(self.app,self.u,notice),'not_configured')
 def test_rollback(self):
  row=self.entry('costs','100','notice-002');prepare_solo_notice(self.app,self.u,row);db.session.rollback();self.assertEqual(Notification.query.count(),0)
 def test_email(self):
  self.app.config.update(EMAIL_NOTIFICATIONS_ENABLED=True,SMTP_HOST='test',SMTP_FROM_EMAIL='test@local.test')
  row=self.entry('sales','100','notice-003');notice=prepare_solo_notice(self.app,self.u,row);db.session.commit()
  with patch('services.solo_notifications.send_email',return_value=True) as sender:
   self.assertEqual(dispatch_solo_email(self.app,self.u,notice),'queued');sender.assert_called_once();self.assertTrue(notice.email_attempted)
