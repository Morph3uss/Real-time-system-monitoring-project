import psutil, socket, time, curses, csv, smtplib
from datetime import datetime
from termcolor import colored
from email.mime.text import MIMEText

# Thresholds for alerts
THRESHOLDS = {"cpu": 90, "ram": 85, "network": 90}

# Alert email address
ALERT_EMAIL = "cotedor67@gmail.com"

# ASCII Art of Morpheus and "MATRIX" word
MORPHEUS = r"""
             _______
            /       \
           |  O   O  |
           |    ^    |
           |   '-'   |
            \_______/
"""

MATRIX_ASCII = r"""
███╗   ███╗ █████╗ ████████╗██████╗ ██╗██╗  ██╗
████╗ ████║██╔══██╗╚══██╔══╝██╔══██╗██║╚██╗██╔╝
██╔████╔██║███████║   ██║   ██████╔╝██║ ╚███╔╝ 
██║╚██╔╝██║██╔══██║   ██║   ██╔══██╗██║ ██╔██╗ 
██║ ╚═╝ ██║██║  ██║   ██║   ██║  ██║██║██╔╝ ██╗
╚═╝     ╚═╝╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═╝╚═╝╚═╝  ╚═╝
"""

# System information retrieval
def get_info():
    cpu = psutil.cpu_percent(1)
    ram = psutil.virtual_memory().percent
    net = (psutil.net_io_counters().bytes_sent + psutil.net_io_counters().bytes_recv) / 1024 / 1024
    disk = {p.device: psutil.disk_usage(p.mountpoint).percent for p in psutil.disk_partitions()}
    ip = socket.gethostbyname(socket.gethostname())
    battery = psutil.sensors_battery()
    return cpu, ram, net, disk, battery.percent if battery else None, ip

# Alert checking function
def check_alerts(cpu, ram, net, disk):
    alerts = []
    if cpu > THRESHOLDS["cpu"]:
        alerts.append(f"High CPU usage ({cpu}%)")
    if ram > THRESHOLDS["ram"]:
        alerts.append(f"High RAM usage ({ram}%)")
    if net > THRESHOLDS["network"]:
        alerts.append(f"High Network usage ({net:.2f} MB/s)")
    alerts += [f"Disk {k} full ({v}%)" for k, v in disk.items() if v > 90]
    return alerts

# Email alert function
def send_email(subject, body):
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = ALERT_EMAIL
    msg["To"] = ALERT_EMAIL
    
    # SMTP server configuration (replace with actual details)
    with smtplib.SMTP("smtp.example.com", 587) as server:
        server.starttls()
        server.login("your_email@example.com", "your_password")
        server.sendmail(ALERT_EMAIL, ALERT_EMAIL, msg.as_string())

# Function to log metrics to a CSV file
def log_to_csv(cpu, ram, net, disk, battery, ip):
    with open("system_metrics.csv", mode="a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([datetime.now(), cpu, ram, net, ip] + list(disk.values()) + [battery])

# Real-time display function
def display_report(stdscr):
    curses.curs_set(0)
    curses.start_color()
    curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)

    try:
        while True:
            cpu, ram, net, disk, battery, ip = get_info()
            alerts = check_alerts(cpu, ram, net, disk)

            # Send email if alerts are found
            if alerts:
                send_email("Critical System Alert", "\n".join(alerts))

            # Log metrics to CSV
            log_to_csv(cpu, ram, net, disk, battery, ip)

            # Clear and display ASCII Art and system information
            stdscr.clear()
            stdscr.addstr(MORPHEUS + "\n", curses.color_pair(1))
            stdscr.addstr(MATRIX_ASCII + "\n", curses.color_pair(1))
            stdscr.addstr(f"💻 Report at {datetime.now()}\n", curses.color_pair(1))
            
            if alerts:
                stdscr.addstr("\n".join(alerts) + "\n", curses.color_pair(1))
            else:
                stdscr.addstr("No alerts.\n", curses.color_pair(1))
            
            stdscr.addstr(f"CPU: {cpu}%  RAM: {ram}%  Network: {net:.2f} MB/s\n")
            stdscr.addstr(f"IP: {ip}\n")
            for part, usage in disk.items():
                stdscr.addstr(f"Disk {part}: {usage}%\n")
            if battery is not None:
                stdscr.addstr(f"Battery: {battery}%\n")

            stdscr.refresh()
            time.sleep(1)  # Run every second for real-time monitoring

    except KeyboardInterrupt:
        stdscr.addstr("\nExiting system monitor...\n")
        stdscr.refresh()
        time.sleep(1)

# Main function to start the curses display
if __name__ == "__main__":
    curses.wrapper(display_report)
