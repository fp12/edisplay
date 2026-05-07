#!/bin/bash

echo "Last 5 lines of beat log:"
tail -n 5 tmp/celery_beat.log
echo ""
echo "Last 5 lines of nohup beat log:"
tail -n 5 tmp/nohup_beat.log
echo ""

echo "Last 5 lines of gpio log:"
tail -n 5 tmp/celery_gpio.log
echo ""
echo "Last 5 lines of nohup gpio log:"
tail -n 5 tmp/nohup_gpio.log
echo ""

echo "Last 10 lines of nohup worker log:"
tail -n 10 tmp/nohup_workers.log
echo ""
echo "Last 30 lines of worker log:"
tail -n 30 tmp/celery_workers.log
echo ""

echo "Last 30 lines of Monitoring log:"
tail -n 30 tmp/monitoring.log
echo ""

echo "Celery processes:"
pgrep -fa celery || echo "No Celery processes running"
echo ""