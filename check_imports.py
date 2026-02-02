import sys

# Import your celery app
from edisplay.scheduler import scheduler

# Check what's loaded
numpy_modules = [name for name in sys.modules.keys() if 'numpy' in name or 'nba' in name]

print("NumPy/NBA related modules loaded:")
for mod in sorted(numpy_modules):
    print(f"  {mod}")

# Find who imported nba_api
if 'nba_api' in sys.modules:
    print("\nnba_api is loaded!")
    
print("\nAll edisplay modules:")
edisplay_mods = [name for name in sys.modules.keys() if 'edisplay' in name]
for mod in sorted(edisplay_mods):
    print(f"  {mod}")
