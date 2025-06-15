import os
from googletrans import Translator
import polib

translator = Translator()

for lang in ['hi', 'mr']:
    po_path = os.path.join('locale', lang, 'LC_MESSAGES', 'django.po')
    
    if not os.path.exists(po_path):
        print(f"Error: {po_path} not found!")
        continue
        
    po = polib.pofile(po_path)
    for entry in po:
        if not entry.msgstr:
            try:
                entry.msgstr = translator.translate(entry.msgid, src='en', dest=lang).text
                print(f"Translated: {entry.msgid[:50]}...")
            except Exception as e:
                print(f"Error: {e}")
    po.save()

print("All done! Now run: python manage.py compilemessages")