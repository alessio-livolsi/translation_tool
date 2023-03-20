# Python
import os
import logging

# Third Party
from googletrans import Translator
import polib
from tqdm import tqdm

# Set up logging to a file
logging.basicConfig(
    level=logging.DEBUG,
    filename="translation.log",
    filemode="w",
    format="%(asctime)s - %(levelname)s - %(message)s",
)

# Load the PO file
po_file = polib.pofile("django.po")

# Translate each message in the PO file
translator = Translator()
for entry in tqdm(po_file, desc="Translating messages"):
    if entry.msgstr:
        # Skip messages that have already been translated
        continue
    # Translate the message using Google Translate
    # dest = language code
    # All language codes can be found here > https://py-googletrans.readthedocs.io/en/latest/#googletrans-languages
    try:
        translation = translator.translate(entry.msgid, dest="es").text
    except Exception as e:
        logging.error(f"Error translating '{entry.msgid}': {e}")
        continue
    # Set the translation as the message's msgstr
    entry.msgstr = translation

# Save the translated PO file with a new filename
base_filename = os.path.splitext("django.po")[0]
translated_filename = f"{base_filename}_es.po"
po_file.save(translated_filename)
print(f"Your file has been translated and saved as {translated_filename}.")
