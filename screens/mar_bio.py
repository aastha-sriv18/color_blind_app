import os
from kivy.lang import Builder
from kivy.uix.screenmanager import Screen
from kivy.properties import StringProperty
from kivymd.uix.filemanager import MDFileManager
from kivymd.toast import toast
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.list import OneLineListItem, MDList
from PIL import Image as PILImage
from math import sqrt

Builder.load_file('screens/mar_bio.kv')

class MarBioScreen(Screen):
    image_path = StringProperty("")
    selected_test = StringProperty("None")
    color_info = StringProperty("")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.manager_open = False
        self.file_manager = MDFileManager(
            exit_manager=self.exit_manager,
            select_path=self.select_path,
            preview=True
        )

    # Open file manager
    def open_file_manager(self):
        start_path = os.path.expanduser("~")
        self.file_manager.show(start_path)
        self.manager_open = True

    # Close file manager
    def exit_manager(self, *args):
        self.manager_open = False
        self.file_manager.close()

    # When a file is selected
    def select_path(self, path):
        self.exit_manager()
        self.image_path = path
        toast(f"Selected: {path}")

    # Show test selection dialog
    def show_test_menu(self):
        tests = ["pH Test", "Nitrate Test", "Phosphate Test", "Chlorophyll Test", "Ammonia Test"]
        menu_items = []
        for test in tests:
            menu_items.append(
                {
                    "text": test,
                    "viewclass": "OneLineListItem",
                    "on_release": lambda x=test: self.set_test(x),
                }
            )

        self.menu = MDDropdownMenu(
            caller=self.ids.test_drop_item,
            items=menu_items,
            width_mult=4,
        )
        self.menu.open()

    # Set selected test
    def set_test(self, test_name):
        self.selected_test = test_name
        self.ids.selected_test_btn.text = f"Selected Test: {test_name}"
        self.menu.dismiss()

    # Button function: Generate analysis
    def generate_analysis(self):
        if not self.image_path:
            toast("Please upload an image first!")
            return
        if self.selected_test == "None":
            toast("Please select a test first!")
            return
        if self.selected_test == "pH Test":
            result = self.process_ph_test(self.image_path)
        elif self.selected_test == "Nitrate Test":
            result = self.process_nitrate_test(self.image_path)
        elif self.selected_test == "Phosphate Test":
            result = self.process_phosphate_test(self.image_path)
        elif self.selected_test == "Chlorophyll Test":
            result = self.process_chlorophyll_test(self.image_path)
        elif self.selected_test == "Ammonia Test":
            result = self.process_ammonia_test(self.image_path)
        else:
            result = f"Analysis for {self.selected_test} not implemented yet."


        # Call your processing function here
        #result = self.process_image(self.image_path, self.selected_test)
        self.color_info = result  # Update the label


    BASIC_COLORS = {
    "Red": (255, 0, 0),
    "Orange": (255, 128, 0),
    "Yellow": (255, 255, 0),
    "Lime Green": (128, 255, 0),
    "Green": (0, 255, 0),
    "Cyan": (0, 255, 255),
    "Sky Blue": (135, 206, 235),
    "Blue": (0, 0, 255),
    "Navy Blue": (0, 0, 128),
    "Violet": (128, 0, 255),
    "Magenta": (255, 0, 255),
    "Pink": (255, 182, 193),
    "Brown": (139, 69, 19),
    "Gray": (128, 128, 128),
    "Black": (0, 0, 0),
    "White": (255, 255, 255)
    }


    # PH Test logic
    PH_COLORS = {
        1: (255, 0, 0),
        2: (255, 64, 64),
        3: (255, 128, 64),
        4: (255, 255, 0),
        5: (192, 255, 0),
        6: (128, 255, 0),
        7: (0, 255, 0),
        8: (0, 255, 128),
        9: (0, 255, 255),
        10: (0, 128, 255),
        11: (0, 0, 255),
        12: (128, 0, 255),
        13: (192, 0, 255),
        14: (255, 0, 255),
    }

    PH_DESCRIPTIONS = {
    1: "Extremely acidic water – dangerous for aquatic life.",
    2: "Very acidic – can harm sensitive marine organisms.",
    3: "Strongly acidic – caution advised.",
    4: "Moderately acidic – may affect fish and plants.",
    5: "Slightly acidic – generally safe but not optimal.",
    6: "Mildly acidic – good for most marine life.",
    7: "Neutral – ideal pH for aquatic environments.",
    8: "Slightly basic – suitable for most marine organisms.",
    9: "Moderately basic – some species may be stressed.",
    10: "Strongly basic – caution advised for sensitive species.",
    11: "Very basic – may harm aquatic life.",
    12: "Extremely basic – dangerous for marine life.",
    13: "Highly alkaline – unsafe for most species.",
    14: "Extremely alkaline – water quality critical.",
    }

    NITRATE_COLORS = {
    0: (255, 255, 255),
    10: (200, 255, 200),
    20: (150, 255, 150),
    40: (0, 255, 0),
    60: (0, 200, 0),
    80: (0, 150, 0),
    100: (0, 100, 0),
    }

    NITRATE_DESCRIPTIONS = {
    0: "No detectable nitrate. Safe for marine life.",
    10: "Low nitrate level. Water quality is good.",
    20: "Moderate nitrate. Monitor for accumulation.",
    40: "High nitrate. Can stress aquatic organisms.",
    60: "Very high nitrate. Risk of algae growth.",
    80: "Dangerously high nitrate. Immediate action needed.",
    100: "Extremely high nitrate. Unsafe for marine life.",
    }

    PHOSPHATE_COLORS = {
    0.0: (230, 255, 255),
    0.1: (180, 240, 255),
    0.2: (130, 210, 255),
    0.5: (80, 180, 255),
    1.0: (30, 150, 255),
    2.0: (0, 100, 200),
    5.0: (0, 60, 150),
    }

    PHOSPHATE_DESCRIPTIONS = {
    0.0: "No detectable phosphate — excellent water quality.",
    0.1: "Very low phosphate — safe for most marine environments.",
    0.2: "Low phosphate — good, minimal risk of algal growth.",
    0.5: "Moderate phosphate — may begin to support algae.",
    1.0: "High phosphate — can cause algae blooms.",
    2.0: "Very high phosphate — strong risk of eutrophication.",
    5.0: "Extremely high phosphate — critical condition for marine life.",
    }

    CHLOROPHYLL_COLORS = {
    0: (250, 255, 210),
    5: (190, 255, 120),
    10: (120, 255, 120),
    20: (0, 255, 0),
    40: (0, 180, 0),
    60: (0, 120, 0),
    100: (0, 80, 0),
    }

    CHLOROPHYLL_DESCRIPTIONS = {
    0: "No chlorophyll detected – very low biological activity.",
    5: "Low chlorophyll – healthy oligotrophic (clean) water.",
    10: "Moderate chlorophyll – normal biological productivity.",
    20: "High chlorophyll – likely algal presence.",
    40: "Very high chlorophyll – possible eutrophication starting.",
    60: "Dense algal bloom likely – reduced water clarity.",
    100: "Extremely high chlorophyll – heavy algal bloom, low oxygen levels.",
    }

    AMMONIA_COLORS = {
    0: (255, 255, 150),
    0.25: (210, 255, 100),
    0.5: (150, 255, 120),
    1.0: (0, 255, 0),
    2.0: (0, 200, 200),
    4.0: (100, 220, 255),
    8.0: (0, 0, 255),
    }

    AMMONIA_DESCRIPTIONS = {
    0: "No ammonia detected – excellent water quality.",
    0.25: "Very low ammonia – safe for marine organisms.",
    0.5: "Low ammonia – still acceptable for most aquatic life.",
    1.0: "Moderate ammonia – may stress sensitive species.",
    2.0: "High ammonia – potentially harmful, monitor closely.",
    4.0: "Very high ammonia – toxic to most marine animals.",
    8.0: "Extremely high ammonia – critical danger, immediate action needed.",
    }






    def get_dominant_color(self, image_path):
        img = PILImage.open(image_path).convert("RGB")
        img = img.resize((50, 50))
        colors = img.getcolors(50*50)
        colors.sort(key=lambda x: x[0], reverse=True)
        return colors[0][1]

    def get_closest_color_name(self, r, g, b):
        """Return the closest color name to a given RGB value."""
        min_dist = float('inf')
        closest_name = "Unknown"
        for name, (cr, cg, cb) in self.BASIC_COLORS.items():
            dist = ((r - cr)**2 + (g - cg)**2 + (b - cb)**2) ** 0.5
            if dist < min_dist:
                min_dist = dist
                closest_name = name
        return closest_name



    def match_ph_color(self, rgb):
        r1, g1, b1 = rgb
        min_dist = float('inf')
        closest_ph = None
        for ph, (r2, g2, b2) in self.PH_COLORS.items():
            dist = sqrt((r1-r2)**2 + (g1-g2)**2 + (b1-b2)**2)
            if dist < min_dist:
                min_dist = dist
                closest_ph = ph
        return closest_ph

    def process_ph_test(self, image_path):
        dominant_color = self.get_dominant_color(image_path)
        ph_value = self.match_ph_color(dominant_color)
        description = self.PH_DESCRIPTIONS.get(ph_value, "No description available.")
        r, g, b = dominant_color
        color_name = self.get_closest_color_name(r, g, b)
        return f"Detected pH: {ph_value}\nDominant Color: {color_name} (RGB: {r}, {g} ,{b})\nAnalysis: {description}"

    def match_nitrate_color(self, rgb):
        r1, g1, b1 = rgb
        min_dist = float('inf')
        closest_value = None
        for value, (r2, g2, b2) in self.NITRATE_COLORS.items():
            dist = sqrt((r1 - r2)**2 + (g1 - g2)**2 + (b1 - b2)**2)
            if dist < min_dist:
                min_dist = dist
                closest_value = value
        return closest_value

    def process_nitrate_test(self, image_path):
        dominant_color = self.get_dominant_color(image_path)
        nitrate_value = self.match_nitrate_color(dominant_color)
        description = self.NITRATE_DESCRIPTIONS.get(nitrate_value, "No description available.")
        r, g, b = dominant_color
        color_name = self.get_closest_color_name(r, g, b)
        return f"Nitrate Level: {nitrate_value} ppm\nDominant Color: (RGB: {r},{g},{b})\nAnalysis: {description}"

    def match_phosphate_color(self, rgb):
        r1, g1, b1 = rgb
        min_dist = float('inf')
        closest_value = None
        for value, (r2, g2, b2) in self.PHOSPHATE_COLORS.items():
            dist = sqrt((r1 - r2)**2 + (g1 - g2)**2 + (b1 - b2)**2)
            if dist < min_dist:
                min_dist = dist
                closest_value = value
        return closest_value

    def process_phosphate_test(self, image_path):
        dominant_color = self.get_dominant_color(image_path)
        phosphate_value = self.match_phosphate_color(dominant_color)
        description = self.PHOSPHATE_DESCRIPTIONS.get(phosphate_value, "No description available.")
        r, g, b = dominant_color
        color_name = self.get_closest_color_name(r, g, b)
        return f"Phosphate Level: {phosphate_value} ppm\nDominant Color: {color_name} (RGB: {r},{g},{b})\n Analysis: {description}"

    def match_chlorophyll_color(self, rgb):
        r1, g1, b1 = rgb
        min_dist = float('inf')
        closest_value = None
        for value, (r2, g2, b2) in self.CHLOROPHYLL_COLORS.items():
            dist = sqrt((r1 - r2)**2 + (g1 - g2)**2 + (b1 - b2)**2)
            if dist < min_dist:
                min_dist = dist
                closest_value = value
        return closest_value
    
    def process_chlorophyll_test(self, image_path):
        dominant_color = self.get_dominant_color(image_path)
        chlorophyll_value = self.match_chlorophyll_color(dominant_color)
        description = self.CHLOROPHYLL_DESCRIPTIONS.get(chlorophyll_value, "No description available.")
        r, g, b = dominant_color
        color_name = self.get_closest_color_name(r, g, b)
        return (f"Chlorophyll Level: {chlorophyll_value} µg/L\n"
                f"Dominant Color: {color_name} (RGB: {r}, {g}, {b})\n"
                f"Analysis: {description}")

    def match_ammonia_color(self, rgb):
        r1, g1, b1 = rgb
        min_dist = float('inf')
        closest_value = None
        for value, (r2, g2, b2) in self.AMMONIA_COLORS.items():
            dist = sqrt((r1 - r2)**2 + (g1 - g2)**2 + (b1 - b2)**2)
            if dist < min_dist:
                min_dist = dist
                closest_value = value
        return closest_value

    def process_ammonia_test(self, image_path):
        dominant_color = self.get_dominant_color(image_path)
        ammonia_value = self.match_ammonia_color(dominant_color)
        description = self.AMMONIA_DESCRIPTIONS.get(ammonia_value, "No description available.")
        r, g, b = dominant_color
        color_name = self.get_closest_color_name(r, g, b)
        return (f"Ammonia Level: {ammonia_value} ppm\n"
                f"Dominant Color: {color_name} (RGB: {r}, {g}, {b})\n"
                f"Analysis: {description}")
