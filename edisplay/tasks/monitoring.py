import platform
from subprocess import run
from datetime import datetime

from celery import shared_task

from edisplay.logging_config import monitoring_logger as logger


@shared_task
def dump_health_data(ignore_result=True):
    if platform.system() != 'Linux':
        return
    
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
    logger.info(f"Avail:{available_mb}MB Swap:{swap_used}MB Celery:{celery_mem}MB {temp}")
    
    # Spike detection
    if available_mb < 80:
        recent_tasks = run(['tail', '-5', 'tmp/celery_workers.log'], 
                          capture_output=True, text=True).stdout
        top_procs = run(['ps', 'aux', '--sort=-%mem'], 
                       capture_output=True, text=True).stdout.split('\n')[1:6]
        
        logger.warning(f"⚠️  SPIKE: {available_mb}MB available")
        logger.warning(f"Recent: {' | '.join([t.strip() for t in recent_tasks.split('\n') if t])}")
        logger.warning(f"Top procs: {' | '.join(top_procs)}")
