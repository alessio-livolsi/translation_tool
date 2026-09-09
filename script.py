import logging
import os
import sys

import polib
from googletrans import LANGUAGES, Translator
from tqdm import tqdm

OUTPUT_DIRECTORY = "output"


logging.basicConfig(
    level=logging.DEBUG,
    filename="translation.log",
    filemode="w",
    format="%(asctime)s - %(levelname)s - %(message)s",
)


def main() -> None:
    source_filename = input(
        "Enter the PO filename, for example examples/example_messages.po: "
    ).strip()

    if not source_filename:
        print("Error: no filename was entered.")
        sys.exit(1)

    if not os.path.isfile(source_filename):
        print(f"Error: '{source_filename}' does not exist.")
        sys.exit(1)

    destination_language = (
        input("Enter the destination language code, for example fr, de, or es: ")
        .strip()
        .lower()
    )

    if destination_language not in LANGUAGES:
        print(f"Error: unknown language code '{destination_language}'.")
        print("Examples: fr, de, es, it, pt, nl")
        sys.exit(1)

    try:
        po_file = polib.pofile(source_filename)
    except (OSError, UnicodeError) as error:
        logging.exception("Unable to load PO file")
        print(f"Error: unable to load '{source_filename}': {error}")
        sys.exit(1)

    translator = Translator()

    for entry in tqdm(po_file, desc="Translating messages"):
        if not entry.msgid:
            continue

        if entry.msgstr:
            continue

        try:
            translation = translator.translate(
                entry.msgid,
                dest=destination_language,
            ).text
        except Exception as error:
            logging.error(
                "Error translating %r: %s",
                entry.msgid,
                error,
            )
            continue

        entry.msgstr = translation

    os.makedirs(OUTPUT_DIRECTORY, exist_ok=True)

    base_filename = os.path.splitext(os.path.basename(source_filename))[0]

    translated_filename = os.path.join(
        OUTPUT_DIRECTORY,
        f"{base_filename}_{destination_language}.po",
    )

    try:
        po_file.save(translated_filename)
    except OSError as error:
        logging.exception("Unable to save translated PO file")
        print(f"Error: unable to save '{translated_filename}': {error}")
        sys.exit(1)

    print(f"Your file has been translated and saved as '{translated_filename}'.")


if __name__ == "__main__":
    main()
