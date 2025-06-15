from django.core.management.base import BaseCommand
from googletrans import Translator
import polib
import os

class Command(BaseCommand):
    help = 'Auto-translate .po files'

    def handle(self, *args, **options):
        translator = Translator(service_urls=['translate.google.com'])
        
        for lang in ['hi', 'mr']:
            po_path = os.path.join('locale', lang, 'LC_MESSAGES', 'django.po')
            
            if not os.path.exists(po_path):
                self.stdout.write(f"Creating {po_path}...")
                os.makedirs(os.path.dirname(po_path), exist_ok=True)
                with open(po_path, 'w', encoding='utf-8') as f:
                    f.write('')
                continue
                
            po = polib.pofile(po_path)
            for entry in po:
                if not entry.msgstr and entry.msgid:
                    try:
                        translation = translator.translate(
                            entry.msgid, 
                            src='en', 
                            dest=lang
                        ).text
                        entry.msgstr = translation
                        print(f"Translated: {entry.msgid[:30]}... → {translation[:30]}...")
                    except Exception as e:
                        print(f"Error translating: {e}")
            po.save()
            print(f"✅ Finished {lang} translations!")