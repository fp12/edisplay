#!/bin/bash

echo "Celery processes:"
pgrep -fa celery || echo "No Celery processes running"
echo ""

echo "Last 10 lines of beat log:"
tail -n 10 tmp/celery_beat.log
echo ""
echo "Last 10 lines of nohup beat log:"
tail -n 10 tmp/nohup_beat.log
echo ""

echo "Last 10 lines of worker log:"
tail -n 10 tmp/celery_workers.log
echo ""
echo "Last 10 lines of nohup worker log:"
tail -n 10 tmp/nohup_workers.log
echo ""

echo "Last 10 lines of gpio log:"
tail -n 10 tmp/celery_gpio.log
echo ""
echo "Last 10 lines of nohup gpio log:"
tail -n 10 tmp/nohup_gpio.log
echo ""