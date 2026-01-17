#!/bin/bash

echo "Archiving old logs..."
[ -f tmp/nohup_gpio.log ] && mv tmp/nohup_gpio.log tmp/nohup_gpio.log.old
[ -f tmp/nohup_workers.log ] && mv tmp/nohup_workers.log tmp/nohup_workers.log.old
[ -f tmp/nohup_beat.log ] && mv tmp/nohup_beat.log tmp/nohup_beat.log.old
[ -f tmp/celery_gpio.log ] && mv tmp/celery_gpio.log tmp/celery_gpio.log.old
[ -f tmp/celery_workers.log ] && mv tmp/celery_workers.log tmp/celery_workers.log.old
[ -f tmp/celery_beat.log ] && mv tmp/celery_beat.log tmp/celery_beat.log.old

echo "Flushing Redis"
redis-cli FLUSHALL

echo "Purging queue"
celery -A edisplay.scheduler purge -f
sleep 3

echo "Starting Celery (GPIO) worker..."
nohup celery -A edisplay.scheduler worker --loglevel=info --logfile=tmp/celery_gpio.log --pool=solo --queues=gpio > tmp/nohup_gpio.log 2>&1 &
sleep 3

echo "Starting Celery workers..."
nohup celery -A edisplay.scheduler worker --loglevel=info --logfile=tmp/celery_workers.log --concurrency=2 > tmp/nohup_workers.log 2>&1 &
sleep 5

echo "Starting Celery beat..."
nohup celery -A edisplay.scheduler beat --loglevel=info --logfile=tmp/celery_beat.log > tmp/nohup_beat.log 2>&1 &
sleep 5

echo "Checking processes..."
pgrep -fa celery

echo "Celery started!"
