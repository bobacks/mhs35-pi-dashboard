# MHS35 Pi Dashboard

A Python dashboard framework for MHS-3.5" SPI LCD displays using the ILI9486 controller and XPT2046 touch controller.

Built and tested on a Raspberry Pi 4 running Debian 13 / Raspberry Pi kernel, where the older `LCD-show` and `fbtft` methods no longer work reliably.

## Screenshots

### Simple Status Dashboard

<img src="screenshots/simple-status.jpg" width="450">

### OpenClaw Dashboard

<img src="screenshots/openclaw-dashboard.jpg" width="450">

## Features

- Custom Python SPI display driver
- ILI9486 display support
- XPT2046 touch support via `/dev/spidev0.1`
- Touch-to-wake support
- Auto-sleep support
- System status dashboard
- Optional OpenClaw server dashboard
- Systemd auto-start
- Works without legacy `fbtft`
- Does not require `LCD-show`

## Tested Hardware

- Raspberry Pi 4B
- MHS-3.5 inch SPI display
- ILI9486 LCD controller
- XPT2046 touch controller
- Debian 13 Trixie
- Kernel `6.18.34+rpt-rpi-v8`

## Required Config

Edit:

```bash
sudo nano /boot/firmware/config.txt
```

Make sure SPI is enabled:

```ini
dtparam=spi=on
```

Do not enable the `ads7846` overlay if using the Python touch reader, because it can claim the SPI device needed by the display.

## Install Dependencies

```bash
sudo apt update
sudo apt install python3-spidev python3-libgpiod python3-pil fonts-dejavu-core
```

## Run Manually

```bash
sudo python3 dashboards/simple_status.py
```

or:

```bash
sudo python3 dashboards/openclaw_status.py
```

## Systemd Service

Copy the service file:

```bash
sudo cp systemd/mhs35-dashboard.service /etc/systemd/system/
```

Reload systemd:

```bash
sudo systemctl daemon-reload
```

Enable on boot:

```bash
sudo systemctl enable mhs35-dashboard.service
sudo systemctl start mhs35-dashboard.service
```

Check status:

```bash
systemctl status mhs35-dashboard.service
```

## How It Works

The display uses:

- `/dev/spidev0.0` for the ILI9486 LCD
- `/dev/spidev0.1` for the XPT2046 touch controller
- GPIO24 for data/command
- GPIO25 for reset

## Why Not LCD-show?

The original LCD-show installer relies on older Raspberry Pi graphics components and legacy framebuffer drivers.

On modern Debian / Raspberry Pi kernels:

- `fbtft_device` may no longer exist
- `fb_ili9486` may no longer exist
- `libraspberrypi-dev` may be unavailable
- `bcm_host.h` may be missing
- `fbcp` may fail to build

This project avoids those dependencies by talking directly to the display over SPI from Python.

## Troubleshooting

### White Screen

Check SPI:

```bash
ls /dev/spidev*
```

Expected:

```text
/dev/spidev0.0
/dev/spidev0.1
```

### Touch Not Working

Do not use the `ads7846` overlay with this project unless you know what you are doing.

### Permission Errors

Run the dashboard with `sudo`.

## OpenClaw Dashboard

The OpenClaw dashboard checks for a running OpenClaw Node process.

## Project Status

Working prototype.

Built through hands-on reverse engineering of the MHS-3.5 inch ILI9486 SPI display on a Raspberry Pi 4.
