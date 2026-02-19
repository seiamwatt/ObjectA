import psutil
import curses
import time


def draw_bar(stdscr, y, x, width, percent, label, color_pair):
    filled = int(width * percent / 100)
    empty = width - filled
    stdscr.addstr(y, x, label, curses.A_BOLD)
    stdscr.addstr(y + 1, x, "█" * filled, curses.color_pair(color_pair))
    stdscr.addstr(y + 1, x + filled, "░" * empty, curses.color_pair(3))
    stdscr.addstr(y + 1, x + width + 1, f" {percent:.1f}%")


def draw_chart(stdscr, y, x, width, height, data, color_pair):
    """Draw an ASCII line chart in the terminal."""
    if not data:
        return

    visible = list(data[-width:])
    min_val = 0
    max_val = 100

    # Y-axis labels
    for row in range(height):
        val = max_val - (row / (height - 1)) * (max_val - min_val)
        label = f"{val:5.0f}% │"
        stdscr.addstr(y + row, x, label, curses.color_pair(3))

    # Bottom axis
    stdscr.addstr(y + height, x, "      └" + "─" * width, curses.color_pair(3))
    time_label = f"← {len(data)}s ago"
    now_label = "now →"
    stdscr.addstr(y + height + 1, x + 7, time_label, curses.color_pair(3))
    stdscr.addstr(y + height + 1, x + 7 + width - len(now_label), now_label, curses.color_pair(3))

    chart_x_start = x + 7
    for i, val in enumerate(visible):
        if max_val == min_val:
            dot_row = height // 2
        else:
            dot_row = int((1 - (val - min_val) / (max_val - min_val)) * (height - 1))
        dot_row = max(0, min(height - 1, dot_row))

        if val < 50:
            c = 1  # green
        elif val < 80:
            c = 2  # yellow
        else:
            c = 4  # red

        # Draw dot
        try:
            stdscr.addstr(y + dot_row, chart_x_start + i, "●", curses.color_pair(c) | curses.A_BOLD)
        except curses.error:
            pass

        # Draw vertical fill below dot
        for row in range(dot_row + 1, height):
            try:
                stdscr.addstr(y + row, chart_x_start + i, "│", curses.color_pair(c))
            except curses.error:
                pass


def main(stdscr):
    curses.curs_set(0)
    stdscr.nodelay(True)
    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(1, curses.COLOR_GREEN, -1)
    curses.init_pair(2, curses.COLOR_YELLOW, -1)
    curses.init_pair(3, curses.COLOR_WHITE, -1)
    curses.init_pair(4, curses.COLOR_RED, -1)
    curses.init_pair(5, curses.COLOR_CYAN, -1)

    history = []
    max_history = 120

    while True:
        stdscr.clear()
        max_y, max_x = stdscr.getmaxyx()
        mem = psutil.virtual_memory()
        swap = psutil.swap_memory()

        if mem.percent < 50:
            color = 1
        elif mem.percent < 80:
            color = 2
        else:
            color = 4

        # Header
        stdscr.addstr(1, 2, "╔══════════════════════════════════════════════════╗", curses.color_pair(5))
        stdscr.addstr(2, 2, "║         🖥  LIVE RAM MONITOR                     ║", curses.color_pair(5) | curses.A_BOLD)
        stdscr.addstr(3, 2, "╚══════════════════════════════════════════════════╝", curses.color_pair(5))

        # RAM bar
        bar_width = 40
        draw_bar(stdscr, 5, 4, bar_width, mem.percent, "RAM Usage:", color)

        # RAM details
        total_gb = mem.total / (1024 ** 3)
        used_gb = mem.used / (1024 ** 3)
        avail_gb = mem.available / (1024 ** 3)
        cached_gb = getattr(mem, "cached", 0) / (1024 ** 3)

        stdscr.addstr(7, 4, f"Total:     {total_gb:.2f} GB", curses.A_BOLD)
        stdscr.addstr(8, 4, f"Used:      {used_gb:.2f} GB", curses.color_pair(color))
        stdscr.addstr(9, 4, f"Available: {avail_gb:.2f} GB", curses.color_pair(1))
        stdscr.addstr(10, 4, f"Cached:    {cached_gb:.2f} GB", curses.color_pair(5))

        # Swap
        if swap.total > 0:
            swap_color = 1 if swap.percent < 50 else (2 if swap.percent < 80 else 4)
            draw_bar(stdscr, 12, 4, bar_width, swap.percent, "Swap Usage:", swap_color)
            stdscr.addstr(14, 4, f"Swap:      {swap.used / (1024 ** 3):.2f} / {swap.total / (1024 ** 3):.2f} GB")
        else:
            stdscr.addstr(12, 4, "Swap: N/A")

        # ASCII Plot Graph
        history.append(mem.percent)
        if len(history) > max_history:
            history.pop(0)

        chart_width = min(max_x - 15, 80)
        chart_height = 10
        stdscr.addstr(16, 4, "RAM Usage Over Time:", curses.A_BOLD | curses.color_pair(5))
        draw_chart(stdscr, 17, 4, chart_width, chart_height, history, color)

        # Top processes
        proc_y = 17 + chart_height + 3
        stdscr.addstr(proc_y, 4, "Top Processes by Memory:", curses.A_BOLD)
        procs = []
        for p in psutil.process_iter(["pid", "name", "memory_percent"]):
            try:
                info = p.info
                if info["memory_percent"] is not None:
                    procs.append(info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass

        procs.sort(key=lambda x: x["memory_percent"], reverse=True)
        for i, proc in enumerate(procs[:5]):
            if proc_y + 1 + i < max_y - 2:
                stdscr.addstr(
                    proc_y + 1 + i, 6,
                    f"{proc['pid']:>7}  {proc['name']:<25} {proc['memory_percent']:.1f}%"
                )

        quit_y = min(proc_y + 7, max_y - 1)
        stdscr.addstr(quit_y, 4, "Press 'q' to quit", curses.color_pair(3))
        stdscr.refresh()

        try:
            key = stdscr.getch()
            if key == ord("q"):
                break
        except Exception:
            pass

        time.sleep(1)


if __name__ == "__main__":
    curses.wrapper(main)