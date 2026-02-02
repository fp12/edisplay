import sys
import importlib.abc
import importlib.machinery

class ImportTracer(importlib.abc.MetaPathFinder):
    def find_module(self, fullname, path=None):
        if 'numpy' in fullname.lower() or 'nba' in fullname.lower():
            import traceback
            print(f"\n{'='*80}")
            print(f"IMPORTING: {fullname}")
            print(f"{'='*80}")
            for line in traceback.format_stack()[:-1]:
                print(line.strip())
            print()
        return None

sys.meta_path.insert(0, ImportTracer())

# Now simulate worker startup
from celery import Celery
from celery.bin.worker import worker as WorkerCommand

app = Celery('test')
app.config_from_object('edisplay.scheduler:scheduler')

# This is what happens when worker starts
from edisplay.scheduler import scheduler
scheduler.autodiscover_tasks([
    'edisplay.workflows.common',
    'edisplay.workflows.weekday',
    'edisplay.workflows.weekend',
])

# Simulate worker initialization
w = WorkerCommand(app=scheduler)

print("\n\nFINAL CHECK: numpy loaded?", "numpy" in sys.modules)
