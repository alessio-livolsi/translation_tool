# Third Party
from googletrans import Translator
import polib
from tqdm import tqdm

# Load the PO file
po_file = polib.pofile("load your file here")

# Translate each message in the PO file
translator = Translator()
for entry in tqdm(po_file, desc="Translating messages"):
    if entry.msgstr:
        # Skip messages that have already been translated
        continue
    # Translate the message using Google Translate
    # dest = language code
    # All language codes can be found here > https://py-googletrans.readthedocs.io/en/latest/#googletrans-languages
    translation = translator.translate(
        entry.msgid, dest="enter your language code here"
    ).text
    # Set the translation as the message's msgstr
    entry.msgstr = translation

# Save the translated PO file
po_file.save("enter your file name here")
print("Your file has been translated.")
