import os
import glob
import platform
from subprocess import Popen, PIPE
from datetime import datetime

from celery import shared_task

from edisplay.logging_config import monitoring_logger


@shared_task
def dump_health_data():
    if platform.system() == 'Linux':
        def run_command(command):
            p = Popen(command, stdout=PIPE, stderr=PIPE, text=True)
            stdout_data, stderr_data = p.communicate()

            output = [' '.join(command)]
            if stderr_data:
                output.append(stderr_data)
            if stdout_data:
                output.append(stdout_data)
            else:
                output.append('no output')

            result = '\n'.join(output)
            monitoring_logger.info(result)

        monitoring_logger.info(f"Health Check: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        run_command(['free', '-t', '-m'])
        run_command(['vcgencmd', 'get_throttled'])
        run_command(['vcgencmd', 'measure_temp'])
        run_command(['vcgencmd', 'measure_volts'])
        run_command(['bash', '-c', 'for p in $(pgrep -f celery); do echo "PID $p: $(ls /proc/$p/fd 2>/dev/null | wc -l) FDs"; done'])
