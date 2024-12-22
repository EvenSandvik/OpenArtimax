import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageDraw, ImageTk
import time
import random
import string

class DrawInBox:
    def __init__(self, root):
        self.root = root
        self.root.title("OpenArtimax")

        self.last_update_time = time.time()  # Track the last update time
        self.update_interval = 0.05  # Minimum interval between updates (in seconds)

        # Define canvas dimensions and other variables before creating the toolbar
        self.canvas_width = 750
        self.canvas_height = 500
        self.brush_size = 4  # Define brush size here

        # Initialize layers before creating the toolbar
        self.layers = []
        self.current_layer_index = 0

        # Main layout
        self.main_frame = tk.Frame(root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Toolbar on the left
        self.create_toolbar()

        # Canvas in the center
        self.canvas_frame = tk.Frame(self.main_frame)
        self.canvas_frame.pack(side="left", fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.canvas = tk.Canvas(self.canvas_frame, width=self.canvas_width, height=self.canvas_height, bg="white")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Bind keyboard shortcut Ctrl+S to the save_image method
        self.root.bind('<Control-s>', self.save_image_event)

        # Variables for drawing
        self.drawing = False
        self.last_x, self.last_y = None, None
        self.color = "black"
        self.erasing = False

        self.add_new_layer()  # Add the initial layer

        # Bind events
        self.canvas.bind("<ButtonPress-1>", self.start_drawing)
        self.canvas.bind("<B1-Motion>", self.draw_on_canvas)
        self.canvas.bind("<ButtonRelease-1>", self.stop_drawing)

    def create_toolbar(self):
        toolbar = tk.Frame(self.main_frame, bg="#f0f0f0", pady=5)
        toolbar.pack(side="left", fill=tk.Y)

        button_style = {
            "bg": "#222",
            "fg": "#fff",
            "font": ("Helvetica Neue", 12, "bold"),
            "relief": "flat",
            "activebackground": "#444",
            "activeforeground": "#fff",
            "highlightthickness": 0,
            "padx": 10,
            "pady": 5,
            "borderwidth": 0,
        }

        # Size controls
        tk.Label(toolbar, text="Canvas Size:", bg="#f0f0f0").pack(pady=2)
        self.width_entry = tk.Entry(toolbar, width=5)
        self.width_entry.insert(0, str(self.canvas_width))
        self.width_entry.pack(pady=2)

        self.height_entry = tk.Entry(toolbar, width=5)
        self.height_entry.insert(0, str(self.canvas_height))
        self.height_entry.pack(pady=2)

        tk.Button(toolbar, text="Resize", command=self.resize_canvas, **button_style).pack(pady=5)

        # Brush size controls
        tk.Label(toolbar, text="Brush Size:", bg="#f0f0f0").pack(pady=2)
        self.brush_size_entry = tk.Entry(toolbar, width=5)
        self.brush_size_entry.insert(0, str(self.brush_size))
        self.brush_size_entry.pack(pady=2)

        tk.Button(toolbar, text="Set", command=self.set_brush_size, **button_style).pack(pady=5)

        # Layer controls
        tk.Button(toolbar, text="Add Layer", command=self.add_new_layer, **button_style).pack(pady=5)

        # Layer display
        tk.Label(toolbar, text="Layers:", bg="#f0f0f0").pack(pady=5)
        self.layer_display_frame = tk.Frame(toolbar, bg="#f0f0f0")
        self.layer_display_frame.pack(fill=tk.BOTH, expand=True)

        self.update_layer_display()

        # Eraser toggle
        tk.Button(toolbar, text="Eraser", command=self.toggle_eraser, **button_style).pack(pady=5)

        # Load and Save buttons
        tk.Button(toolbar, text="Save", command=self.save_image, **button_style).pack(pady=5)
        tk.Button(toolbar, text="Load", command=self.load_image, **button_style).pack(pady=5)

        # Color palette
        tk.Label(toolbar, text="Colors:", bg="#f0f0f0").pack(pady=5)
        colors = ["black", "red", "blue", "green", "yellow", "purple"]
        for color in colors:
            btn = tk.Button(toolbar, bg=color, width=2, command=lambda c=color: self.change_color(c))
            btn.pack(pady=2)

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

    def draw_on_canvas(self, event):
        if self.drawing:
            x, y = event.x, event.y
            draw = ImageDraw.Draw(self.layers[self.current_layer_index])
            if self.erasing:
                draw.line([self.last_x, self.last_y, x, y], fill=(255, 255, 255, 0), width=self.brush_size)
            else:
                draw.line([self.last_x, self.last_y, x, y], fill=self.color, width=self.brush_size)
            self.last_x, self.last_y = x, y

            # Update the canvas only if sufficient time has passed
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
