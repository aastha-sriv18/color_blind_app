from kivy.uix.screenmanager import Screen
from kivy.lang import Builder
from kivy.properties import StringProperty
from kivy.uix.filechooser import FileChooserIconView
from kivy.uix.popup import Popup
from kivy.core.window import Window
from bs4 import BeautifulSoup
import re
import html
import platform

# Check if running on Android or PC
if platform.system() == "Linux" and platform.machine().startswith("arm"):
    from android.activity import activity
    from jnius import autoclass, cast
else:
    activity = None
    autoclass = None
    cast = None

# Load KV file for this screen
Builder.load_file('screens/emails.kv')


class EmailsScreen(Screen):

    def process_html_text(self, html_text):
        """Cleans pasted email HTML using BeautifulSoup"""
        soup = BeautifulSoup(html_text, 'html.parser')
        text = soup.get_text(separator='\n')
        text = html.unescape(text)

        # Extract sender/time and highlight important parts
        senders = re.findall(r'From:\s*(.*)', text)
        times = re.findall(r'(?:Sent|On)\s.*\d{4}', text)
        keywords = ["important", "urgent", "please note", "asap"]
        imp_lines = [l for l in text.splitlines() if any(k in l.lower() for k in keywords)]

        summary = "Email Summary\n----------------\n"
        for s, t in zip(senders, times):
            summary += f"{s} ({t})\n"
        summary += "\n" + "\n".join(imp_lines)

        # Update output text on screen
        self.ids.output_text.text = summary if summary.strip() else "No important info detected."

        return summary

    def extract_text_mlkit(self, image_path):
        """Uses Google ML Kit for OCR (Android only)"""

        # Prevent crashes if running on PC
        if autoclass is None:
            self.ids.output_text.text = "ML Kit OCR works only on Android device."
            return

        InputImage = autoclass('com.google.mlkit.vision.common.InputImage')
        TextRecognition = autoclass('com.google.mlkit.vision.text.TextRecognition')
        OnSuccessListener = autoclass('com.google.android.gms.tasks.OnSuccessListener')
        OnFailureListener = autoclass('com.google.android.gms.tasks.OnFailureListener')

        image = InputImage.fromFilePath(self._get_android_context(), image_path)
        recognizer = TextRecognition.getClient()

        screen = self  # Reference to current screen

        class Success(OnSuccessListener):
            def onSuccess(_self, result):
                text = result.getText()
                screen.ids.output_text.text = text

        class Failure(OnFailureListener):
            def onFailure(_self, e):
                screen.ids.output_text.text = "OCR failed: " + str(e)

        recognizer.process(image).addOnSuccessListener(Success()).addOnFailureListener(Failure())

    def _get_android_context(self):
        """Get Android app context for ML Kit"""
        PythonActivity = autoclass('org.kivy.android.PythonActivity')
        return PythonActivity.mActivity
