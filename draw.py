import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageDraw, ImageTk, ImageFilter
import time
import random
import string

class DrawInBox:
    def __init__(self, root):
        self.root = root
        self.root.title("OpenArtimax")

        self.last_update_time = time.time()
        self.update_interval = 0.05

        self.canvas_width = 750
        self.canvas_height = 500
        self.brush_size = 4

        self.layers = []
        self.current_layer_index = 0
        self.brush_image = None
        self.opacity = 255

        # Main layout with a modern look
        self.main_frame = tk.Frame(root, bg="white")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        self.create_toolbar()

        # Layer display frame
        self.layer_display_frame = tk.Frame(self.main_frame, bg="white", padx=10, pady=10)
        self.layer_display_frame.pack(side="right", fill=tk.Y)

        # Canvas with a shadow effect
        self.canvas_frame = tk.Canvas(self.main_frame, bg="white", highlightthickness=0)
        self.canvas_frame.pack(side="left", fill=tk.BOTH, expand=True, padx=15, pady=15)
        self.canvas_shadow = tk.Frame(self.canvas_frame, bg="#ddd")
        self.canvas_shadow.place(relx=0.02, rely=0.02, relwidth=0.96, relheight=0.96)
        self.canvas = tk.Canvas(self.canvas_shadow, width=self.canvas_width, height=self.canvas_height, bg="white", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.root.bind('<Control-s>', self.save_image_event)

        self.drawing = False
        self.last_x, self.last_y = None, None
        self.color = "black"
        self.erasing = False

        self.add_new_layer()

        self.canvas.bind("<ButtonPress-1>", self.start_drawing)
        self.canvas.bind("<B1-Motion>", self.draw_on_canvas)
        self.canvas.bind("<ButtonRelease-1>", self.stop_drawing)

    def create_toolbar(self):
        toolbar = tk.Frame(self.main_frame, bg="white", padx=10, pady=10)
        toolbar.pack(side="left", fill=tk.Y)

        button_style = {
            "bg": "#007BFF",
            "fg": "#fff",
            "font": ("Helvetica Neue", 10, "bold"),
            "relief": "flat",
            "activebackground": "#0056b3",
            "activeforeground": "#fff",
            "padx": 8,
            "pady": 5,
        }

        label_style = {"bg": "white", "font": ("Helvetica Neue", 10), "anchor": "w"}

        tk.Label(toolbar, text="Canvas Size", **label_style).pack(pady=5, anchor="w")
        self.width_entry = tk.Entry(toolbar, width=5)
        self.width_entry.insert(0, str(self.canvas_width))
        self.width_entry.pack(pady=2)

        self.height_entry = tk.Entry(toolbar, width=5)
        self.height_entry.insert(0, str(self.canvas_height))
        self.height_entry.pack(pady=2)

        tk.Button(toolbar, text="Resize", command=self.resize_canvas, **button_style).pack(pady=5)

        tk.Label(toolbar, text="Brush Size", **label_style).pack(pady=5, anchor="w")
        self.brush_size_entry = tk.Entry(toolbar, width=5)
        self.brush_size_entry.insert(0, str(self.brush_size))
        self.brush_size_entry.pack(pady=2)

        tk.Button(toolbar, text="Set", command=self.set_brush_size, **button_style).pack(pady=5)

        tk.Label(toolbar, text="Opacity (0-255)", **label_style).pack(pady=5, anchor="w")
        self.opacity_entry = tk.Entry(toolbar, width=5)
        self.opacity_entry.insert(0, str(self.opacity))
        self.opacity_entry.pack(pady=2)

        tk.Button(toolbar, text="Set Opacity", command=self.set_opacity, **button_style).pack(pady=5)

        tk.Button(toolbar, text="Add Layer", command=self.add_new_layer, **button_style).pack(pady=5)

        tk.Label(toolbar, text="Brush", **label_style).pack(pady=5, anchor="w")
        tk.Button(toolbar, text="Load Brush", command=self.load_brush, **button_style).pack(pady=5)

        tk.Button(toolbar, text="Eraser", command=self.toggle_eraser, **button_style).pack(pady=5)
        tk.Button(toolbar, text="Save", command=self.save_image, **button_style).pack(pady=5)
        tk.Button(toolbar, text="Load", command=self.load_image, **button_style).pack(pady=5)

        tk.Label(toolbar, text="Colors", **label_style).pack(pady=5, anchor="w")
        colors = ["black", "red", "blue", "green", "yellow", "purple"]
        for color in colors:
            btn = tk.Button(toolbar, bg=color, width=2, command=lambda c=color: self.change_color(c), relief="flat", bd=0)
            btn.pack(pady=2, ipadx=10, ipady=2, anchor="w")

    def add_new_layer(self):
        new_layer = Image.new("RGBA", (self.canvas_width, self.canvas_height), (255, 255, 255, 0))
        self.layers.append(new_layer)
        self.current_layer_index = len(self.layers) - 1
        self.update_layer_display()
        self.update_canvas()


    def update_layer_display(self):
        # Clear existing layer buttons
        for widget in self.layer_display_frame.winfo_children():
            widget.destroy()

        # Add a button for each layer
        for index, layer in enumerate(self.layers):
            text = f"Layer {index + 1}"
            btn = tk.Button(self.layer_display_frame, text=text, command=lambda i=index: self.switch_layer(i))
            if index == self.current_layer_index:
                btn.config(bg="blue", fg="white")
            else:
                btn.config(bg="white", fg="black")
            btn.pack(pady=2, fill=tk.X)

    def switch_layer(self, index):
        self.current_layer_index = index
        self.update_layer_display()
        self.update_canvas()

    def next_layer(self):
        if self.current_layer_index < len(self.layers) - 1:
            self.current_layer_index += 1

    def previous_layer(self):
        if self.current_layer_index > 0:
            self.current_layer_index -= 1

    def update_canvas(self):
        # Clear the canvas
        self.canvas.delete("all")
        
        # Combine layers into a single image
        combined_image = Image.new("RGBA", (self.canvas_width, self.canvas_height))
        for layer in self.layers:
            combined_image = Image.alpha_composite(combined_image, layer)
        
        # Update the canvas with the new image
        self.tk_image = ImageTk.PhotoImage(combined_image)
        self.canvas.create_image(0, 0, anchor="nw", image=self.tk_image)

    def change_color(self, new_color):
        self.color = new_color
        self.erasing = False

    def toggle_eraser(self):
        self.erasing = not self.erasing

    def start_drawing(self, event):
        self.drawing = True
        self.last_x, self.last_y = event.x, event.y

    def set_opacity(self):
        try:
            self.opacity = int(self.opacity_entry.get())
        except ValueError:
            print("Please enter a valid opacity value.")

    def load_brush(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png;*.jpg;*.jpeg;*.bmp;*.gif"), ("All files", "*.*")])
        if file_path:
            brush_image = Image.open(file_path).convert("RGBA")
            self.brush_image = brush_image

    def draw_on_canvas(self, event):
        if self.drawing:
            x, y = event.x, event.y
            draw = ImageDraw.Draw(self.layers[self.current_layer_index])

            if self.brush_image:
                brush = self.brush_image.resize((self.brush_size, self.brush_size)).copy()
                alpha = brush.split()[3].point(lambda p: p * (self.opacity / 255))
                brush.putalpha(alpha)
                self.layers[self.current_layer_index].paste(brush, (x - self.brush_size // 2, y - self.brush_size // 2), brush)
            else:
                color = (*self.root.winfo_rgb(self.color)[:3], self.opacity)
                draw.line([self.last_x, self.last_y, x, y], fill=color, width=self.brush_size)
            
            self.last_x, self.last_y = x, y
            current_time = time.time()
            if current_time - self.last_update_time >= self.update_interval:
                self.update_canvas()
                self.last_update_time = current_time

    def stop_drawing(self, event):
        self.drawing = False
        self.last_x, self.last_y = None, None

    def resize_canvas(self):
        try:
            new_width = int(self.width_entry.get())
            new_height = int(self.height_entry.get())

            # Resize all layers
            resized_layers = []
            for layer in self.layers:
                resized_layer = layer.resize((new_width, new_height))
                resized_layers.append(resized_layer)
            self.layers = resized_layers

            self.canvas.config(width=new_width, height=new_height)

            self.canvas_width = new_width
            self.canvas_height = new_height

            self.update_canvas()
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
            combined_image = Image.new("RGBA", (self.canvas_width, self.canvas_height))
            for layer in self.layers:
                combined_image = Image.alpha_composite(combined_image, layer)
            combined_image.convert("RGB").save(file_path)

    def load_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png;*.jpg;*.jpeg;*.bmp;*.gif"), ("All files", "*.*")])
        if file_path:
            loaded_image = Image.open(file_path).convert("RGBA")
            self.canvas_width, self.canvas_height = loaded_image.size
            self.canvas.config(width=self.canvas_width, height=self.canvas_height)

            self.layers = [loaded_image]
            self.current_layer_index = 0

            # Update entries
            self.width_entry.delete(0, tk.END)
            self.width_entry.insert(0, str(self.canvas_width))
            self.height_entry.delete(0, tk.END)
            self.height_entry.insert(0, str(self.canvas_height))

            self.update_canvas()

    def generate_random_name(self, length=10):
        """Generate a random string for the filename."""
        return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

    def save_image_event(self, event):
        # Generate a random name for the image
        random_name = self.generate_random_name() + ".png"
        
        file_path = filedialog.asksaveasfilename(defaultextension=".png", initialfile=random_name,
                                                filetypes=[("PNG files", "*.png"), ("All files", "*.*")])
        if file_path:
            combined_image = Image.new("RGBA", (self.canvas_width, self.canvas_height))
            for layer in self.layers:
                combined_image = Image.alpha_composite(combined_image, layer)
            combined_image.convert("RGB").save(file_path)


if __name__ == "__main__":
    root = tk.Tk()
    app = DrawInBox(root)
    root.mainloop()
