# Validazione prima del chunking

Il modulo `validation.py` usa solo la libreria standard e non modifica i testi.
Conservare il testo estratto, inclusi newline e separatori pagina `\f`, prima del cleaning.

```python
import json
from pathlib import Path
from rag.ingestion.validation import ValidationConfig, validate_document

config = ValidationConfig(
    expect_sections=True,
    allowed_boundary_patterns=(r'Manuale tecnico', r'Pagina \d+'),
)
report = validate_document(original_text, cleaned_text, config, document_id='manuale.pdf')
Path('validation-report.json').write_text(
    json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8'
)
```

Le strategie predefinite riconoscono articoli, capitoli e titoli numerati a inizio
riga. Gli ID nel report hanno prefisso dell'indice del pattern, ad esempio `0:3`
per `Art. 3`. Pattern personalizzati devono contenere il gruppo `(?P<id>...)`;
lo stesso pattern deve riconoscere originale e versione pulita. I riferimenti
alle posizioni sono intervalli di caratteri `[inizio, fine)` nei due input.

Il report distingue anomalie rilevate, casi da verificare e rimozioni consentite.
Le percentuali misurano caratteri non bianchi eliminati o sostituiti, ignorando
il cambio di maiuscole. Non sono una misura di perdita semantica. Le rimozioni
consentite rimangono nel totale ma vengono escluse dal confronto con la soglia.

Limiti: l'allineamento lessicale con contesto locale non comprende il significato.
Convenzioni numeriche dipendono dalla configurazione (default italiano); documenti
con convenzioni miste richiedono revisione. Le negazioni riconosciute sono solo
quelle configurate. Header/footer sono consentiti esclusivamente ai margini delle
pagine; preservare i separatori pagina è necessario per riconoscerli.
Sezioni duplicate non vengono abbinate arbitrariamente: le metriche sono `null`
e il caso è da verificare. Una sezione scomparsa ha rimozione del 100%; i suoi
numeri e negazioni non vengono associati a frasi di altre sezioni.
Se il cleaning appiattisce tutte le righe, il riconoscimento delle sezioni può
fallire: il report segnala le sezioni mancanti, senza ricostruirle automaticamente.
`nessuna_anomalia_rilevata` non certifica la conservazione del significato.

Test: `python3 -m unittest discover -s tests -v`.
