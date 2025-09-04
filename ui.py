import io
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk
import mss
import datetime

class SnipOverlay:
    """
    Fullscreen overlay to select a region. Renders a screenshot; user drags a rectangle.
    On mouse release, crops the PIL image and calls on_capture(cropped_image).
    """
    def __init__(self, on_capture):
        self.on_capture = on_capture
        self.root = tk.Tk()
        self.root.attributes("-fullscreen", True)
        self.root.attributes("-topmost", True)
        self.root.configure(cursor="crosshair")
        self.root.title("SnipSum - Select Area (Esc to cancel)")

        # Capture full virtual screen (all monitors)
        with mss.mss() as sct:
            monitor = sct.monitors[0]
            sshot = sct.grab(monitor)
            self.screen_w = sshot.width
            self.screen_h = sshot.height
            img = Image.frombytes("RGB", (sshot.width, sshot.height), sshot.rgb)
            self.screenshot = img

        self.canvas = tk.Canvas(self.root, width=self.screen_w, height=self.screen_h, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        self.photo = ImageTk.PhotoImage(self.screenshot)
        self.bg = self.canvas.create_image(0, 0, image=self.photo, anchor="nw")

        self.start_x = self.start_y = None
        self.rect = None

        self.root.bind("<Escape>", lambda e: self.root.destroy())
        self.canvas.bind("<ButtonPress-1>", self.on_press)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)

        # Dim overlay
        self.overlay = self.canvas.create_rectangle(0, 0, self.screen_w, self.screen_h, fill="#000", stipple="gray25", outline="")

    def on_press(self, event):
        self.start_x, self.start_y = event.x, event.y
        if self.rect:
            self.canvas.delete(self.rect)
        self.rect = self.canvas.create_rectangle(self.start_x, self.start_y, event.x, event.y,
                                                 outline="#00E0FF", width=2)

    def on_drag(self, event):
        if not self.rect: return
        self.canvas.coords(self.rect, self.start_x, self.start_y, event.x, event.y)

    def on_release(self, event):
        if not self.rect:
            self.root.destroy()
            return
        x1, y1, x2, y2 = self.canvas.coords(self.rect)
        # Normalize
        x1, x2 = sorted((int(x1), int(x2)))
        y1, y2 = sorted((int(y1), int(y2)))
        if x2 - x1 < 5 or y2 - y1 < 5:
            self.root.destroy()
            return

        crop = self.screenshot.crop((x1, y1, x2, y2))
        self.root.destroy()
        # Callback
        self.on_capture(crop)

    def run(self):
        self.root.mainloop()


def show_result_window(total, items, original_image=None, raw_text=None):
    root = tk.Tk()
    root.title("SnipSum — Result")

    frm = ttk.Frame(root, padding=12)
    frm.pack(fill="both", expand=True)

    ttk.Label(frm, text="Total", font=("Segoe UI", 14, "bold")).grid(row=0, column=0, sticky="w")
    total_var = tk.StringVar(value=str(total))
    total_entry = ttk.Entry(frm, textvariable=total_var, font=("Segoe UI", 16), width=24)
    total_entry.grid(row=1, column=0, sticky="we", pady=(0, 6))
    total_entry.select_range(0, tk.END)

    def copy_total():
        root.clipboard_clear()
        root.clipboard_append(total_var.get())
        messagebox.showinfo("Copied", "Total copied to clipboard.")

    def save_snapshot():
        if original_image is None:
            messagebox.showwarning("No image", "No snapshot available to save.")
            return
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        fpath = filedialog.asksaveasfilename(defaultextension=".png", initialfile=f"snip_{ts}.png",
                                             filetypes=[("PNG Image", "*.png")])
        if fpath:
            original_image.save(fpath)
            messagebox.showinfo("Saved", f"Saved to {fpath}")

    def re_snip():
        root.destroy()
        # Re-launch overlay
        from app import on_region_captured
        SnipOverlay(on_region_captured).run()

    btns = ttk.Frame(frm)
    btns.grid(row=2, column=0, sticky="we", pady=6)
    ttk.Button(btns, text="Copy Total", command=copy_total).pack(side="left")
    ttk.Button(btns, text="Save Snapshot", command=save_snapshot).pack(side="left", padx=6)
    ttk.Button(btns, text="Re-Snip", command=re_snip).pack(side="left")

    # Numbers list (read-only)
    box = tk.Text(frm, height=10, wrap="none")
    box.grid(row=3, column=0, sticky="nsew", pady=(8, 0))
    frm.rowconfigure(3, weight=1)
    frm.columnconfigure(0, weight=1)

    box.insert("end", "Parsed numbers (included):\n")
    for v, raw in items:
        box.insert("end", f"  {v}    ← from '{raw}'\n")

    if raw_text:
        box.insert("end", "\n--- OCR Raw Text ---\n")
        box.insert("end", raw_text)

    # Make text read-only
    box.configure(state="disabled")

    root.mainloop()
