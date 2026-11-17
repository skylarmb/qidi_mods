# AGENTS.md

This repo holds local mods for a QIDI Max4 3D printer. The source of truth is this repo. Edit files here, then copy them to the printer.

## Safety rules

1. Before you restart Klipper, check the print state. Do not restart Klipper if the state is `printing` or `paused`.
   ```sh
   curl -s "http://10.0.4.69/printer/objects/query?print_stats=state"
   ```
2. Do not restart Klipper, Moonraker, or the printer while the user prints. A crowsnest restart is safe at any time.
3. `install.sh` restarts Klipper. Do not run it during a print. To deploy a camera change only, copy `crowsnest.conf` and restart crowsnest.
4. A Klipper restart while the box heater is on puts the box MCU (`mcu_box1`) in shutdown. Klipper then reports "Can not update MCU 'mcu_box1' config as it is shutdown". Send `FIRMWARE_RESTART` to recover:
   ```sh
   curl -s -X POST http://10.0.4.69/printer/firmware_restart
   ```
   A restart also stops a box drying cycle. Tell the user.

## Access

- SSH: `ssh qidi@10.0.4.69`. Key authentication works. Use `-o BatchMode=yes` so a failed key does not hang on a password prompt.
- The SSH client prints a post-quantum key exchange warning on every connection. Filter it: `2>&1 | grep -v -e WARNING -e 'This session' -e 'server may'`.
- `sudo` needs a password. Do not use it. Restart services through the Moonraker API instead.
- The local machine has no `jq` on `PATH`. Use `nix-shell -p jq --run '...'`, or run `python3` on the printer.

## Moonraker API

Moonraker listens on `localhost:7125` on the printer. nginx also serves it at `http://10.0.4.69/` from the LAN.

| Task | Request |
|---|---|
| List Klipper objects | `GET /printer/objects/list` |
| Query objects | `GET /printer/objects/query?<object>&<object>=<field>` (URL-encode spaces as `%20`) |
| Klipper state | `GET /printer/info` (`ready`, `startup`, `shutdown`, `error`) |
| Run G-code | `POST /printer/gcode/script?script=<gcode>` |
| Firmware restart | `POST /printer/firmware_restart` |
| Restart a service | `POST /machine/services/restart?service=<klipper\|crowsnest\|moonraker>` |
| List Fluidd cameras | `GET /server/webcams/list` |
| Change a Fluidd camera | `POST /server/webcams/item` with JSON `{"uid": "...", <fields>}` (`/server/webcams/post` returns 404 on this version) |
| Chart history | `GET /server/temperature_store` |

## Printer layout

| Item | Path on the printer |
|---|---|
| Klipper config | `~/printer_data/config/printer.cfg` |
| Klipper extras | `~/klipper/klippy/extras/` |
| Crowsnest config | `~/printer_data/config/crowsnest.conf` |
| Logs | `~/printer_data/logs/` (`klippy.log`, `moonraker.log`, `crowsnest.log`) |

- Klipper runs Python 3.9. `~/klipper` is not a git repo.
- `klippy.log` is large. Read it with `grep -n` and `tail`, not `cat`.
- Klipper caches imported modules. After you change a `.py` extra, restart the `klipper` service. `RESTART` and `FIRMWARE_RESTART` do not reload the code.
- QIDI ships some extras as compiled `.so` files (for example `aht20_f.so`). Read their data through `get_status()` from the Moonraker query API.
- Sensor types come from `~/klipper/klippy/extras/temperature_sensors.cfg`. This is a firmware file. Do not edit it. Register a new sensor type from a config section that comes before the section that uses it (see `config/box_humidity.cfg`).
- The web UI is a Fluidd fork (`thelegendtubaguy`, `tltg`). The `tltg-optimized-macros` installer also changes Klipper, Moonraker, and system services.
- QIDI AI detection (`algo_app.service`, port 9010) is disabled. Klipper `ai_func_manager` shows detection as enabled, but no service answers it.

## Cameras

- Both cameras share one USB 2.0 bus. Only one camera can stream at a time. The second camera fails with `uvcvideo: Failed to submit URB 0 (-28)` in `dmesg`, and ustreamer serves a NO SIGNAL frame.
- A NO SIGNAL frame still returns HTTP 200. To check a stream, read `http://localhost:<port>/state` on the printer and check `"online": true` and `captured_fps`.
- Crowsnest takes about 45 seconds after a restart to start ustreamer.
- The Fluidd service type "MJPEG stream" is the browser format. It does not depend on the camera format in `crowsnest.conf`.

## Repo workflow

1. Edit files in this repo.
2. Copy the changed files to the printer with `scp`, or run `./install.sh` when no print runs.
3. Check the result on the printer.
4. Update `README.md` when a mod changes.
