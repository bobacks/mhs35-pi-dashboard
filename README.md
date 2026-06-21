# MHS35 Pi Dashboard

A Python dashboard framework for MHS-3.5" SPI LCD displays based on the ILI9486 controller.

Designed for modern Raspberry Pi OS and Debian systems where the legacy LCD-show and fbtft drivers no longer work.

## Features

- ILI9486 display support
- XPT2046 touch support
- Touch wake
- Automatic sleep
- Systemd auto-start
- Custom Python dashboards
- Example OpenClaw dashboard
- Raspberry Pi 4 tested

## Screenshots

### Simple Status Dashboard

(screenshot)

### OpenClaw Dashboard

(screenshot)

## Hardware

Tested with:

- Raspberry Pi 4
- MHS-3.5 inch SPI display
- ILI9486 LCD controller
- XPT2046 touch controller

## Why This Exists

Many MHS35 displays rely on LCD-show and fbtft drivers which no longer work on modern Raspberry Pi kernels.

This project provides a modern Python-based alternative.
