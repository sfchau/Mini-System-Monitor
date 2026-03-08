import tkinter as tk
from tkinter import Canvas, ttk
import psutil


REFRESH_INTERVAL = 2000  
WIDTH, HEIGHT = 700, 500
CIRCLE_RADIUS = 70
TOP_PROCESSES_COUNT = 8

PASTEL_COLORS = {
    "CPU": "#FFD1DC",     
    "Memory": "#B2DFDB",  
    "Disk": "#FFF9C4",    
}

def get_system_crumbs():
    cpu = psutil.cpu_percent()
    memory = psutil.virtual_memory().percent
    disk = psutil.disk_usage('/').percent
    return cpu, memory, disk

def get_top_processes(n=TOP_PROCESSES_COUNT):
    processes = []
    total_mem = psutil.virtual_memory().total
    for proc in psutil.process_iter(['name', 'cpu_percent', 'memory_percent']):
        try:
            if proc.info['name'] in ('System Idle Process', 'Idle'):
                continue
            cpu_perc = proc.info['cpu_percent'] / psutil.cpu_count()
            mem_mb = proc.info['memory_percent'] * total_mem / 100 / (1024 ** 2)
            processes.append({
                'name': proc.info['name'],
                'cpu_percent': cpu_perc,
                'memory_mb': mem_mb
            })
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    processes.sort(key=lambda x: x['memory_mb'], reverse=True)
    return processes[:n]

def draw_gauge(canvas, x, y, percent, color, label):
    canvas.create_oval(x - CIRCLE_RADIUS, y - CIRCLE_RADIUS,
                       x + CIRCLE_RADIUS, y + CIRCLE_RADIUS,
                       fill="#f0f0f0", outline="")
    angle = percent * 3.6
    canvas.create_arc(x - CIRCLE_RADIUS, y - CIRCLE_RADIUS,
                      x + CIRCLE_RADIUS, y + CIRCLE_RADIUS,
                      start=90, extent=-angle, fill=color, outline="")
    canvas.create_text(x, y, text=f"{label}\n{percent:.0f}%", font=("Comic Sans MS", 14), fill="#555")

def update():
    canvas.delete("all")
    cpu, mem, disk = get_system_crumbs()
    draw_gauge(canvas, WIDTH//4, 100, cpu, PASTEL_COLORS["CPU"], "CPU")
    draw_gauge(canvas, WIDTH//2, 100, mem, PASTEL_COLORS["Memory"], "Memory")
    draw_gauge(canvas, 3*WIDTH//4, 100, disk, PASTEL_COLORS["Disk"], "Disk")

    for row in tree.get_children():
        tree.delete(row)
    for proc in get_top_processes():
        tree.insert("", "end", values=(proc['name'], f"{proc['cpu_percent']:.1f}%", f"{proc['memory_mb']:.0f} MB"))

    root.after(REFRESH_INTERVAL, update)


root = tk.Tk()
root.title("Combing Crumbs")
root.configure(bg="#fefefe")
root.resizable(False, False)


screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
x = (screen_width - WIDTH) // 2
y = (screen_height - HEIGHT) // 2
root.geometry(f"{WIDTH}x{HEIGHT}+{x}+{y}")


canvas = Canvas(root, width=WIDTH, height=200, bg="#fefefe", highlightthickness=0)
canvas.pack()


columns = ("Process", "CPU %", "Memory MB")
tree = ttk.Treeview(root, columns=columns, show='headings', height=TOP_PROCESSES_COUNT)
for col in columns:
    tree.heading(col, text=col)
    tree.column(col, anchor="center", width=int(WIDTH/len(columns)) - 20)
tree.pack(fill="both", expand=True, padx=10, pady=10)


style = ttk.Style()
style.theme_use("clam")
style.configure("Treeview",
                background="#fefefe",
                foreground="#555",
                rowheight=25,
                fieldbackground="#fefefe",
                font=("Comic Sans MS", 10))
style.map('Treeview', background=[('selected', '#AEDFF7')])


for proc in psutil.process_iter():
    try:
        proc.cpu_percent(interval=None)
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        continue
psutil.cpu_percent(interval=None)

update()
root.mainloop()