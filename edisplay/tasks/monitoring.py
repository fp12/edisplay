import platform
from subprocess import run
from datetime import datetime

from celery import shared_task

from edisplay.logging_config import monitoring_logger


@shared_task
def dump_health_data():
    if platform.system() != 'Linux':
        return

    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # Get memory stats
    mem = run(['free', '-m'], capture_output=True, text=True).stdout.split('\n')[1].split()
    available_mb = int(mem[6])
    swap_used = run(['free', '-m'], capture_output=True, text=True).stdout.split('\n')[2].split()[2]
    
    # Get celery memory
    celery_mem = run(['bash', '-c', 
                     'ps aux | grep "[c]elery" | awk \'{sum+=$6} END {print sum/1024}\''],
                    capture_output=True, text=True).stdout.strip()
    
    # Get temp
    temp = run(['vcgencmd', 'measure_temp'], capture_output=True, text=True).stdout.strip().replace('temp=', '')
    
    # Single line log
    monitoring_logger.info(f"{timestamp} | Avail:{available_mb}MB Swap:{swap_used}MB Celery:{celery_mem}MB {temp}")
    
    # Spike detection
    if available_mb < 80:
        recent_tasks = run(['tail', '-5', 'tmp/celery_workers.log'], 
                          capture_output=True, text=True).stdout
        top_procs = run(['ps', 'aux', '--sort=-%mem'], 
                       capture_output=True, text=True).stdout.split('\n')[1:6]
        
        monitoring_logger.warning(f"⚠️  SPIKE at {timestamp}: {available_mb}MB available")
        monitoring_logger.warning(f"Recent: {' | '.join([t.strip() for t in recent_tasks.split('\n') if t])}")
        monitoring_logger.warning(f"Top procs: {' | '.join(top_procs)}")

"""
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
"""
