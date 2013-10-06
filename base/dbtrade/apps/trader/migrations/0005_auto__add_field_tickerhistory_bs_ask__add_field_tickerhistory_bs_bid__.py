# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'TickerHistory.bs_ask'
        db.add_column(u'trader_tickerhistory', 'bs_ask',
                      self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=12, decimal_places=2),
                      keep_default=False)

        # Adding field 'TickerHistory.bs_bid'
        db.add_column(u'trader_tickerhistory', 'bs_bid',
                      self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=12, decimal_places=2),
                      keep_default=False)

        # Adding field 'TickerHistory.bs_high'
        db.add_column(u'trader_tickerhistory', 'bs_high',
                      self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=12, decimal_places=2),
                      keep_default=False)

        # Adding field 'TickerHistory.bs_last'
        db.add_column(u'trader_tickerhistory', 'bs_last',
                      self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=12, decimal_places=2),
                      keep_default=False)

        # Adding field 'TickerHistory.bs_low'
        db.add_column(u'trader_tickerhistory', 'bs_low',
                      self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=12, decimal_places=2),
                      keep_default=False)

        # Adding field 'TickerHistory.bs_volume'
        db.add_column(u'trader_tickerhistory', 'bs_volume',
                      self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=18, decimal_places=8),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'TickerHistory.bs_ask'
        db.delete_column(u'trader_tickerhistory', 'bs_ask')

        # Deleting field 'TickerHistory.bs_bid'
        db.delete_column(u'trader_tickerhistory', 'bs_bid')

        # Deleting field 'TickerHistory.bs_high'
        db.delete_column(u'trader_tickerhistory', 'bs_high')

        # Deleting field 'TickerHistory.bs_last'
        db.delete_column(u'trader_tickerhistory', 'bs_last')

        # Deleting field 'TickerHistory.bs_low'
        db.delete_column(u'trader_tickerhistory', 'bs_low')

        # Deleting field 'TickerHistory.bs_volume'
        db.delete_column(u'trader_tickerhistory', 'bs_volume')


    models = {
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
        }
    }

    complete_apps = ['trader']