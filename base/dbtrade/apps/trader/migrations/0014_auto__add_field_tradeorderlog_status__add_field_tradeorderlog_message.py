# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'TradeOrderLog.status'
        db.add_column(u'trader_tradeorderlog', 'status',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=32),
                      keep_default=False)

        # Adding field 'TradeOrderLog.message'
        db.add_column(u'trader_tradeorderlog', 'message',
                      self.gf('django.db.models.fields.TextField')(null=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'TradeOrderLog.status'
        db.delete_column(u'trader_tradeorderlog', 'status')

        # Deleting field 'TradeOrderLog.message'
        db.delete_column(u'trader_tradeorderlog', 'message')


    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'trader.emailnotice': {
            'Meta': {'object_name': 'EmailNotice'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'date_added': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date_updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '254'}),
            'frequency': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'high_price_point': ('django.db.models.fields.DecimalField', [], {'max_digits': '12', 'decimal_places': '5', 'db_index': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_sent': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(1970, 1, 1, 0, 0)', 'db_index': 'True'}),
            'low_price_point': ('django.db.models.fields.DecimalField', [], {'max_digits': '12', 'decimal_places': '5', 'db_index': 'True'}),
            'market': ('django.db.models.fields.CharField', [], {'max_length': '32', 'db_index': 'True'}),
            'max_send': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'uuid': ('django.db.models.fields.CharField', [], {'max_length': '36', 'null': 'True', 'db_index': 'True'})
        },
        u'trader.emailnoticelog': {
            'Meta': {'object_name': 'EmailNoticeLog'},
            'date_added': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'db_index': 'True', 'blank': 'True'}),
            'email_notice': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['trader.EmailNotice']", 'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'market': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'notice_type': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'price': ('django.db.models.fields.DecimalField', [], {'max_digits': '12', 'decimal_places': '5'})
        },
        u'trader.orderrecord': {
            'Meta': {'object_name': 'OrderRecord'},
            'btc_value': ('django.db.models.fields.DecimalField', [], {'max_digits': '18', 'decimal_places': '8'}),
            'btc_value_int': ('django.db.models.fields.IntegerField', [], {}),
            'date_added': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date_updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'hold': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'oid': ('django.db.models.fields.CharField', [], {'max_length': '100', 'db_index': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'OPEN'", 'max_length': '32'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'usd_value': ('django.db.models.fields.DecimalField', [], {'max_digits': '12', 'decimal_places': '5'}),
            'usd_value_int': ('django.db.models.fields.IntegerField', [], {})
        },
        u'trader.tickerhistory': {
            'Meta': {'object_name': 'TickerHistory'},
            'average_value': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '12', 'decimal_places': '5'}),
            'average_value_int': ('django.db.models.fields.IntegerField', [], {}),
            'bs_ask': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '12', 'decimal_places': '2'}),
            'bs_bid': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '12', 'decimal_places': '2'}),
            'bs_high': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '12', 'decimal_places': '2'}),
            'bs_last': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '12', 'decimal_places': '2'}),
            'bs_low': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '12', 'decimal_places': '2'}),
            'bs_volume': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '18', 'decimal_places': '8'}),
            'buy_value': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '12', 'decimal_places': '5'}),
            'buy_value_int': ('django.db.models.fields.IntegerField', [], {}),
            'cb_buy_value': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '12', 'decimal_places': '5'}),
            'cb_buy_value_50': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '12', 'decimal_places': '5'}),
            'cb_sell_value': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '12', 'decimal_places': '5'}),
            'cb_sell_value_50': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '12', 'decimal_places': '5'}),
            'date_added': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'high_value': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '12', 'decimal_places': '5'}),
            'high_value_int': ('django.db.models.fields.IntegerField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_value': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '12', 'decimal_places': '5'}),
            'last_value_int': ('django.db.models.fields.IntegerField', [], {}),
            'low_value': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '12', 'decimal_places': '5'}),
            'low_value_int': ('django.db.models.fields.IntegerField', [], {}),
            'mtgox_timestamp': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'sell_value': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '12', 'decimal_places': '5'}),
            'sell_value_int': ('django.db.models.fields.IntegerField', [], {}),
            'volume': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '18', 'decimal_places': '8'}),
            'weighted_average_value': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '12', 'decimal_places': '5'}),
            'weighted_average_value_int': ('django.db.models.fields.IntegerField', [], {})
        },
        u'trader.tradeorder': {
            'Meta': {'object_name': 'TradeOrder'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'db_index': 'True'}),
            'btc_amount': ('django.db.models.fields.DecimalField', [], {'max_digits': '18', 'decimal_places': '8'}),
            'date_added': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date_expire': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True'}),
            'date_updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'locked': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'parent_trade': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['trader.TradeOrder']", 'null': 'True'}),
            'price_point': ('django.db.models.fields.DecimalField', [], {'max_digits': '12', 'decimal_places': '5', 'db_index': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '32', 'db_index': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'null': 'True'}),
            'uuid': ('django.db.models.fields.CharField', [], {'max_length': '36', 'null': 'True', 'db_index': 'True'})
        },
        u'trader.tradeorderlog': {
            'Meta': {'object_name': 'TradeOrderLog'},
            'btc_amount': ('django.db.models.fields.DecimalField', [], {'max_digits': '18', 'decimal_places': '8'}),
            'date_added': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'message': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'price_point': ('django.db.models.fields.DecimalField', [], {'max_digits': '12', 'decimal_places': '5'}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'trade_order': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['trader.TradeOrder']"}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '32'})
        },
        u'trader.usersettings': {
            'Meta': {'object_name': 'UserSettings'},
            'coinbase_oauth_token': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['auth.User']", 'unique': 'True'})
        }
    }

    complete_apps = ['trader']