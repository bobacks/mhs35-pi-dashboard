#!/usr/bin/env python3
"""
Simple MHS35 Raspberry Pi status dashboard.

Shows:
- Date/time
- Hostname
- IP address
- Load average
- CPU temperature
- RAM usage
- Disk usage

Requires:
- mhs35_console.py in the same directory or Python path
- SPI enabled in /boot/firmware/config.txt
- /dev/spidev0.0 available for LCD
"""

import time
import socket
import subprocess
import shutil
from mhs35_console import MHS35


DRAW_INTERVAL = 5


def run(cmd: str) -> str:
    try:
        return subprocess.check_output(cmd, shell=True, text=True).strip()
    except Exception:
        return "N/A"


def ip_addr() -> str:
    value = run("hostname -I")
    return value.split()[0] if value else "N/A"


def cpu_temp() -> str:
    value = run("cat /sys/class/thermal/thermal_zone0/temp")
    return f"{int(value) / 1000:.1f}°C" if value.isdigit() else "N/A"


def cpu_load() -> str:
    return run("awk '{print $1, $2, $3}' /proc/loadavg")


def mem_usage() -> str:
    return run("free -h | awk '/Mem:/ {print $3 \" / \" $2}'")


def disk_usage() -> str:
    usage = shutil.disk_usage("/")
    used = usage.used // (1024 ** 3)
    total = usage.total // (1024 ** 3)
    return f"{used}G / {total}G"


def draw_status(display: MHS35) -> None:
    display.clear("black")

    display.text("CLAW STATUS", 20, 15, "lime", 30)
    display.text(time.strftime("%a %d %b %Y  %H:%M:%S"), 20, 60, "yellow", 20)

    display.text(f"Host: {socket.gethostname()}", 20, 105, "white")
    display.text(f"IP:   {ip_addr()}", 20, 135, "cyan")
    display.text(f"Load: {cpu_load()}", 20, 165, "white")
    display.text(f"Temp: {cpu_temp()}", 20, 195, "orange")
    display.text(f"RAM:  {mem_usage()}", 20, 225, "white")
    display.text(f"Disk: {disk_usage()}", 20, 255, "white")

    display.show()


def main() -> None:
    display = MHS35()

    try:
        while True:
            draw_status(display)
            time.sleep(DRAW_INTERVAL)
    finally:
        display.close()


if __name__ == "__main__":
    main()
