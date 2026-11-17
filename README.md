# qidi_mods

Local changes to the QIDI Max4 printer (`qidi@10.0.4.69`). A firmware update can delete these files. Run `./install.sh` to copy them back.

## Mods

- **Box humidity chart** (`klipper/extras/box_humidity.py`, `config/box_humidity.cfg`). This adds a `Box1_Humidity` sensor to the Fluidd Thermals chart. The value is %RH, but Fluidd shows it with a °C unit. Moonraker keeps about 20 minutes of chart history.
- **Logitech Brio camera** (`config/crowsnest.conf`). `[cam 2]` streams the Brio at 1080p and 15 fps on port 8081 (`/webcam2/`). `[cam 1]` (the built-in camera, port 8080, `/webcam/`) is commented out. Only one camera can stream at a time, because both cameras share one USB 2.0 bus and each one reserves more than half of its bandwidth. To swap cameras, comment out one section and uncomment the other. In Fluidd, the camera "Main" uses `/webcam/` and "Logitech" uses `/webcam2/`. Moonraker stores these Fluidd entries, so `install.sh` does not set them.

## Install

```sh
./install.sh [user@host]
```

The script copies the files, adds `[include box_humidity.cfg]` to `printer.cfg`, and restarts crowsnest and Klipper through the Moonraker API. If Klipper does not reach the `ready` state, the script sends `FIRMWARE_RESTART`. The restart stops an active box drying cycle.
