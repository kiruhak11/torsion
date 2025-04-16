import tkinter as tk
import math

class TorsionAnimation:
    def __init__(self, parent):
        self.canvas = tk.Canvas(parent, width=300, height=300, bg="white", highlightthickness=0)
        self.canvas.pack()
        self.center_x = 150
        self.center_y = 150
        self.radius = 50
        self.angle = 0
        self.animate()

    def animate(self):
        self.canvas.delete("all")
        self.canvas.create_oval(self.center_x - self.radius, self.center_y - self.radius,
                                self.center_x + self.radius, self.center_y + self.radius, outline="black")
        end_x = self.center_x + self.radius * math.cos(math.radians(self.angle))
        end_y = self.center_y + self.radius * math.sin(math.radians(self.angle))
        self.canvas.create_line(self.center_x, self.center_y, end_x, end_y, fill="red", width=3)
        self.canvas.create_text(self.center_x, self.center_y + self.radius + 20,
                                text=f"Угол: {self.angle}°", font=("Arial", 12))
        self.angle = (self.angle + 5) % 360
        self.canvas.after(100, self.animate)
