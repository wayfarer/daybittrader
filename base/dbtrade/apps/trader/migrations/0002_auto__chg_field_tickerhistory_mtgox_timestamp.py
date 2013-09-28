# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'TickerHistory.mtgox_timestamp'
        db.alter_column(u'trader_tickerhistory', 'mtgox_timestamp', self.gf('django.db.models.fields.CharField')(max_length=100))

    def backwards(self, orm):

        # Changing field 'TickerHistory.mtgox_timestamp'
        db.alter_column(u'trader_tickerhistory', 'mtgox_timestamp', self.gf('django.db.models.fields.IntegerField')())

    models = {
        u'trader.tickerhistory': {
            'Meta': {'object_name': 'TickerHistory'},
            'average_value': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '12', 'decimal_places': '5'}),
            'average_value_int': ('django.db.models.fields.IntegerField', [], {}),
            'buy_value': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '12', 'decimal_places': '5'}),
            'buy_value_int': ('django.db.models.fields.IntegerField', [], {}),
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