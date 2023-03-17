# Translation Tool

## Overview
A simple script script that loads a PO file that iterates over each message and then translates the message using Google Translate API. 
The script uses the googletrans library and outputs translated text which, is then set as the message's msgstr attribute.

## Get Started
- Download or clone the repo
- Set up a virtual environment and `pip install -r requirements.txt`
- Drag the desired load file into the project
- Enter the language via the dest argument 
- A link to all the available languages is commented in the script
- Name the translated file accordingly
- To run the script `python script.py`

## Considerations
In the requirements we are using version 4.0.0-rc1 of googletrans library. This is because the latest version of the library requires an API key to use Google Translate service.
Starting from version 4.1.0, Google requires a valid API key to use their Translation API service. Without a valid API key, the translation requests will fail with a 403 error. 

## Enjoy 🙃
