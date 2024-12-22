import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageDraw, ImageTk

class DrawInBox:
    def __init__(self, root):
        self.root = root
        self.root.title("Draw in a Box")

        # Set up canvas
        self.canvas_width = 500
        self.canvas_height = 500
        self.canvas = tk.Canvas(root, width=self.canvas_width, height=self.canvas_height, bg="white")
        self.canvas.pack()

        # Variables for drawing
        self.drawing = False
        self.last_x, self.last_y = None, None
        self.color = "black"
        self.brush_size = 2

        # Image for saving
        self.image = Image.new("RGB", (self.canvas_width, self.canvas_height), "white")
        self.draw = ImageDraw.Draw(self.image)

        # Set up controls
        control_frame = tk.Frame(root)
        control_frame.pack()

        # Size controls
        tk.Label(control_frame, text="Width:").pack(side="left")
        self.width_entry = tk.Entry(control_frame, width=5)
        self.width_entry.insert(0, str(self.canvas_width))
        self.width_entry.pack(side="left")

        tk.Label(control_frame, text="Height:").pack(side="left")
        self.height_entry = tk.Entry(control_frame, width=5)
        self.height_entry.insert(0, str(self.canvas_height))
        self.height_entry.pack(side="left")

        tk.Button(control_frame, text="Resize", command=self.resize_canvas).pack(side="left")

        # Brush size controls
        tk.Label(control_frame, text="Brush Size:").pack(side="left")
        self.brush_size_entry = tk.Entry(control_frame, width=5)
        self.brush_size_entry.insert(0, str(self.brush_size))
        self.brush_size_entry.pack(side="left")

        tk.Button(control_frame, text="Set Brush Size", command=self.set_brush_size).pack(side="left")

        # Load and Save buttons
        tk.Button(control_frame, text="Save Image", command=self.save_image).pack(side="left")
        tk.Button(control_frame, text="Load Image", command=self.load_image).pack(side="left")

        # Color buttons
        self.color_frame = tk.Frame(root)
        self.color_frame.pack()
        colors = ["black", "red", "blue", "green", "yellow", "purple"]
        for color in colors:
            btn = tk.Button(self.color_frame, bg=color, width=2, command=lambda c=color: self.change_color(c))
            btn.pack(side="left")

        # Bind events
        self.canvas.bind("<ButtonPress-1>", self.start_drawing)
        self.canvas.bind("<B1-Motion>", self.draw_on_canvas)
        self.canvas.bind("<ButtonRelease-1>", self.stop_drawing)

    def change_color(self, new_color):
        self.color = new_color

    def start_drawing(self, event):
        self.drawing = True
        self.last_x, self.last_y = event.x, event.y

    def draw_on_canvas(self, event):
        if self.drawing:
            x, y = event.x, event.y
            self.canvas.create_line(self.last_x, self.last_y, x, y, fill=self.color, width=self.brush_size)
            self.draw.line([self.last_x, self.last_y, x, y], fill=self.color, width=self.brush_size)
            self.last_x, self.last_y = x, y

    def stop_drawing(self, event):
        self.drawing = False
        self.last_x, self.last_y = None, None

    def resize_canvas(self):
        try:
            new_width = int(self.width_entry.get())
            new_height = int(self.height_entry.get())
            self.canvas.config(width=new_width, height=new_height)

            # Resize image for saving
            new_image = Image.new("RGB", (new_width, new_height), "white")
            new_image.paste(self.image, (0, 0))
            self.image = new_image
            self.draw = ImageDraw.Draw(self.image)

            self.canvas_width = new_width
            self.canvas_height = new_height
        except ValueError:
            print("Please enter valid dimensions.")

    def set_brush_size(self):
        try:
            self.brush_size = int(self.brush_size_entry.get())
        except ValueError:
            print("Please enter a valid brush size.")

    def save_image(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png"), ("All files", "*.*")])
        if file_path:
            self.image.save(file_path)

    def load_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png;*.jpg;*.jpeg;*.bmp;*.gif"), ("All files", "*.*")])
        if file_path:
            loaded_image = Image.open(file_path)
            self.image = loaded_image.convert("RGB")
            self.canvas_width, self.canvas_height = self.image.size
            self.canvas.config(width=self.canvas_width, height=self.canvas_height)
            self.draw = ImageDraw.Draw(self.image)

            # Update entries
            self.width_entry.delete(0, tk.END)
            self.width_entry.insert(0, str(self.canvas_width))
            self.height_entry.delete(0, tk.END)
            self.height_entry.insert(0, str(self.canvas_height))

            # Display loaded image on canvas
            self.tk_image = ImageTk.PhotoImage(self.image)
            self.canvas.create_image(0, 0, anchor="nw", image=self.tk_image)

if __name__ == "__main__":
    root = tk.Tk()
    app = DrawInBox(root)
    root.mainloop()
