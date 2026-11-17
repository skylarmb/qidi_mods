# qidi_mods

Local changes to the QIDI Max4 printer (`qidi@10.0.4.69`). A firmware update can delete these files. Run `./install.sh` to copy them back.

## Mods

- **Box humidity chart** (`klipper/extras/box_humidity.py`, `config/box_humidity.cfg`). This adds a `Box1_Humidity` sensor to the Fluidd Thermals chart. The value is %RH, but Fluidd shows it with a °C unit. Moonraker keeps about 20 minutes of chart history.

## Install

```sh
./install.sh [user@host]
```

The script copies the files, adds `[include box_humidity.cfg]` to `printer.cfg`, and restarts Klipper through the Moonraker API. If Klipper does not reach the `ready` state, the script sends `FIRMWARE_RESTART`. The restart stops an active box drying cycle.
