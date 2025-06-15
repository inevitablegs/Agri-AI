from googletrans import Translator
import polib

# Set your target language: 'hi' for Hindi, 'mr' for Marathi
target_lang = 'hi'

# Path to your .po file
po_file = 'locale/hi/LC_MESSAGES/django.po'

# Load and translate
po = polib.pofile(po_file)
translator = Translator()

for entry in po:
    if not entry.translated():
        translated = translator.translate(entry.msgid, dest=target_lang).text
        entry.msgstr = translated
        print(f"{entry.msgid} ➜ {translated}")

# Save the updated file
po.save()
