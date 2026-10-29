1.Fare data cleaning(Normalizzazione, rimozione rumore, conservazione struttura)
2. Verifica integrità del dataset nuovo, assicurarsi nn si sono persi iformazioni importanti



1. Rimozione del "Rumore" Strutturale e Visivo

I documenti (soprattutto PDF e HTML) contengono elementi utili per l'occhio umano ma dannosi per un LLM.
• Header e Footer: Rimuovere intestazioni di pagina, numeri di pagina e piè di pagina. Se inclusi nei chunk, frammentano le frasi e confondono l'algoritmo di ricerca semantica.
• Codice Boilerplate: In caso di file HTML/XML, eliminare tag di formattazione, script JavaScript, fogli di stile CSS e menu di navigazione.
• Separatori e Caratteri Speciali: Pulire stringhe di trattini (---), asterischi (***) o sequenze di spazi vuoti e ritorni a capo multipli (\n\n\n) che alterano il calcolo delle distanze semantiche.

2. Normalizzazione del Testo

Rendere il testo uniforme aiuta i modelli di embedding a lavorare su vettori più coerenti.
• Standardizzazione dei caratteri: Convertire le virgolette "intelligenti" (curve) in virgolette dritte standard, gestire correttamente le codifiche (es. forzare UTF-8) e risolvere i problemi di legature (es. "fi" o "fl" uniti nei PDF).
• Espansione delle abbreviazioni: Se il dominio lo richiede, mappare e sostituire acronimi ambigui o abbreviazioni per standardizzare i termini (es. "all." -> "allegato").
• Correzione degli errori di OCR: Se i documenti derivano da scansioni, applicare filtri di correzione ortografica guidati dal contesto per correggere lettere scambiate (es. "o" al posto di "0", o "l" al posto di "1").

3. Gestione di Tabelle, Elementi Grafici e Contenuti Multimediali

Le tabelle e le immagini sono i punti deboli dei sistemi RAG tradizionali basati su solo testo.
• Linearizzazione delle tabelle: Non lasciare le tabelle come testo grezzo disallineato. Convertirle in formati strutturati leggibili dagli LLM, come Markdown, JSON, oppure sostituirle con un riassunto testuale (textual description) della tabella stessa.
• Didascalie e Alt-Text: Estrarre il testo alternativo delle immagini e le didascalie dei grafici, associandoli chiaramente al paragrafo di contesto in cui si trovano.

4. Filtraggio dei Contenuti e De-duplicazione

• Rimozione dei duplicati: Eliminare versioni obsolete dello stesso documento o sezioni ripetute (es. clausole di esclusione della responsabilità o disclaimer legali presenti in fondo a ogni pagina).
• Rimozione di PII (Informazioni Personali Identificabili): Mascherare o anonimizzare dati sensibili (nomi, email, codici fiscali, numeri di telefono) sia per ragioni di privacy (GDPR) sia per evitare che il modello si concentri su dettagli irrilevanti.
• Sfoltimento dei contenuti irrilevanti: Rimuovere introduzioni puramente formali, ringraziamenti o pagine di copertina che non apportano valore informativo.

5. Strategie Avanzate di Pre-Chunking

La pulizia non è solo "cancellare", ma anche preparare la struttura corretta.
• Arricchimento dei metadati: Prima di spezzare il testo, estrarre e iniettare metadati chiave (es. autore, data, capitolo di appartenenza, tag tematici). Questi metadati verranno poi agganciati a ogni singolo chunk per abilitare il filtraggio ibrido (keyword + vettoriale).
• Risoluzione delle coreferenze: Sostituire i pronomi (es. "Esso", "Questo software") con il soggetto effettivo a cui si riferiscono se si trovano all'inizio di un potenziale chunk, per evitare che il blocco perda significato una volta isolato.




Altri criteri
Operazione	Quando applicarla	Priorità
Rimuovere spazi multipli	Quando sono rumore di formattazione	Alta
Normalizzare caratteri Unicode	Quando ci sono caratteri equivalenti rappresentati diversamente	Media
Rimuovere header/footer ripetuti	PDF con intestazioni ricorrenti	Alta
Rimuovere numeri di pagina isolati	Se non hanno significato nel contenuto	Media
Correggere parole spezzate	Quando l'estrazione interrompe parole a fine riga	Alta
Gestire righe vuote e newline	Senza perdere i paragrafi	Alta
Eliminare duplicati	Quando il contenuto è realmente duplicato	Media
Eliminare stop words	Generalmente da evitare nel RAG semantico	Bassa
Lemmatizzazione/stemming	Generalmente non necessari per embeddings moderni	Bassa