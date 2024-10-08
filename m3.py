import os
from datetime import datetime
import tkinter as tk
from tkinter import messagebox
import subprocess
import platform
from functools import partial
from PIL import ImageGrab, Image, ImageTk
import pyautogui
from screeninfo import get_monitors

ImageGrab.grab = partial(ImageGrab.grab, all_screens=True)

class ScreenshotApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Screenshot App")
        self.master.geometry("400x400")  # Increased size for new widgets

        self.start_x = self.start_y = self.end_x = None
        self.rect = None
        self.selected_monitor = 1  # Default to monitor 1
        self.last_screenshot_file = None  # To store the last screenshot file path

        # Toggle Monitor Button
        self.toggle_button = tk.Button(master, text="Switch to Monitor 2", command=self.toggle_monitor)
        self.toggle_button.pack(pady=10)

        # Label to show selected monitor
        self.monitor_label = tk.Label(master, text=f"Selected Monitor: {self.selected_monitor}")
        self.monitor_label.pack(pady=10)

        self.select_button = tk.Button(master, text="Select Area", command=self.select_area)
        self.select_button.pack(pady=10)

        self.fullscreen_button = tk.Button(master, text="Capture Full Screen", command=self.capture_full_screen)
        self.fullscreen_button.pack(pady=10)

        self.active_window_button = tk.Button(master, text="Capture Active Window", command=self.capture_active_window)
        self.active_window_button.pack(pady=10)

        # Button to show last image captured
        self.show_last_image_button = tk.Button(master, text="Show Last Image Captured", command=self.show_last_image)
        self.show_last_image_button.pack(pady=10)

        self.gallery_button = tk.Button(master, text="Show Gallery", command=self.show_gallery)
        self.gallery_button.pack(pady=10)


    def toggle_monitor(self):
        # Toggle between monitors 1 and 2
        if self.selected_monitor == 1:
            self.selected_monitor = 2
            self.toggle_button.config(text="Switch to Monitor 1")
        else:
            self.selected_monitor = 1
            self.toggle_button.config(text="Switch to Monitor 2")
        
        self.update_monitor_label()

    def update_monitor_label(self):
        self.monitor_label.config(text=f"Selected Monitor: {self.selected_monitor}")

    def select_area(self):
        self.master.withdraw()  # Hide the main window
        self.screen_canvas = tk.Toplevel(self.master)
        
        # Remove window decorations
        self.screen_canvas.overrideredirect(True)
        
        # Get monitor info
        monitors = get_monitors()
        monitor = monitors[self.selected_monitor - 1]  # Convert 1-based to 0-based index
        monitor_x = monitor.x
        monitor_y = monitor.y
        monitor_width = monitor.width
        monitor_height = monitor.height

        # Set the position and size of the canvas
        self.screen_canvas.geometry(f"{monitor_width}x{monitor_height}+{monitor_x}+{monitor_y}")

        # Ensure the canvas is on top
        self.screen_canvas.attributes("-topmost", True)

        # Make the screen transparent
        self.screen_canvas.attributes("-alpha", 0.3)  

        # Create and configure the canvas
        self.canvas = tk.Canvas(self.screen_canvas, cursor="cross")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Bind mouse events
        self.canvas.bind("<ButtonPress-1>", self.on_button_press)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_button_release)

        # Ensure the canvas has focus
        self.canvas.focus_set()

        # Bind Escape key to canvas
        self.canvas.bind("<Escape>", self.cancel_selection)

    def cancel_selection(self, event):
        # Close the canvas and restore the main window
        self.screen_canvas.destroy()
        self.master.deiconify()  # Show the main window again

    def on_button_press(self, event):
        self.start_x = event.x
        self.start_y = event.y
        if self.rect:
            self.canvas.delete(self.rect)
        self.rect = self.canvas.create_rectangle(self.start_x, self.start_y, self.start_x, self.start_y, outline="red")

    def on_mouse_drag(self, event):
        self.canvas.coords(self.rect, self.start_x, self.start_y, event.x, event.y)

    def on_button_release(self, event):
        self.end_x = event.x
        self.end_y = event.y
        self.capture_selected_area()
        self.screen_canvas.destroy()
        self.master.deiconify()  # Show the main window again

    def capture_full_screen(self):
        self.master.withdraw()
        self.master.after(200, self.take_full_screen_screenshot)

    def take_full_screen_screenshot(self):
        monitor_region = self.get_monitor_region()
        self.take_screenshot(monitor_region)
        self.master.deiconify()

    def capture_active_window(self):
        self.master.withdraw()
        self.master.after(200, self.take_active_window_screenshot)

    def take_active_window_screenshot(self):
        window = pyautogui.getActiveWindow()
        if window:
            bbox = window.box
            x1 = bbox.left
            y1 = bbox.top
            x2 = bbox.left + bbox.width
            y2 = bbox.top + bbox.height
            region = (x1, y1, x2, y2)
            self.take_screenshot(region)
        else:
            messagebox.showerror("Error", "No active window found")
        self.master.deiconify()

    def get_monitor_region(self):
        monitors = get_monitors()
        if self.selected_monitor <= len(monitors):
            monitor = monitors[self.selected_monitor - 1]
            return (monitor.x, monitor.y, monitor.x + monitor.width, monitor.y + monitor.height)
        else:
            return None

    def take_screenshot(self, region=None):
        save_path = "screenshots"
        if not os.path.exists(save_path):
            os.makedirs(save_path)
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.last_screenshot_file = os.path.join(save_path, f"screenshot_{timestamp}.png")

        if region:
            screenshot = ImageGrab.grab(bbox=region)
        else:
            screenshot = ImageGrab.grab()

        screenshot.save(self.last_screenshot_file)

    def capture_selected_area(self):
        if self.start_x is not None and self.start_y is not None and self.end_x is not None and self.end_y is not None:
            x1 = min(self.start_x, self.end_x)
            y1 = min(self.start_y, self.end_y)
            x2 = max(self.start_x, self.end_x)
            y2 = max(self.start_y, self.end_y)
            region = (x1, y1, x2, y2)
            # Adjust coordinates based on selected monitor
            adjusted_region = self.adjust_coordinates_for_monitor(region)
            self.take_screenshot(adjusted_region)
        else:
            messagebox.showerror("Error", "No area selected")

    def adjust_coordinates_for_monitor(self, region):
        # Get monitor info
        monitors = get_monitors()
        monitor = monitors[self.selected_monitor - 1]
        offset_x = monitor.x
        offset_y = monitor.y

        # Adjust region based on monitor offset
        adjusted_region = (
            region[0] + offset_x,
            region[1] + offset_y,
            region[2] + offset_x,
            region[3] + offset_y
        )
        return adjusted_region

    def show_last_image(self):
        if self.last_screenshot_file and os.path.exists(self.last_screenshot_file):
            # Open and display the last screenshot
            image = Image.open(self.last_screenshot_file)
            image.show()
        else:
            messagebox.showerror("Error", "No screenshot available")



    def show_gallery(self):
        # Create a new window for the gallery
        gallery_window = tk.Toplevel(self.master)
        gallery_window.title("Screenshot Gallery")

        # Create a frame for the gallery images
        gallery_frame = tk.Frame(gallery_window)
        gallery_frame.pack(fill=tk.BOTH, expand=True)

        # Load images from the screenshots folder
        save_path = "screenshots"
        if not os.path.exists(save_path):
            messagebox.showerror("Error", "No screenshots found")
            return

        image_files = [f for f in os.listdir(save_path) if f.endswith('.png')]
        if not image_files:
            messagebox.showinfo("Info", "No images to display")
            return

        # Create a canvas to hold the images
        canvas = tk.Canvas(gallery_frame)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Add a scrollbar
        scrollbar = tk.Scrollbar(gallery_frame, orient=tk.VERTICAL, command=canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        canvas.configure(yscrollcommand=scrollbar.set)

        # Create a frame inside the canvas to hold the images
        image_frame = tk.Frame(canvas)
        canvas.create_window((0, 0), window=image_frame, anchor=tk.NW)

        def open_image(image_path):
            # Function to open the image with the default image viewer
            if platform.system() == "Windows":
                os.startfile(image_path)
            elif platform.system() == "Darwin":  # macOS
                subprocess.run(["open", image_path])
            elif platform.system() == "Linux":
                subprocess.run(["xdg-open", image_path])
            else:
                messagebox.showerror("Error", "Unsupported OS for opening images")

        # Add images to the frame
        for image_file in image_files:
            image_path = os.path.join(save_path, image_file)
            img = Image.open(image_path)
            img.thumbnail((200, 200))  # Resize for display
            img_tk = ImageTk.PhotoImage(img)

            img_label = tk.Label(image_frame, image=img_tk)
            img_label.image = img_tk  # Keep a reference to avoid garbage collection

            # Bind click event to the label
            img_label.bind("<Button-1>", lambda e, path=image_path: open_image(path))
            img_label.pack(side=tk.TOP, padx=10, pady=10)

        # Update scrollregion of the canvas
        image_frame.update_idletasks()
        canvas.config(scrollregion=canvas.bbox(tk.ALL))



if __name__ == "__main__":
    root = tk.Tk()
    app = ScreenshotApp(root)
    root.mainloop()
