#!/usr/bin/env bash
# Copies the mods to the printer and restarts Klipper.
# Run this again after a firmware update deletes the files.
set -euo pipefail

HOST="${1:-qidi@10.0.4.69}"
cd "$(dirname "$0")"

scp klipper/extras/*.py "$HOST:~/klipper/klippy/extras/"
scp config/*.cfg "$HOST:~/printer_data/config/"

# Add the include after [include box.cfg] if printer.cfg does not have it.
ssh "$HOST" 'cfg=~/printer_data/config/printer.cfg
grep -q "^\[include box_humidity.cfg\]" "$cfg" ||
  sed -i "/^\[include box.cfg\]/a [include box_humidity.cfg]" "$cfg"
curl -s -X POST "localhost:7125/machine/services/restart?service=klipper"
# The box MCU shuts down if the host stops while the box heater is on.
# Wait for Klipper to start, then send FIRMWARE_RESTART if it is not ready.
for i in $(seq 1 30); do
  state=$(curl -s localhost:7125/printer/info | grep -o "\"state\":\"[a-z]*\"")
  echo "$state" | grep -q -e ready -e error && break
  sleep 3
done
echo "$state" | grep -q ready ||
  curl -s -X POST localhost:7125/printer/firmware_restart'
