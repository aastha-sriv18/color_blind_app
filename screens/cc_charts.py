import os
from kivy.uix.screenmanager import Screen
from kivymd.toast import toast
from kivymd.uix.filemanager import MDFileManager
from kivy.lang import Builder
from kivy.properties import StringProperty
from PIL import Image as PILImage
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.list import OneLineListItem
from PIL import ImageEnhance

Builder.load_file('screens/cc_charts.kv')


class CCChartsScreen(Screen):
    selected_cb = StringProperty("")  # renamed for consistency with code usage
    image_path = StringProperty("")
    result_image = StringProperty("")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.manager_open = False
        self.file_manager = MDFileManager(
            exit_manager=self.exit_manager,
            select_path=self.select_path,
            preview=False,  # Set to False to avoid common crashes on some OS
        )
        self.menu = None  # initialize dropdown menu variable

    def open_file_manager(self):
        start_path = os.path.expanduser("~")
        self.file_manager.show(start_path)
        self.manager_open = True

    def select_path(self, path):
        self.exit_manager()
        self.image_path = path
        toast(f"Selected: {os.path.basename(path)}")
        try:
            self.ids.image_preview.source = path
            self.ids.status_label.text = "[color=00ff00]Image loaded successfully![/color]"
        except Exception as e:
            self.ids.status_label.text = f"[color=ff0000]Error loading image: {e}[/color]"

    def exit_manager(self, *args):
        self.manager_open = False
        self.file_manager.close()

    # Show dropdown menu for color blindness selection
    def show_cb_menu(self):
        cb_types = ["Protanopia", "Deuteranopia", "Tritanopia"]
        menu_items = []

        for cb_name in cb_types:
            menu_items.append(
                {
                    "text": cb_name,
                    "viewclass": "OneLineListItem",
                    "on_release": lambda x=cb_name: self.set_cb(x),
                }
            )

        self.menu = MDDropdownMenu(
            caller=self.ids.cb_drop_item,
            items=menu_items,
            width_mult=4,
        )
        self.menu.open()

    # Set selected color blindness from dropdown
    def set_cb(self, cb_name):
        self.selected_cb = cb_name
        self.ids.selected_cb_btn.text = f"Selected Color Blindness: {cb_name}"
        if self.menu:
            self.menu.dismiss()

    def generate_chart(self):
        """Generate color-blind–friendly version using PIL"""
        if not self.image_path or not self.selected_cb:
            self.ids.status_label.text = "[color=ff0000]Please select both chart and blindness type![/color]"
            return

        try:
            img = PILImage.open(self.image_path).convert("RGB")

            # Transformation matrices for each blindness type
            if self.selected_cb == "Protanopia":
                matrix = (
                    0.56667, 0.43333, 0, 0,     # R' = 0.566R + 0.433G + 0B + 0
                    0.55833, 0.44167, 0, 0,     # G' = 0.558R + 0.441G + 0B + 0
                    0, 0.24167, 0.75833, 0      # B' = 0R + 0.241G + 0.758B + 0
                )
            elif self.selected_cb == "Deuteranopia":
                matrix = (
                    0.625, 0.375, 0, 0,
                    0.7, 0.3, 0, 0,
                    0, 0.3, 0.7, 0
                )
            elif self.selected_cb == "Tritanopia":
                matrix = (
                    0.95, 0.05, 0, 0,
                    0, 0.43333, 0.56667, 0,
                    0, 0.475, 0.525, 0
                )

            else:
                self.ids.status_label.text = "[color=ff0000]Unknown blindness type![/color]"
                return

            # Apply color transformation
            transformed = img.convert("RGB", matrix)

            # Enhance contrast + brightness
            enhancer = ImageEnhance.Contrast(transformed)
            transformed = enhancer.enhance(1.3)
            enhancer = ImageEnhance.Brightness(transformed)
            transformed = enhancer.enhance(1.1)

            # Save output
            os.makedirs("generated", exist_ok=True)
            output_path = os.path.join("generated", f"{self.selected_cb}_chart.png")
            transformed.save(output_path)

            # Show on screen
            self.result_image = output_path
            self.ids.result_image.source = self.result_image
            self.ids.status_label.text = f"[color=00ff00]{self.selected_cb}-friendly chart generated![/color]"
            toast("Chart generated successfully!")

        except Exception as e:
            self.ids.status_label.text = f"[color=ff0000]Error: {str(e)}[/color]"

    def download_chart(self):
        """Save the generated chart image to Downloads folder."""
        if not self.result_image or not os.path.exists(self.result_image):
            toast("No generated chart to download!")
            return

        try:
            # Determine a save path
            home = os.path.expanduser("~")
            download_dir = os.path.join(home, "Downloads")
            os.makedirs(download_dir, exist_ok=True)

            filename = os.path.basename(self.result_image)
            destination = os.path.join(download_dir, filename)

            # Copy file
            with open(self.result_image, "rb") as src, open(destination, "wb") as dst:
                dst.write(src.read())

            toast(f"Chart saved to Downloads/{filename}")
            self.ids.status_label.text = f"[color=00ff00]Chart saved to Downloads/{filename}[/color]"

        except Exception as e:
            self.ids.status_label.text = f"[color=ff0000]Error saving file: {e}[/color]"
            toast("Error saving file!")
