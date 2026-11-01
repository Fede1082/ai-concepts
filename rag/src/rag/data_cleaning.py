import re


def clean_text(raw_text: str) -> str | None:
    """
    Pulisce testo grezzo estratto da PDF.
    Ritorna il testo pulito o None se vuoto dopo cleaning.

    Passaggi:
    1. Rimuove header/footer ripetuti
    2. Rimuove numeri di pagina isolati
    3. Normalizza spazi e a capo
    4. Scarta se vuoto
    """

    if not raw_text or not raw_text.strip():
        return None

    # 1. Rimuovi header/footer ripetuti (righe identiche che si ripetono)
    lines = raw_text.split("\n")
    cleaned_lines = []
    last_line = ""
    repeat_count = 0

    for line in lines:
        stripped = line.strip()

        if stripped == last_line.strip():
            repeat_count += 1
            if repeat_count < 3:
                cleaned_lines.append(line)
        else:
            cleaned_lines.append(line)
            last_line = line
            repeat_count = 0

    text = "\n".join(cleaned_lines)

    # 2. Rimuovi numeri di pagina isolati (sola riga con cifre)
    text = re.sub(r"^\s*\d+\s*$", "", text, flags=re.MULTILINE)

    # 3. Normalizza spazi e a capo
    text = re.sub(r"-\n", "", text)
    text = re.sub(r" +", " ", text)
    text = re.sub(r"\n\n+", "\n\n", text)
    text = "\n".join(line.strip() for line in text.split("\n"))

    # 4. Scarta se vuoto
    text = text.strip()
    if not text:
        return None

    return text
