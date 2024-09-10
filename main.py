import tkinter as tk
from tkinter import messagebox
import pyautogui
from datetime import datetime
import os

class ScreenshotApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Screenshot App")
        self.master.geometry("300x200")

        self.start_x = self.start_y = self.end_x = None
        self.rect = None

        self.select_button = tk.Button(master, text="Select Area", command=self.select_area)
        self.select_button.pack(pady=10)

        self.fullscreen_button = tk.Button(master, text="Capture Full Screen", command=self.capture_full_screen)
        self.fullscreen_button.pack(pady=10)

        self.active_window_button = tk.Button(master, text="Capture Active Window", command=self.capture_active_window)
        self.active_window_button.pack(pady=10)

    def select_area(self):
        self.master.withdraw()  # Hide the main window
        self.screen_canvas = tk.Toplevel(self.master)
        self.screen_canvas.attributes("-fullscreen", True)
        self.screen_canvas.attributes("-alpha", 0.3)  # Make the screen transparent

        self.canvas = tk.Canvas(self.screen_canvas, cursor="cross")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.canvas.bind("<ButtonPress-1>", self.on_button_press)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_button_release)

    def on_button_press(self, event):
        # Start the selection
        self.start_x = event.x
        self.start_y = event.y
        if self.rect:
            self.canvas.delete(self.rect)
        self.rect = self.canvas.create_rectangle(self.start_x, self.start_y, self.start_x, self.start_y, outline="red")

    def on_mouse_drag(self, event):
        # Update the selection rectangle
        self.canvas.coords(self.rect, self.start_x, self.start_y, event.x, event.y)

    def on_button_release(self, event):
        # End the selection and capture the screenshot
        self.end_x = event.x
        self.end_y = event.y
        self.capture_selected_area()
        self.screen_canvas.destroy()
        self.master.deiconify()  # Show the main window again

    def capture_selected_area(self):
        if self.start_x and self.start_y and self.end_x and self.end_y:
            x = min(self.start_x, self.end_x)
            y = min(self.start_y, self.end_y)
            width = abs(self.end_x - self.start_x)
            height = abs(self.end_y - self.start_y)
            region = (x, y, width, height)
            self.take_screenshot(region)
        else:
            messagebox.showerror("Error", "No area selected")

    def capture_full_screen(self):
        # Hide the app window
        self.master.withdraw()

        # Small delay to ensure the window is hidden
        self.master.after(200, self.take_full_screen_screenshot)

    def take_full_screen_screenshot(self):
        # Take the screenshot of the full screen
        self.take_screenshot()

        # Restore the app window
        self.master.deiconify()

    def capture_active_window(self):
        # Hide the app window
        self.master.withdraw()

        # Small delay to ensure the window is hidden
        self.master.after(200, self.take_active_window_screenshot)

    def take_active_window_screenshot(self):
        # Get the active window
        window = pyautogui.getActiveWindow()
        if window:
            bbox = window.box
            region = (bbox.left, bbox.top, bbox.width, bbox.height)
            self.take_screenshot(region)
        else:
            messagebox.showerror("Error", "No active window found")

        # Restore the app window
        self.master.deiconify()

    def take_screenshot(self, region=None):
        save_path = "screenshots"
        if not os.path.exists(save_path):
            os.makedirs(save_path)
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        screenshot_file = os.path.join(save_path, f"screenshot_{timestamp}.png")

        screenshot = pyautogui.screenshot(region=region)
        screenshot.save(screenshot_file)
        # messagebox.showinfo("Screenshot", f"Screenshot saved as {screenshot_file}")

if __name__ == "__main__":
    root = tk.Tk()
    app = ScreenshotApp(root)
    root.mainloop()
