# ESP32 basics

PlatformIO project for learning the ESP32 (board `esp32dev`, port `/dev/cu.usbserial-0001`).

## Setup (once)
```
cd esp32_basics
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

## Build, flash, monitor
```
.venv/bin/pio run -t upload       # compile and flash
.venv/bin/pio device monitor      # serial output (Ctrl+C to quit)
.venv/bin/esptool chip-id         # check the board is detected
```
The first build downloads the toolchain and takes a few minutes.
