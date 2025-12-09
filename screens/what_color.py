import os
import webbrowser
from kivy.properties import StringProperty
from kivy.uix.image import Image
from kivy.graphics import Color, Rectangle
from kivymd.uix.screen import MDScreen
from kivymd.uix.filemanager import MDFileManager
from kivymd.toast import toast
from PIL import Image as PILImage


class TappableImage(Image):
    overlay_rect = None

    def on_touch_down(self, touch):
        # To only accept touch input in the widget area
        if not self.collide_point(*touch.pos):
            return super().on_touch_down(touch)

        if not self.texture:
            return True

        x, y = touch.pos
        lx = x - self.x
        ly = y - self.y

        box_w, box_h = self.width, self.height
        tex_w, tex_h = self.texture.width, self.texture.height

        if self.keep_ratio:
            scale = min(box_w / tex_w, box_h / tex_h)
            img_w = tex_w * scale
            img_h = tex_h * scale
            ox = (box_w - img_w) / 2.0 
            oy = (box_h - img_h) / 2.0  
        else:
            img_w, img_h = box_w, box_h
            ox, oy = 0, 0

        if not (ox <= lx <= ox + img_w and oy <= ly <= oy + img_h):
            return True

        # calculation stuff down here
        touch_x_relative_to_img = lx - ox
        touch_y_relative_to_img = ly - oy

        nx = touch_x_relative_to_img / float(img_w)
        ny = touch_y_relative_to_img / float(img_h)

        px = int(nx * tex_w)
        py = int(ny * tex_h) # Kivy Y-origin (bottom)

        parent = self.parent
        while parent:
            if hasattr(parent, "process_image_at"):
                parent.process_image_at(px, py)
                break
            parent = parent.parent

        radius = 3
        
        center_x_local = ox + touch_x_relative_to_img
        center_y_local = oy + touch_y_relative_to_img
        

        overlay_x = self.x + center_x_local - radius
        overlay_y = self.y + center_y_local - radius

        if self.overlay_rect is None:
            with self.canvas.after:
                Color(1, 0, 0, 0.8)
                self.overlay_rect = Rectangle(pos=(overlay_x, overlay_y),
                                              size=(radius*2, radius*2))
        else:
            self.overlay_rect.pos = (overlay_x, overlay_y)
            self.overlay_rect.size = (radius*2, radius*2)

        return True


class WhatColorScreen(MDScreen):
    image_path = StringProperty("")
    color_info = StringProperty("Select an image to start")
    color_url = StringProperty("")
    pil_image = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.manager_open = False
        self.file_manager = MDFileManager(
            exit_manager=self.exit_manager,
            select_path=self.select_path,
            preview=False, # Set to False to avoid common crashes on some OS
        )

    def open_file_manager(self):
        start_path = os.path.expanduser("~")
        self.file_manager.show(start_path)
        self.manager_open = True

    def select_path(self, path):
        self.exit_manager()
        self.image_path = path
        toast(f"Selected: {os.path.basename(path)}")
        try:
            self.pil_image = PILImage.open(path).convert("RGB")
            self.color_info = "Tap the image to identify color"
        except Exception as e:
            self.color_info = f"Error loading image: {e}"

    def exit_manager(self, *args):
        self.manager_open = False
        self.file_manager.close()

    def process_image_at(self, px, py, radius=3):
        if self.pil_image is None:
            self.color_info = "No image loaded."
            self.color_url = ""
            return

        img = self.pil_image
        w, h = img.size

        # Fixed to invert Y to get the correct pixel DO NOT TOUCH
        pil_y = h - 1 - py

        pil_y = max(0, min(pil_y, h - 1))
        px = max(0, min(px, w - 1))

        try:
            r, g, b = img.getpixel((px, pil_y))
            hex_color = f'{r:02x}{g:02x}{b:02x}'
            color_name = self.get_color_name(r, g, b)
            self.color_info = f"Color: {color_name}\nRGB: {r},{g},{b}"
            self.color_url = f'https://www.colorhexa.com/{hex_color}'
        except Exception as e:
            self.color_info = f"Error reading pixel: {e}"
            self.color_url = ""

    def open_color_url(self):
        if self.color_url:
            webbrowser.open(self.color_url)

    def get_color_name(self, r, g, b):

        colors = {
            # --- Reds & Pinks ---
            "Red": (255, 0, 0), "Dark Red": (139, 0, 0), "Crimson": (220, 20, 60),
            "Firebrick": (178, 34, 34), "Salmon": (250, 128, 114), "Light Salmon": (255, 160, 122),
            "Coral": (255, 127, 80), "Tomato": (255, 99, 71), "Pink": (255, 192, 203),
            "Light Pink": (255, 182, 193), "Hot Pink": (255, 105, 180), "Deep Pink": (255, 20, 147),
            "Medium Violet Red": (199, 21, 133), "Pale Violet Red": (219, 112, 147),

            # --- Oranges & Yellows ---
            "Orange": (255, 165, 0), "Dark Orange": (255, 140, 0), "Orange Red": (255, 69, 0),
            "Gold": (255, 215, 0), "Yellow": (255, 255, 0), "Light Yellow": (255, 255, 224),
            "Lemon Chiffon": (255, 250, 205), "Papaya Whip": (255, 239, 213), "Moccasin": (255, 228, 181),
            "Peach Puff": (255, 218, 185),

            # --- Browns, Tans & Beiges ---
            "Cornsilk": (255, 248, 220), "Blanched Almond": (255, 235, 205), "Bisque": (255, 228, 196),
            "Navajo White": (255, 222, 173), "Wheat": (245, 222, 179), "Burlywood": (222, 184, 135),
            "Tan": (210, 180, 140), "Rosy Brown": (188, 143, 143), "Sandy Brown": (244, 164, 96),
            "Goldenrod": (218, 165, 32), "Dark Goldenrod": (184, 134, 11), "Peru": (205, 133, 63),
            "Chocolate": (210, 105, 30), "Saddle Brown": (139, 69, 19), "Sienna": (160, 82, 45),
            "Brown": (165, 42, 42), "Maroon": (128, 0, 0), "Beige": (245, 245, 220),
            "Antique White": (250, 235, 215),

            # --- Greens, Cyans & Blues ---
            "Green": (0, 128, 0), "Dark Green": (0, 100, 0), "Pale Green": (152, 251, 152),
            "Light Green": (144, 238, 144), "Forest Green": (34, 139, 34), "Lime": (0, 255, 0),
            "Lime Green": (50, 205, 50), "Olive": (128, 128, 0), "Dark Olive Green": (85, 107, 47),
            "Olive Drab": (107, 142, 35), "Sea Green": (46, 139, 87), "Medium Sea Green": (60, 179, 113),
            "Spring Green": (0, 255, 127), "Teal": (0, 128, 128), "Aqua": (0, 255, 255),
            "Cyan": (0, 255, 255), "Light Cyan": (224, 255, 255), "Pale Turquoise": (175, 238, 238),
            "Aquamarine": (127, 255, 212), "Turquoise": (64, 224, 208), "Medium Turquoise": (72, 209, 204),
            "Dark Turquoise": (0, 206, 209), "Cadet Blue": (95, 158, 160), "Steel Blue": (70, 130, 180),
            "Light Steel Blue": (176, 196, 222), "Powder Blue": (176, 224, 230), "Light Blue": (173, 216, 230),
            "Sky Blue": (135, 206, 235), "Light Sky Blue": (135, 206, 250), "Deep Sky Blue": (0, 191, 255),
            "Dodger Blue": (30, 144, 255), "Cornflower Blue": (100, 149, 237), "Royal Blue": (65, 105, 225),
            "Blue": (0, 0, 255), "Medium Blue": (0, 0, 205), "Dark Blue": (0, 0, 139), "Navy": (0, 0, 128),
            "Midnight Blue": (25, 25, 112),

            # --- Purples ---
            "Lavender": (230, 230, 250), "Thistle": (216, 191, 216), "Plum": (221, 160, 221),
            "Violet": (238, 130, 238), "Orchid": (218, 112, 214), "Fuchsia": (255, 0, 255),
            "Magenta": (255, 0, 255), "Medium Orchid": (186, 85, 211), "Medium Purple": (147, 112, 219),
            "Blue Violet": (138, 43, 226), "Dark Violet": (148, 0, 211), "Dark Orchid": (153, 50, 204),
            "Dark Magenta": (139, 0, 139), "Purple": (128, 0, 128), "Indigo": (75, 0, 130),
            "Slate Blue": (106, 90, 205), "Dark Slate Blue": (72, 61, 139),

            # --- Greys & Whites ---
            "White": (255, 255, 255), "Snow": (255, 250, 250), "Honeydew": (240, 255, 240),
            "Mint Cream": (245, 255, 250), "Azure": (240, 255, 255), "Alice Blue": (240, 248, 255),
            "Ghost White": (248, 248, 255), "White Smoke": (245, 245, 245), "Seashell": (255, 245, 238),
            "Old Lace": (253, 245, 230), "Floral White": (255, 250, 240), "Ivory": (255, 255, 240),
            "Gainsboro": (220, 220, 220), "Light Gray": (211, 211, 211), "Silver": (192, 192, 192),
            "Dark Gray": (169, 169, 169), "Gray": (128, 128, 128), "Dim Gray": (105, 105, 105),
            "Light Slate Gray": (119, 136, 153), "Slate Gray": (112, 128, 144), "Dark Slate Gray": (47, 79, 79),
            "Black": (0, 0, 0),
        }

        from colorsys import rgb_to_hls

        H_WEIGHT = 10.0
        L_WEIGHT = 2.0
        S_WEIGHT = 1.0

        # Normalize input RGB (0-255) to (0-1) and convert to HLS
        h_in, l_in, s_in = rgb_to_hls(r / 255.0, g / 255.0, b / 255.0)

        min_diff = float("inf")
        closest_color = "Unknown"

        for name, value in colors.items():
            r_target, g_target, b_target = value

            # Convert target color to HLS
            h_target, l_target, s_target = rgb_to_hls(r_target / 255.0, g_target / 255.0, b_target / 255.0)

            hue_diff = abs(h_in - h_target)
            hue_diff = min(hue_diff, 1.0 - hue_diff)

            d_squared = (H_WEIGHT * hue_diff)**2 + \
                        (L_WEIGHT * (l_in - l_target))**2 + \
                        (S_WEIGHT * (s_in - s_target))**2

            d = d_squared ** 0.5
            
            if d < min_diff:
                min_diff = d
                closest_color = name
                
        return closest_color