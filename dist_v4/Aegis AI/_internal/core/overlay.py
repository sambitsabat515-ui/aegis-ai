import tkinter as tk
import threading
import time

class OverlayManager:
    def __init__(self):
        self.root = None
        self.boxes = []
        self.running = False
        
    def _run_overlay(self):
        self.root = tk.Tk()
        # Make the window transparent and cover the whole screen
        self.root.attributes('-alpha', 0.5)
        self.root.attributes('-transparentcolor', 'white')
        self.root.config(bg='white')
        
        # Remove window decorations and keep on top
        self.root.overrideredirect(True)
        self.root.attributes('-topmost', True)
        
        # Cover the entire screen
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        self.root.geometry(f"{screen_width}x{screen_height}+0+0")
        
        # Create a canvas for drawing
        self.canvas = tk.Canvas(self.root, width=screen_width, height=screen_height, bg='white', highlightthickness=0)
        self.canvas.pack()
        
        self.root.mainloop()
        self.running = False

    def start(self):
        if not self.running:
            self.running = True
            threading.Thread(target=self._run_overlay, daemon=True).start()

    def stop(self):
        if self.running and self.root:
            try:
                self.root.quit()
            except Exception:
                pass
            self.running = False
            self.root = None

    def draw_highlight(self, x, y, w, h, risk="RED", duration=3.0):
        """Draws a box on the screen at the given coordinates"""
        if not self.root or not self.canvas:
            return
            
        color = "red" if risk == "RED" else "yellow"
        
        # Thread-safe canvas update
        def _draw():
            # Draw a thick glowing style box
            box_id = self.canvas.create_rectangle(
                x, y, x + w, y + h, 
                outline=color, width=4, dash=(5, 5)
            )
            
            # Draw a semi-transparent fill
            fill_id = self.canvas.create_rectangle(
                x, y, x + w, y + h,
                fill=color, stipple='gray25', outline=''
            )
            
            # Schedule removal
            self.root.after(int(duration * 1000), lambda: self._remove_box(box_id, fill_id))

        try:
            self.root.after(0, _draw)
        except Exception:
            pass
            
    def _remove_box(self, box_id, fill_id):
        if self.canvas:
            self.canvas.delete(box_id)
            self.canvas.delete(fill_id)

# Singleton-like instance
overlay = OverlayManager()
