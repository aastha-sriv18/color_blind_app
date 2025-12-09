import os
from kivy.uix.screenmanager import Screen
from kivy.lang import Builder

from kivy.properties import StringProperty
from kivy.uix.image import Image
from kivymd.uix.filemanager import MDFileManager
from kivymd.toast import toast
from kivy.core.image import Image as CoreImage
from PIL import Image as PILImage
from kivy.uix.filechooser import FileChooserIconView
import io

Builder.load_file('screens/what_color.kv')

class WhatColorScreen(Screen):
    image_path = StringProperty("")
    color_info = StringProperty("")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Setup file manager
        self.manager_open = False
        self.file_manager = MDFileManager(
            exit_manager=self.exit_manager,
            select_path=self.select_path,
            preview=True  # only for images
        )

    # Open the file manager
    def open_file_manager(self):
        start_path = os.path.expanduser("~")  # Home directory
        self.file_manager.show(start_path)
        self.manager_open = True

    # When a file is selected
    def select_path(self, path):
        self.exit_manager()
        self.image_path = path
        toast(f"Selected: {path}")
        self.process_image(path)

    # When user closes the file manager
    def exit_manager(self, *args):
        self.manager_open = False
        self.file_manager.close()

    # Process the image and extract dominant color
    def process_image(self, path):
        try:
            img = PILImage.open(path).convert("RGB")
            img = img.resize((50, 50))
            pixels = list(img.getdata())
            r = sum([p[0] for p in pixels]) // len(pixels)
            g = sum([p[1] for p in pixels]) // len(pixels)
            b = sum([p[2] for p in pixels]) // len(pixels)
            hex_color = f'#{r:02x}{g:02x}{b:02x}'
            color_name = self.get_color_name(r, g, b)
            self.color_info = f"Dominant Color: {color_name} ({hex_color.upper()})"
        except Exception as e:
            self.color_info = f"Error: {e}"
    
    def get_color_name(self, r, g, b):
        """Find the closest color name based on Euclidean distance in RGB space."""

        # Define basic color dictionary (you can expand it)
        colors = {
            "Red": (255, 0, 0),
            "Dark Red": (139, 0, 0),
            "Orange": (255, 165, 0),
            "Yellow": (255, 255, 0),
            "Green": (0, 255, 0),
            "Dark Green": (0, 100, 0),
            "Cyan": (0, 255, 255),
            "Blue": (0, 0, 255),
            "Light Blue": (173, 216, 230),
            "Navy Blue": (0, 0, 128),
            "Purple": (128, 0, 128),
            "Pink": (255, 192, 203),
            "Magenta": (255, 0, 255),
            "Brown": (165, 42, 42),
            "Gray": (128, 128, 128),
            "Light Gray": (211, 211, 211),
            "White": (255, 255, 255),
            "Black": (0, 0, 0),
            "Olive": (128, 128, 0),
            "Teal": (0, 128, 128),
        }

        # Function to calculate Euclidean distance
        def distance(c1, c2):
            return ((c1[0]-c2[0])**2 + (c1[1]-c2[1])**2 + (c1[2]-c2[2])**2) ** 0.5

        # Find the color with minimum distance
        min_diff = float("inf")
        closest_color = "Unknown"

        for name, value in colors.items():
            d = distance((r, g, b), value)
            if d < min_diff:
                min_diff = d
                closest_color = name

        return closest_color


