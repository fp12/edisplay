#!/bin/bash

echo "Last 10 lines of beat log:"
tail -n 10 tmp/celery_beat.log
echo ""

echo "Last 10 lines of worker log:"
tail -n 10 tmp/celery_workers.log
echo ""

echo "Last 10 lines of gpio log:"
tail -n 10 tmp/celery_gpio.log
echo ""

echo "Stopping Celery processes..."
pkill -TERM -f celery
echo "Celery stopped!"