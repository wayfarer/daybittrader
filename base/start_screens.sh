#!/bin/bash

screen1celery="./manage.py celeryd -l info -Q celery -B"
screen2celery="./manage.py celeryd -l info -Q ticker"
screen3celery="./manage.py celeryd -l info -Q live_connect -c 1"
screen4celery="./manage.py celeryd -l info -Q do_trades -c 1"
screen5celery="./manage.py celeryd -l info -Q trade -c 4"
screen6celery="./manage.py celeryd -l info -Q notices"
screen7celery="./manage.py celeryd -l info -Q interval_history -c 4"

shared="source /app/dbt/ve/bin/activate;cd /app/dbt/code/base"
	
screen -dmS beat
screen -dmS ticker
screen -dmS live_connect
screen -dmS do_trades
screen -dmS trade
screen -dmS notices
screen -dmS interval

screen -S beat -X stuff "$shared$(printf \\r)"
screen -S ticker -X stuff "$shared$(printf \\r)"
screen -S live_connect -X stuff "$shared$(printf \\r)"
screen -S do_trades -X stuff "$shared$(printf \\r)"
screen -S trade -X stuff "$shared$(printf \\r)"
screen -S notices -X stuff "$shared$(printf \\r)"
screen -S interval -X stuff "$shared$(printf \\r)"

screen -S beat -X stuff "$screen1celery$(printf \\r)"
screen -S ticker -X stuff "$screen2celery$(printf \\r)"
screen -S live_connect -X stuff "$screen3celery$(printf \\r)"
screen -S do_trades -X stuff "$screen4celery$(printf \\r)"
screen -S trade -X stuff "$screen5celery$(printf \\r)"
screen -S notices -X stuff "$screen6celery$(printf \\r)"
screen -S interval -X stuff "$screen7celery$(printf \\r)"
