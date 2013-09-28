from django.db import models

class TimeStampModel(models.Model):
    #: Date added
    date_added = models.DateTimeField(auto_now_add=True)
    
    #: Date updated
    date_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True
        
class LogModel(models.Model):
    #: Date added
    date_added = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        abstract = True


class TickerHistory(LogModel):
    volume = models.DecimalField(max_digits=18, decimal_places=8, null=True)
    
    weighted_average_value  = models.DecimalField(max_digits=12, decimal_places=5, null=True)
    weighted_average_value_int = models.IntegerField()
    
    average_value = models.DecimalField(max_digits=12, decimal_places=5, null=True)
    average_value_int = models.IntegerField()
    
    last_value = models.DecimalField(max_digits=12, decimal_places=5, null=True)
    last_value_int = models.IntegerField()
    
    high_value = models.DecimalField(max_digits=12, decimal_places=5, null=True)
    high_value_int = models.IntegerField()
    
    low_value = models.DecimalField(max_digits=12, decimal_places=5, null=True)
    low_value_int = models.IntegerField()
    
    sell_value = models.DecimalField(max_digits=12, decimal_places=5, null=True)
    sell_value_int = models.IntegerField()
    
    buy_value = models.DecimalField(max_digits=12, decimal_places=5, null=True)
    buy_value_int = models.IntegerField()
    
    cb_buy_value = models.DecimalField(max_digits=12, decimal_places=5, null=True)
    cb_buy_value_50 = models.DecimalField(max_digits=12, decimal_places=5, null=True)
    
    mtgox_timestamp = models.CharField(max_length=100)
    
    
class OrderRecord(TimeStampModel):
    
    #: Order OID, according to MtGox
    oid = models.CharField(max_length=100, db_index=True)
    
    #: BUY, SELL
    type = models.CharField(max_length=32)
    
    #: OPEN, CANCELED, COMPLETED
    status = models.CharField(max_length=32, default='OPEN')
    
    #: Value, in BTC
    btc_value = models.DecimalField(max_digits=18, decimal_places=8)
    btc_value_int = models.IntegerField()
    
    #: Value, in USD
    usd_value = models.DecimalField(max_digits=12, decimal_places=5)
    usd_value_int = models.IntegerField()
    
    #: If True, when this bid is made, it does not get replaced every 5 minutes.
    hold = models.BooleanField(default=False)
