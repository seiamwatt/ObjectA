#!/usr/bin/env python3
"""
🤖 ASSEMBLY LINE MISSION CONTROL — Rich Terminal Dashboard
A live demo dashboard for monitoring robots on an assembly line.
All data is simulated for demonstration purposes.
"""

import time
import random
import platform
from datetime import datetime, timedelta
from collections import deque

from rich.console import Console
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.progress import (
    BarColumn,
    Progress,
    SpinnerColumn,
    TextColumn,
    TimeElapsedColumn,
)
from rich.table import Table
from rich.text import Text
from rich.align import Align
from rich import box
from rich.rule import Rule
from rich.padding import Padding

console = Console()

# ── Configuration ──────────────────────────────────────────────────────────────
HISTORY = 40
_start = time.time()

# ── Robot Definitions ──────────────────────────────────────────────────────────
ROBOTS = [
    {
        "id": "ARM-01",
        "name": "Welding Alpha",
        "model": "FANUC R-2000iC/165F",
        "task": "Chassis Welding",
        "zone": "Zone A",
        "active": True,
        "health": 96,
        "temp": 42.3,
        "cycles_today": 847,
        "target_cycles": 1000,
        "error_code": None,
        "uptime_hrs": 11.4,
        "last_maintenance": "2026-02-10",
        "speed_pct": 88,
    },
    {
        "id": "ARM-02",
        "name": "Painter Beta",
        "model": "ABB IRB 5500-25",
        "task": "Body Painting",
        "zone": "Zone B",
        "active": True,
        "health": 91,
        "temp": 38.7,
        "cycles_today": 612,
        "target_cycles": 800,
        "error_code": None,
        "uptime_hrs": 9.2,
        "last_maintenance": "2026-02-14",
        "speed_pct": 92,
    },
    {
        "id": "ARM-03",
        "name": "Assembler Gamma",
        "model": "KUKA KR 360 R2830",
        "task": "Door Assembly",
        "zone": "Zone C",
        "active": True,
        "health": 78,
        "temp": 51.2,
        "cycles_today": 534,
        "target_cycles": 750,
        "error_code": "W-012",
        "uptime_hrs": 7.8,
        "last_maintenance": "2026-01-28",
        "speed_pct": 71,
    },
    {
        "id": "ARM-04",
        "name": "Inspector Delta",
        "model": "UR10e + Vision",
        "task": "Quality Check",
        "zone": "Zone D",
        "active": True,
        "health": 99,
        "temp": 31.5,
        "cycles_today": 1203,
        "target_cycles": 1200,
        "error_code": None,
        "uptime_hrs": 11.9,
        "last_maintenance": "2026-02-16",
        "speed_pct": 100,
    },
    {
        "id": "ARM-05",
        "name": "Lifter Epsilon",
        "model": "FANUC M-900iB/700",
        "task": "Heavy Lifting",
        "zone": "Zone A",
        "active": False,
        "health": 45,
        "temp": 22.0,
        "cycles_today": 0,
        "target_cycles": 500,
        "error_code": "E-307",
        "uptime_hrs": 0,
        "last_maintenance": "2026-01-15",
        "speed_pct": 0,
    },
    {
        "id": "ARM-06",
        "name": "Sealer Zeta",
        "model": "ABB IRB 6700-200",
        "task": "Adhesive Sealing",
        "zone": "Zone B",
        "active": True,
        "health": 87,
        "temp": 44.1,
        "cycles_today": 701,
        "target_cycles": 850,
        "error_code": None,
        "uptime_hrs": 10.1,
        "last_maintenance": "2026-02-08",
        "speed_pct": 83,
    },
]

# ── Simulated history ─────────────────────────────────────────────────────────
production_history = deque(maxlen=HISTORY)
defect_history = deque(maxlen=HISTORY)
throughput_history = deque(maxlen=HISTORY)
energy_history = deque(maxlen=HISTORY)
event_log = deque(maxlen=14)

# Seed history
for i in range(HISTORY):
    production_history.append(random.randint(70, 100))
    defect_history.append(random.uniform(0.5, 3.5))
    throughput_history.append(random.randint(140, 190))
    energy_history.append(random.uniform(45, 75))

# Seed log
EVENTS = [
    "🤖 ARM-01 completed weld cycle #847",
    "🎨 ARM-02 paint booth pressure nominal",
    "⚠️  ARM-03 joint 4 torque above threshold — monitoring",
    "✅ ARM-04 quality check PASS — batch #1203",
    "🔴 ARM-05 offline — motor fault E-307 detected",
    "🔧 ARM-06 adhesive cartridge replaced",
    "📦 Conveyor belt speed adjusted to 1.2 m/s",
    "🌡  Zone A ambient temp: 23.1°C — nominal",
    "📊 Shift output: 3,897 units (target: 4,100)",
    "🔋 Energy consumption spike in Zone B — investigating",
    "✅ Safety perimeter scan — all clear",
    "📡 PLC heartbeat OK — cycle time 0.8ms",
    "🛠  Preventive maintenance scheduled for ARM-03 tonight",
    "🚨 Emergency stop test — Zone D — PASSED",
    "📈 OEE trending upward: 84.2% → 86.7%",
    "🤖 ARM-01 recalibrated — drift corrected +0.02mm",
    "💾 Backup of robot programs completed",
    "🔄 Shift handover in 45 minutes",
]

for _ in range(8):
    ts = (datetime.now() - timedelta(seconds=random.randint(10, 300))).strftime("%H:%M:%S")
    event_log.appendleft((ts, random.choice(EVENTS)))

# ── Sparkline renderer ─────────────────────────────────────────────────────────
SPARK_CHARS = " ▁▂▃▄▅▆▇█"


def sparkline(data, color="green"):
    mn = min(data) if data else 0
    mx = max(max(data), mn + 1)
    txt = Text()
    for v in data:
        idx = int((v - mn) / (mx - mn) * (len(SPARK_CHARS) - 1))
        txt.append(SPARK_CHARS[idx], style=color)
    return txt


def gauge(value, width=20, color="green", label=True):
    if value > 80:
        color = "red" if color == "green" else color
    elif value > 60:
        color = "yellow" if color == "green" else color
    filled = int(value / 100 * width)
    bar = "█" * filled + "░" * (width - filled)
    if label:
        return Text(f"[{bar}] {value:5.1f}%", style=color)
    return Text(f"[{bar}]", style=color)


# ── Header ─────────────────────────────────────────────────────────────────────
def make_header():
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    uptime = int(time.time() - _start)
    h, rem = divmod(uptime, 3600)
    m, s = divmod(rem, 60)

    active = sum(1 for r in ROBOTS if r["active"])
    total = len(ROBOTS)

    title = Text()
    title.append(" 🏭 ASSEMBLY LINE MISSION CONTROL ", style="bold bright_cyan")
    title.append("│", style="dim")
    title.append(f" {now} ", style="bright_white")
    title.append("│", style="dim")
    title.append(f" ⏱ SHIFT {h:02d}:{m:02d}:{s:02d} ", style="bright_green")
    title.append("│", style="dim")
    title.append(f" 🤖 {active}/{total} ACTIVE ", style="bright_yellow")
    title.append("│", style="dim")

    # Overall line status
    if active == total:
        title.append(" ● LINE RUNNING ", style="bold bright_green")
    elif active > 0:
        title.append(" ● DEGRADED ", style="bold bright_yellow")
    else:
        title.append(" ● LINE DOWN ", style="bold bright_red")

    return Panel(Align.center(title), style="bold blue", box=box.HEAVY, padding=(0, 1))


# ── Robot Status Panel ─────────────────────────────────────────────────────────
def make_robot_panel():
    table = Table(
        box=box.SIMPLE_HEAVY,
        show_header=True,
        header_style="bold white",
        expand=True,
        padding=(0, 1),
    )
    table.add_column("ID", style="bold cyan", width=7)
    table.add_column("Name", style="bright_white", width=16)
    table.add_column("Status", justify="center", width=10)
    table.add_column("Health", width=14)
    table.add_column("Temp", justify="right", width=7)
    table.add_column("Speed", justify="right", width=7)
    table.add_column("Task", style="dim", width=16)

    for r in ROBOTS:
        # Status
        if not r["active"]:
            status = Text("⬤ OFFLINE", style="bold red")
        elif r["error_code"]:
            status = Text("⬤ WARNING", style="bold yellow")
        else:
            status = Text("⬤ ONLINE", style="bold green")

        # Health bar
        h = r["health"]
        hcol = "green" if h > 80 else ("yellow" if h > 50 else "red")
        health_bar = Text()
        filled = int(h / 100 * 8)
        health_bar.append("█" * filled, style=hcol)
        health_bar.append("░" * (8 - filled), style="dim")
        health_bar.append(f" {h}%", style=f"bold {hcol}")

        # Temp
        t = r["temp"]
        tcol = "green" if t < 40 else ("yellow" if t < 50 else "red")
        temp = Text(f"{t:.1f}°C", style=tcol)

        # Speed
        s = r["speed_pct"]
        scol = "green" if s > 80 else ("yellow" if s > 50 else "red")
        speed = Text(f"{s}%", style=scol)

        table.add_row(r["id"], r["name"], status, health_bar, temp, speed, r["task"])

    return Panel(
        table,
        title="[bold cyan]🤖 ROBOT FLEET STATUS[/]",
        border_style="cyan",
        box=box.ROUNDED,
    )


# ── Production Output Panel ────────────────────────────────────────────────────
def make_production_panel():
    total_today = sum(r["cycles_today"] for r in ROBOTS)
    total_target = sum(r["target_cycles"] for r in ROBOTS)
    pct = (total_today / total_target * 100) if total_target else 0

    table = Table(box=None, show_header=False, padding=(0, 1), expand=True)
    table.add_column("Label", style="dim green", width=12)
    table.add_column("Bar", ratio=1)
    table.add_column("Val", justify="right", style="bold", width=14)

    for r in ROBOTS:
        if not r["active"]:
            continue
        rpct = (r["cycles_today"] / r["target_cycles"] * 100) if r["target_cycles"] else 0
        col = "green" if rpct >= 80 else ("yellow" if rpct >= 50 else "red")
        bar = gauge(min(rpct, 100), width=14, color=col)
        table.add_row(r["id"], bar, f"{r['cycles_today']}/{r['target_cycles']}")

    spark = sparkline(throughput_history, color="green")

    content = Table.grid(expand=True)
    content.add_row(table)
    content.add_row(Rule(style="dim green"))
    content.add_row(Text("Throughput/min ", style="dim") + spark)
    content.add_row(
        Text(f"Total: {total_today:,} / {total_target:,}  ({pct:.1f}%)", style="bold bright_green")
    )

    return Panel(
        content,
        title="[bold green]📦 PRODUCTION OUTPUT[/]",
        border_style="green",
        box=box.ROUNDED,
    )


# ── Quality / Defect Panel ─────────────────────────────────────────────────────
def make_quality_panel():
    current_defect = defect_history[-1]
    avg_defect = sum(defect_history) / len(defect_history)

    spark = sparkline(defect_history, color="red")

    oee = random.uniform(83, 88)
    yield_rate = 100 - current_defect
    first_pass = random.uniform(96, 99)

    table = Table(box=None, show_header=False, padding=(0, 1), expand=True)
    table.add_column("Metric", style="dim", width=16)
    table.add_column("Value", style="bold bright_white", justify="right")

    table.add_row("OEE", Text(f"{oee:.1f}%", style="bold bright_green"))
    table.add_row("Yield Rate", Text(f"{yield_rate:.1f}%", style="bold bright_green"))
    table.add_row("First Pass Yield", Text(f"{first_pass:.1f}%", style="bold bright_green"))
    table.add_row("Defect Rate", Text(f"{current_defect:.2f}%", style="bold yellow"))
    table.add_row("Avg Defect Rate", Text(f"{avg_defect:.2f}%", style="dim"))

    content = Table.grid(expand=True)
    content.add_row(table)
    content.add_row(Rule(style="dim red"))
    content.add_row(Text("Defect Trend ", style="dim") + spark)

    return Panel(
        content,
        title="[bold red]🔍 QUALITY METRICS[/]",
        border_style="red",
        box=box.ROUNDED,
    )


# ── Robot Detail / Model Info ──────────────────────────────────────────────────
def make_detail_panel():
    table = Table(
        box=box.SIMPLE,
        show_header=True,
        header_style="bold white",
        expand=True,
        padding=(0, 1),
    )
    table.add_column("ID", style="bold cyan", width=7)
    table.add_column("Model", style="bright_white", width=22)
    table.add_column("Zone", justify="center", width=7)
    table.add_column("Uptime", justify="right", width=7)
    table.add_column("Last Maint.", justify="right", width=12)
    table.add_column("Errors", justify="center", width=7)

    for r in ROBOTS:
        err = Text(r["error_code"] or "—", style="bold red" if r["error_code"] else "dim green")
        up = Text(f"{r['uptime_hrs']:.1f}h", style="bright_white" if r["active"] else "dim")

        # Days since maintenance
        maint = r["last_maintenance"]
        days_ago = (datetime.now() - datetime.strptime(maint, "%Y-%m-%d")).days
        mcol = "green" if days_ago < 14 else ("yellow" if days_ago < 30 else "red")
        maint_txt = Text(f"{maint} ({days_ago}d)", style=mcol)

        table.add_row(r["id"], r["model"], r["zone"], up, maint_txt, err)

    return Panel(
        table,
        title="[bold white]📋 ROBOT DETAILS & MAINTENANCE[/]",
        border_style="white",
        box=box.ROUNDED,
    )


# ── Energy Panel ───────────────────────────────────────────────────────────────
def make_energy_panel():
    current = energy_history[-1]
    avg = sum(energy_history) / len(energy_history)
    spark = sparkline(energy_history, color="yellow")

    table = Table(box=None, show_header=False, padding=(0, 1), expand=True)
    table.add_column("Metric", style="dim yellow", width=14)
    table.add_column("Value", style="bold bright_white", justify="right")

    table.add_row("Current Draw", Text(f"{current:.1f} kW", style="bold bright_yellow"))
    table.add_row("Average", Text(f"{avg:.1f} kW", style="dim"))
    table.add_row("Peak Today", Text(f"{max(energy_history):.1f} kW", style="bold red"))
    table.add_row("Cost/hr (est)", Text(f"${current * 0.12:.2f}", style="bold bright_white"))

    content = Table.grid(expand=True)
    content.add_row(table)
    content.add_row(Rule(style="dim yellow"))
    content.add_row(Text("Power Trend ", style="dim") + spark)

    return Panel(
        content,
        title="[bold yellow]⚡ ENERGY[/]",
        border_style="yellow",
        box=box.ROUNDED,
    )


# ── Assembly Line Floor Map ─────────────────────────────────────────────────────
def make_floormap_panel():
    """Render an ASCII diagram of the assembly line with color-coded robot stations."""

    # Animated conveyor tick
    tick_idx = int(time.time() * 2) % 4
    conveyor_chars = ["═══▶", "══▶═", "═▶══", "▶═══"]
    cseg = conveyor_chars[tick_idx]

    # Build a lookup for quick status
    def status_style(r):
        if not r["active"]:
            return "bold red"
        elif r["error_code"]:
            return "bold yellow"
        return "bold green"

    def status_icon(r):
        if not r["active"]:
            return "⬤"
        elif r["error_code"]:
            return "⬤"
        return "⬤"

    def bot_box(r, width=22):
        """Create a small box for a robot station."""
        st = status_style(r)
        icon = status_icon(r)
        txt = Text()
        # Top border
        txt.append("┌" + "─" * (width - 2) + "┐\n", style="dim " + ("red" if not r["active"] else ("yellow" if r["error_code"] else "green")))
        # Robot ID + status dot
        line1 = f" {icon} {r['id']} "
        status_label = "OFFLINE" if not r["active"] else ("WARN" if r["error_code"] else "ONLINE")
        pad = width - 2 - len(r["id"]) - len(status_label) - 4
        line1 += " " * max(pad, 1) + status_label + " "
        txt.append("│", style="dim " + ("red" if not r["active"] else ("yellow" if r["error_code"] else "green")))
        txt.append(line1, style=st)
        txt.append("│\n", style="dim " + ("red" if not r["active"] else ("yellow" if r["error_code"] else "green")))
        # Robot name
        name_line = f" {r['name'][:width-4]}"
        name_line += " " * (width - 2 - len(name_line))
        txt.append("│", style="dim " + ("red" if not r["active"] else ("yellow" if r["error_code"] else "green")))
        txt.append(name_line, style="bright_white" if r["active"] else "dim")
        txt.append("│\n", style="dim " + ("red" if not r["active"] else ("yellow" if r["error_code"] else "green")))
        # Task
        task_line = f" {r['task'][:width-4]}"
        task_line += " " * (width - 2 - len(task_line))
        txt.append("│", style="dim " + ("red" if not r["active"] else ("yellow" if r["error_code"] else "green")))
        txt.append(task_line, style="dim cyan")
        txt.append("│\n", style="dim " + ("red" if not r["active"] else ("yellow" if r["error_code"] else "green")))
        # Health + temp mini bar
        h = r["health"]
        hbar_len = 8
        hfilled = int(h / 100 * hbar_len)
        health_str = "█" * hfilled + "░" * (hbar_len - hfilled)
        info_line = f" {health_str} {r['temp']:.0f}°C"
        info_line += " " * (width - 2 - len(info_line))
        hcol = "green" if h > 80 else ("yellow" if h > 50 else "red")
        txt.append("│", style="dim " + ("red" if not r["active"] else ("yellow" if r["error_code"] else "green")))
        txt.append(f" {health_str}", style=hcol)
        temp_s = f" {r['temp']:.0f}°C"
        remaining = width - 2 - 1 - len(health_str) - len(temp_s)
        txt.append(" " * max(remaining, 1), style="dim")
        tcol = "green" if r["temp"] < 40 else ("yellow" if r["temp"] < 50 else "red")
        txt.append(temp_s, style=tcol)
        txt.append(" │\n", style="dim " + ("red" if not r["active"] else ("yellow" if r["error_code"] else "green")))
        # Bottom border
        txt.append("└" + "─" * (width - 2) + "┘", style="dim " + ("red" if not r["active"] else ("yellow" if r["error_code"] else "green")))
        return txt

    # Build the full floor map using a grid
    map_text = Text()

    # Title row with zone labels
    map_text.append("  ╔══════════════════════════════════════════════════════════════════════════════════════════════════╗\n", style="dim cyan")
    map_text.append("  ║", style="dim cyan")
    map_text.append("     ZONE A                    ", style="bold bright_cyan")
    map_text.append("ZONE B                    ", style="bold bright_magenta")
    map_text.append("ZONE C                    ", style="bold bright_yellow")
    map_text.append("        ", style="dim")
    map_text.append("║\n", style="dim cyan")

    # Raw material input
    map_text.append("  ║", style="dim cyan")
    map_text.append("  📥 RAW                                                                                           ", style="dim white")
    map_text.append("║\n", style="dim cyan")

    # Conveyor line top
    conv_full = (cseg * 24)[:96]
    map_text.append("  ║", style="dim cyan")
    map_text.append(f"  {conv_full}", style="dim bright_cyan")
    map_text.append("║\n", style="dim cyan")

    # Station row 1: ARM-01, ARM-02, ARM-03 (top of line)
    row1_bots = [ROBOTS[0], ROBOTS[1], ROBOTS[2]]
    lines_per_box = 6  # each bot_box has 6 lines

    # Build each robot box as list of lines
    def box_lines(r, width=28):
        st = status_style(r)
        bcol = "red" if not r["active"] else ("yellow" if r["error_code"] else "green")
        lines = []
        # line 0: top
        lines.append(("┌" + "─" * (width - 2) + "┐", f"dim {bcol}"))
        # line 1: ID + status
        icon = status_icon(r)
        status_label = "OFFLINE" if not r["active"] else ("WARN" if r["error_code"] else "ONLINE")
        inner = f" {icon} {r['id']}  {status_label}"
        inner += " " * (width - 2 - len(inner))
        lines.append(("│" + inner + "│", st, f"dim {bcol}"))
        # line 2: name
        inner = f" {r['name'][:width-4]}"
        inner += " " * (width - 2 - len(inner))
        lines.append(("│" + inner + "│", "bright_white" if r["active"] else "dim", f"dim {bcol}"))
        # line 3: task
        inner = f" {r['task'][:width-4]}"
        inner += " " * (width - 2 - len(inner))
        lines.append(("│" + inner + "│", "dim cyan", f"dim {bcol}"))
        # line 4: health + temp
        h = r["health"]
        hbar_len = 10
        hfilled = int(h / 100 * hbar_len)
        hbar = "█" * hfilled + "░" * (hbar_len - hfilled)
        hcol = "green" if h > 80 else ("yellow" if h > 50 else "red")
        temp_str = f"{r['temp']:.0f}°C"
        inner = f" {hbar}  {temp_str}  {r['speed_pct']}%"
        inner += " " * (width - 2 - len(inner))
        lines.append(("│" + inner + "│", hcol, f"dim {bcol}"))
        # line 5: bottom
        lines.append(("└" + "─" * (width - 2) + "┘", f"dim {bcol}"))
        return lines

    # Render rows of robot boxes side by side
    def render_bot_row(bots, width=28, prefix="  ║  "):
        all_lines = [box_lines(r, width) for r in bots]
        result = Text()
        for line_idx in range(6):
            result.append(prefix, style="dim cyan")
            for bot_idx, bl in enumerate(all_lines):
                line_data = bl[line_idx]
                if len(line_data) == 2:
                    # Single style line (borders)
                    result.append(line_data[0], style=line_data[1])
                else:
                    # Border + content + border style
                    content = line_data[0]
                    content_style = line_data[1]
                    border_style = line_data[2]
                    result.append("│", style=border_style)
                    result.append(content[1:-1], style=content_style)
                    result.append("│", style=border_style)
                if bot_idx < len(all_lines) - 1:
                    result.append("  ", style="dim")
            # Pad to fill panel width
            result.append("  ║\n", style="dim cyan")
        return result

    # Connection arrows from stations to conveyor
    map_text.append("  ║", style="dim cyan")
    map_text.append("       ╠═══╣              ╠═══╣              ╠═══╣                                    ", style="dim bright_cyan")
    map_text.append("║\n", style="dim cyan")

    # Row 1: top 3 robots
    map_text += render_bot_row([ROBOTS[0], ROBOTS[1], ROBOTS[2]], width=28, prefix="  ║  ")

    # Spacer with conveyor continuation
    map_text.append("  ║", style="dim cyan")
    map_text.append("       ╠═══╣              ╠═══╣              ╠═══╣                                    ", style="dim bright_cyan")
    map_text.append("║\n", style="dim cyan")

    # Second conveyor line
    map_text.append("  ║", style="dim cyan")
    map_text.append(f"  {conv_full}", style="dim bright_cyan")
    map_text.append("║\n", style="dim cyan")

    map_text.append("  ║", style="dim cyan")
    map_text.append("       ╠═══╣              ╠═══╣              ╠═══╣                                    ", style="dim bright_cyan")
    map_text.append("║\n", style="dim cyan")

    # Row 2: bottom 3 robots
    map_text += render_bot_row([ROBOTS[3], ROBOTS[4], ROBOTS[5]], width=28, prefix="  ║  ")

    # Connection + conveyor
    map_text.append("  ║", style="dim cyan")
    map_text.append("       ╠═══╣              ╠═══╣              ╠═══╣                                    ", style="dim bright_cyan")
    map_text.append("║\n", style="dim cyan")

    map_text.append("  ║", style="dim cyan")
    map_text.append(f"  {conv_full}", style="dim bright_cyan")
    map_text.append("║\n", style="dim cyan")

    # Output
    map_text.append("  ║", style="dim cyan")
    map_text.append("                                                                            📤 OUTPUT ", style="dim white")
    map_text.append("║\n", style="dim cyan")
    map_text.append("  ╚══════════════════════════════════════════════════════════════════════════════════════════════════╝\n", style="dim cyan")

    # Legend
    legend = Text()
    legend.append("  ⬤", style="bold green")
    legend.append(" Online  ", style="dim")
    legend.append("⬤", style="bold yellow")
    legend.append(" Warning  ", style="dim")
    legend.append("⬤", style="bold red")
    legend.append(" Offline  ", style="dim")
    legend.append("═▶", style="dim bright_cyan")
    legend.append(" Conveyor Belt", style="dim")
    map_text.append(legend)

    return Panel(
        map_text,
        title="[bold bright_cyan]🗺  ASSEMBLY LINE FLOOR MAP[/]",
        border_style="bright_cyan",
        box=box.ROUNDED,
    )


# ── Event Log ──────────────────────────────────────────────────────────────────
def make_log_panel():
    text = Text()
    for ts, msg in event_log:
        text.append(f"[{ts}] ", style="dim cyan")
        text.append(msg + "\n")
    return Panel(
        Padding(text, (0, 1)),
        title="[bold bright_cyan]📋 LIVE EVENT LOG[/]",
        border_style="bright_cyan",
        box=box.ROUNDED,
    )


# ── Layout builder ─────────────────────────────────────────────────────────────
def build_layout():
    layout = Layout()

    layout.split_column(
        Layout(name="header", size=3),
        Layout(name="robots", size=11),
        Layout(name="floormap", size=28),
        Layout(name="middle"),
        Layout(name="bottom"),
        Layout(name="footer", size=3),
    )

    layout["middle"].split_row(
        Layout(name="production", ratio=2),
        Layout(name="quality", ratio=1),
        Layout(name="energy", ratio=1),
    )

    layout["bottom"].split_row(
        Layout(name="details", ratio=3),
        Layout(name="log", ratio=2),
    )

    return layout


# ── Simulation tick ────────────────────────────────────────────────────────────
def tick():
    """Simulate small changes each cycle."""
    for r in ROBOTS:
        if not r["active"]:
            # Small chance inactive robot comes back online
            if random.random() < 0.02:
                r["active"] = True
                r["error_code"] = None
                r["health"] = random.randint(60, 80)
                ts = datetime.now().strftime("%H:%M:%S")
                event_log.appendleft((ts, f"✅ {r['id']} back online — resuming operations"))
            continue

        # Simulate work
        r["cycles_today"] += random.randint(1, 4)
        r["temp"] += random.uniform(-0.5, 0.5)
        r["temp"] = max(25, min(60, r["temp"]))
        r["health"] += random.uniform(-0.3, 0.1)
        r["health"] = max(20, min(100, r["health"]))
        r["speed_pct"] = max(0, min(100, r["speed_pct"] + random.randint(-2, 2)))
        r["uptime_hrs"] += 0.5 / 3600

        # Random warning
        if r["error_code"] is None and random.random() < 0.005:
            r["error_code"] = f"W-{random.randint(1,99):03d}"
            ts = datetime.now().strftime("%H:%M:%S")
            event_log.appendleft((ts, f"⚠️  {r['id']} warning: {r['error_code']} — monitoring"))

        # Random clear warning
        if r["error_code"] and random.random() < 0.03:
            ts = datetime.now().strftime("%H:%M:%S")
            event_log.appendleft((ts, f"✅ {r['id']} warning {r['error_code']} cleared"))
            r["error_code"] = None

        # Rare breakdown
        if random.random() < 0.002:
            r["active"] = False
            r["error_code"] = f"E-{random.randint(100,999)}"
            r["speed_pct"] = 0
            ts = datetime.now().strftime("%H:%M:%S")
            event_log.appendleft((ts, f"🔴 {r['id']} OFFLINE — fault {r['error_code']}"))

    # Update histories
    production_history.append(random.randint(70, 100))
    defect_history.append(max(0.1, defect_history[-1] + random.uniform(-0.3, 0.3)))
    throughput_history.append(random.randint(140, 190))
    energy_history.append(max(30, min(90, energy_history[-1] + random.uniform(-2, 2))))

    # Random event log
    if random.random() < 0.3:
        ts = datetime.now().strftime("%H:%M:%S")
        event_log.appendleft((ts, random.choice(EVENTS)))


# ── Render ─────────────────────────────────────────────────────────────────────
def render(layout):
    layout["header"].update(make_header())
    layout["robots"].update(make_robot_panel())
    layout["floormap"].update(make_floormap_panel())
    layout["production"].update(make_production_panel())
    layout["quality"].update(make_quality_panel())
    layout["energy"].update(make_energy_panel())
    layout["details"].update(make_detail_panel())
    layout["log"].update(make_log_panel())

    progress = Progress(
        SpinnerColumn(style="cyan"),
        TextColumn("[bold cyan]ASSEMBLY LINE CONTROL[/] "),
        BarColumn(bar_width=None, style="cyan", complete_style="bright_cyan"),
        TextColumn(" "),
        TimeElapsedColumn(),
        TextColumn(" [dim]Press Ctrl+C to exit[/]"),
        expand=True,
    )
    progress.add_task("running", total=None)
    layout["footer"].update(Panel(progress, style="dim blue", box=box.HEAVY, padding=(0, 1)))


# ── Main ───────────────────────────────────────────────────────────────────────
def main():
    layout = build_layout()

    console.print("[bold bright_cyan]🏭 Initializing Assembly Line Mission Control...[/]")
    time.sleep(0.5)

    with Live(layout, refresh_per_second=2, screen=True, console=console):
        while True:
            tick()
            render(layout)
            time.sleep(0.5)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[bold bright_cyan]🏭 Assembly Line Control offline. Goodbye![/]\n")
