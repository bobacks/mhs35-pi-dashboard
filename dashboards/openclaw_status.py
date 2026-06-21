#!/usr/bin/env python3
import time, socket, subprocess, shutil
import spidev
from mhs35_console import MHS35

SLEEP_AFTER = 20
DRAW_INTERVAL = 2

touch = spidev.SpiDev()
touch.open(0, 1)
touch.max_speed_hz = 200000
touch.mode = 0

def read12(cmd):
    r = touch.xfer2([cmd, 0, 0])
    return ((r[1] << 8) | r[2]) >> 3

def touched():
    z1 = read12(0xB0)
    z2 = read12(0xC0)
    return z1 > 50 and z2 > z1

def run(cmd):
    try:
        return subprocess.check_output(cmd, shell=True, text=True).strip()
    except Exception:
        return "N/A"

def ip_addr():
    s = run("hostname -I")
    return s.split()[0] if s else "N/A"

def cpu_percent():
    a = run("awk '/cpu / {print $2+$4, $2+$4+$5}' /proc/stat").split()
    time.sleep(0.06)
    b = run("awk '/cpu / {print $2+$4, $2+$4+$5}' /proc/stat").split()
    if len(a) < 2 or len(b) < 2:
        return 0
    used = float(b[0]) - float(a[0])
    total = float(b[1]) - float(a[1])
    return int((used / total) * 100) if total else 0

def ram_info():
    out = run("free -m | awk '/Mem:/ {print $3, $2, int($3/$2*100)}'").split()
    if len(out) != 3:
        return "N/A", 0
    return f"{out[0]}M/{out[1]}M", int(out[2])

def disk_info():
    u = shutil.disk_usage("/")
    pct = int(u.used / u.total * 100)
    return f"{u.used//(1024**3)}G/{u.total//(1024**3)}G", pct

def temp():
    t = run("cat /sys/class/thermal/thermal_zone0/temp")
    return float(t) / 1000 if t.isdigit() else 0

def uptime():
    s = int(float(run("cat /proc/uptime").split()[0]))
    d = s // 86400
    h = (s % 86400) // 3600
    m = (s % 3600) // 60
    if d:
        return f"{d}d {h}h"
    if h:
        return f"{h}h {m}m"
    return f"{m}m"

def cpu_mhz():
    mhz = run("awk -F= '/arm/ {print int($2/1000000)}' /sys/devices/system/cpu/cpu0/cpufreq/scaling_cur_freq 2>/dev/null")
    return f"{mhz}MHz" if mhz.isdigit() else "N/A"

def openclaw_status():
    proc = run("pgrep -af '/usr/bin/node .*openclaw.*/dist/index.js gateway' | head -1")
    if proc and proc != "N/A":
        return "RUNNING", "lime"
    return "OFFLINE", "red"

last_net = None
def net_speed():
    global last_net
    line = run("cat /proc/net/dev | awk '/eth0|wlan0/ {rx+=$2; tx+=$10} END {print rx, tx}'")
    p = line.split()
    if len(p) < 2:
        return "0K", "0K"
    now = time.time()
    rx, tx = int(p[0]), int(p[1])
    if not last_net:
        last_net = (now, rx, tx)
        return "0K", "0K"
    old_t, old_rx, old_tx = last_net
    dt = max(now - old_t, 0.1)
    last_net = (now, rx, tx)

    def fmt(v):
        v = v / dt
        if v > 1024 * 1024:
            return f"{v/(1024*1024):.1f}M"
        return f"{v/1024:.0f}K"

    return fmt(rx - old_rx), fmt(tx - old_tx)

def col(v, warn, bad):
    if v >= bad:
        return "red"
    if v >= warn:
        return "yellow"
    return "lime"

def bar(d, x, y, w, pct, colour):
    d.draw.rectangle((x, y, x+w, y+17), outline=(70, 85, 90))
    fill = int((w-4) * max(0, min(pct, 100)) / 100)
    d.draw.rectangle((x+2, y+2, x+2+fill, y+15), fill=colour)

def draw_status(d):
    cpu = cpu_percent()
    ram_txt, ram = ram_info()
    disk_txt, disk = disk_info()
    t = temp()
    down, up = net_speed()
    claw, claw_col = openclaw_status()

    health = "OK"
    health_col = "lime"
    if claw != "RUNNING":
        health, health_col = "OPENCLAW", "yellow"
    if t >= 80 or disk >= 90:
        health, health_col = "ALERT", "red"

    d.clear("black")

    d.text("CLAW", 12, 8, "lime", 32)
    d.text(time.strftime("%H:%M"), 250, 13, "white", 28)
    d.draw.ellipse((420, 23, 434, 37), fill=health_col)
    d.text(health, 440, 18, health_col, 15)
    d.draw.line((12, 56, 468, 56), fill="lime", width=2)

    rows = [
        ("CPU", cpu, f"{cpu_mhz()}", col(cpu, 70, 90), 78),
        ("RAM", ram, ram_txt, col(ram, 75, 90), 120),
        ("SSD", disk, disk_txt, col(disk, 80, 90), 162),
    ]

    for label, pct, sub, colour, y in rows:
        d.text(label, 16, y-6, "white", 22)
        bar(d, 82, y, 150, pct, colour)
        d.text(f"{pct:>3}%", 242, y-7, colour, 21)
        d.text(sub, 310, y-4, "cyan", 17)

    d.draw.rectangle((14, 204, 466, 246), outline="cyan", width=2)
    d.text("CLAW", 28, 215, "cyan", 18)
    d.text(claw, 105, 214, claw_col, 20)
    d.text(f"TEMP {t:.0f}°C", 260, 214, col(int(t), 70, 80), 20)

    d.draw.rectangle((14, 254, 466, 286), outline="cyan", width=2)
    d.text(ip_addr(), 28, 261, "cyan", 17)
    d.text(f"↓{down}", 250, 261, "white", 17)
    d.text(f"↑{up}", 350, 261, "lime", 17)

    d.draw.rectangle((14, 294, 466, 318), outline=health_col, width=2)
    d.text(f"UP {uptime()}", 28, 298, "white", 14)
    d.text("v1.0", 332, 298, "yellow", 14)

    d.show()

d = MHS35()
awake = True
last_activity = time.time()
last_draw = 0

try:
    draw_status(d)

    while True:
        now = time.time()

        if touched():
            last_activity = now
            if not awake:
                awake = True
                draw_status(d)
                last_draw = now
                time.sleep(0.4)

        if awake and now - last_draw >= DRAW_INTERVAL:
            draw_status(d)
            last_draw = now

        if awake and now - last_activity >= SLEEP_AFTER:
            d.display_off()
            awake = False

        time.sleep(0.1)

finally:
    touch.close()
    d.close()
