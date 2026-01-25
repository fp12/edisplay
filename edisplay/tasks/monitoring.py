from subprocess import Popen, PIPE
import platform

from celery import shared_task


@shared_task
def dump_health_data():
    if platform.system() == 'Linux':
        def run_command(command):
            p = Popen(command, stdout=PIPE, stderr=PIPE, text=True)
            stdout_data, stderr_data = p.communicate()

            print(' '.join(command))
            if stderr_data:
                print(stderr_data)
            if stdout_data:
                print(stdout_data)
            else:
                'no output'

        run_command(['free', '-t', '-m'])
        run_command(['vcgencmd', 'get_throttled'])
        run_command(['vcgencmd', 'measure_temp'])
        run_command(['vcgencmd', 'measure_volts'])
