# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Is

**edisplay** is a smart display system for a 7.5" Waveshare e-ink panel (480×800, 1-bit). It runs on a Raspberry Pi, uses Celery with Redis for task scheduling, and displays dynamic content (calendar, transit, weather, NBA scores, etc.) that adapts to time-of-day and which household devices are connected to the router.

## Running the Application

```bash
# Start all workers (flushes Redis, deletes beat schedule, starts 3 workers)
bash edisplay_start.sh

# Stop all workers
bash edisplay_stop.sh

# Check status and recent logs
bash edisplay_status.sh
```

Three Celery processes run concurrently:
- **GPIO worker** — solo pool (no concurrency), handles e-ink display I/O
- **Main workers** — thread pool (concurrency=2), handles data fetching and image generation
- **Beat scheduler** — fires cron jobs defined in `edisplay/scheduler_beat.py`

Logs go to `tmp/nohup_gpio.log`, `tmp/nohup_workers.log`, `tmp/nohup_beat.log`, and `tmp/monitoring.log`.

## Architecture

### Task Queue Setup

Two separate Celery apps:
- `edisplay/scheduler.py` — main app (general tasks and workflows)
- `edisplay/scheduler_gpio.py` — GPIO-isolated app (display output must be sequential)

Broker configuration is platform-aware (`edisplay/scheduler_config.py`):
- **Linux**: Redis on `localhost:6379`
- **Windows**: RabbitMQ on `localhost:5672` (for local dev/testing)

Task serialization uses **pickle** (PIL Image objects are passed between tasks).

### Display Pipeline

Every routine follows the same pattern:
1. A group of parallel tasks each generate a PIL Image panel
2. `assemble_img.s()` merges them vertically into a single 480×800 image
3. `publish_img.s()` sends it to the e-ink display (or renders on-screen on Windows)

```python
chain(
    group(task_a.s(), task_b.s(), task_c.s()),
    assemble_img.s(),
    publish_img.s()
).apply_async()
```

Partial refreshes are tracked; every 20th refresh triggers a full refresh to prevent ghosting.

### Schedules and Workflows

- **`edisplay/scheduler_beat.py`** — all cron definitions (20+ schedules, America/Montreal timezone)
- **`edisplay/workflows/weekday.py`** — time-of-day routines Mon–Fri
- **`edisplay/workflows/weekend.py`** — time-of-day routines Sat–Sun
- **`edisplay/workflows/common.py`** — background tasks (device presence polling every 2 min, nightly cache warm-up at 4 AM, midnight display sleep, weekly cache clear)

### Device Presence Gating

`edisplay/devices.py` — `DevicePresence` reads from Redis whether each household device (id0, id1, id2) is on the network (updated via ASUS router API). Workflows check `any_connected()` / `is_connected(device)` before rendering content. If no device is connected the display goes to sleep.

### Content Tasks (`edisplay/tasks/`)

| Task file | What it generates |
|-----------|-------------------|
| `time.py` | Time/date panels |
| `calendar.py` | Google Calendar events |
| `meteo.py` | Weather forecast (Open-Meteo) |
| `nba.py` | NBA scores and upcoming games |
| `stm.py` | Bus arrival times (GTFS realtime) |
| `library.py` | Book return dates (Google Sheets) |
| `message.py` | Time-based messages from `secrets.yaml` |
| `image.py` | `assemble_img`, `publish_img`, `sleep_display` |
| `network.py` | Updates device presence in Redis |
| `monitoring.py` | Logs system health metrics |

### Caching

Generated images are cached as dated PNG files in `tmp/` (e.g., `tmp/nba_results_2026-05-07.png`). Cache is cleared weekly (Monday 1 AM via `weekly_0100`) and on demand via `utils.clear_cache()`.

## Configuration

All secrets and device identifiers live in `secrets.yaml` (not committed). The loader is `edisplay/secrets.py`. Keys include: Google credentials, router credentials, device MAC addresses, bus stop IDs, custom messages.

## Image Constants

Defined in `edisplay/image_config.py`: `WIDTH=480`, `HEIGHT=800`, mode `"1"` (1-bit). Panel heights must sum to 800.

## Key Utilities

- `edisplay/tasks/utils.py` — `independant_chain()` links tasks so a single failure doesn't abort the whole chain; `get_cached_image()`, `fetch_image()`, `clear_cache()`
- `edisplay/fonts.py` — font loading (Quicksand, Fira Code, Audiowide families)
- `edisplay/redis_utils.py` — helpers for reading/writing typed values to Redis
