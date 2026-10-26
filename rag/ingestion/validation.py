"""Read-only, heuristic validation before chunking. Offsets refer to input strings."""
from collections import Counter
from dataclasses import asdict, dataclass
from difflib import SequenceMatcher
import re


@dataclass(frozen=True)
class ValidationConfig:
    # Each pattern must expose an ``id`` group. Match headings, not citations.
    section_patterns: tuple = (
        r'^\s*art\.?\s+(?P<id>\d+[a-z]?)\b',
        r'^\s*capitolo\s+(?P<id>[ivxlcdm]+|\d+)\b',
        r'^\s*(?P<id>\d+(?:\.\d+)*)(?:[.)])?\s+(?=\w)',
    )
    expect_sections: bool = False
    negations: tuple = ('non', 'mai', 'nessuno', 'nessuna', 'nessun')
    # Full-line regexes, eligible only on the first/last nonempty line of a page.
    allowed_boundary_patterns: tuple = ()
    decimal_separator: str = ','
    thousands_separator: str = '.'
    removal_threshold: float = 20.0
    alignment_threshold: float = 0.55

    def __post_init__(self):
        if self.decimal_separator == self.thousands_separator:
            raise ValueError('Numeric separators must differ')
        if not 0 <= self.removal_threshold <= 100:
            raise ValueError('removal_threshold must be between 0 and 100')
        if not 0 <= self.alignment_threshold <= 1:
            raise ValueError('alignment_threshold must be between 0 and 1')
        for pattern in self.section_patterns:
            if 'id' not in re.compile(pattern).groupindex:
                raise ValueError('Section patterns require an id group')


def extract_sections(text, strategy):
    """Return sections including preamble, retaining duplicate occurrences."""
    headings = []
    offset = 0
    for line in text.splitlines(keepends=True):
        for index, pattern in enumerate(strategy):
            match = re.match(pattern, line, re.I)
            if match:
                headings.append((offset, f'{index}:{match["id"].casefold()}', line.strip()))
                break
        offset += len(line)
    sections = []
    if not headings or headings[0][0] > 0:
        sections.append(dict(id=None, title=None, start=0,
                             end=headings[0][0] if headings else len(text)))
    for index, (start, identifier, title) in enumerate(headings):
        end = headings[index + 1][0] if index + 1 < len(headings) else len(text)
        sections.append(dict(id=identifier, title=title, start=start, end=end))
    for section in sections:
        section['text'] = text[section['start']:section['end']]
    return sections


def _tokens(text):
    return list(re.finditer(r'\d+(?:[.,]\d+)*(?:\s*%)?|[^\W\d_]+', text, re.UNICODE))


def _values(text):
    return [m.group().casefold().replace(' ', '') for m in _tokens(text)]


def measure_removal(original, cleaned):
    """Count non-whitespace source characters in deleted/replaced spans."""
    before = ''.join(original.split()).casefold()
    after = ''.join(cleaned.split()).casefold()
    matcher = SequenceMatcher(None, before, after, autojunk=False)
    removed = sum(i2 - i1 for tag, i1, i2, _, _ in matcher.get_opcodes()
                  if tag in ('delete', 'replace'))
    return dict(original_characters=len(before), removed_characters=removed,
                removed_percent=round(100 * removed / len(before), 2) if before else 0.0)


def align_passages(original, cleaned):
    """Align lexical edit spans with surrounding context, ignoring whitespace/case."""
    a, b = _tokens(original), _tokens(cleaned)
    matcher = SequenceMatcher(None, _values(original), _values(cleaned), autojunk=False)
    for tag, i, j, k, l in matcher.get_opcodes():
        if tag == 'equal':
            continue
        def span(tokens, start, end, text):
            left = tokens[start].start() if start < len(tokens) else len(text)
            right = tokens[end - 1].end() if end > start else left
            return left, right
        x, y = span(a, i, j, original)
        u, v = span(b, k, l, cleaned)
        context_a = original[max(0, x - 100):min(len(original), y + 100)]
        context_b = cleaned[max(0, u - 100):min(len(cleaned), v + 100)]
        confidence = SequenceMatcher(None, _values(context_a), _values(context_b),
                                     autojunk=False).ratio()
        yield dict(original=original[x:y], cleaned=cleaned[u:v],
                   original_span=[x, y], cleaned_span=[u, v],
                   original_context=context_a, cleaned_context=context_b,
                   confidence=round(confidence, 3))


def compare_numbers(original, cleaned, config):
    def numbers(text):
        values = []
        for token in _tokens(text):
            raw = token.group()
            if raw[0].isdigit():
                value = re.sub(r'\s+', '', raw)
                value = value.replace(config.thousands_separator, '')
                value = value.replace(config.decimal_separator, '.')
                values.append(value)
        return values
    return numbers(original) != numbers(cleaned)


def compare_negations(original, cleaned, config):
    def negations(text):
        return Counter(t for t in _values(text) if t in config.negations)
    return negations(original) != negations(cleaned)


def compare_section_structure(original, cleaned):
    a = [s['id'] for s in original if s['id'] is not None]
    b = [s['id'] for s in cleaned if s['id'] is not None]
    findings = []
    for identifier in dict.fromkeys(a + b):
        before, after = a.count(identifier), b.count(identifier)
        if before != after:
            kind = 'section_missing' if after < before else 'section_added_or_duplicated'
            findings.append(dict(type=kind, section=identifier,
                                 original_count=before, cleaned_count=after))
    if Counter(a) == Counter(b) and a != b:
        findings.append(dict(type='section_order_changed', section=None,
                             original_order=a, cleaned_order=b))
    return findings


def _allowed_spans(text, patterns):
    spans, page_offset = [], 0
    for page in text.split('\f'):
        lines, offset = [], page_offset
        for line in page.splitlines(keepends=True):
            if line.strip():
                lines.append((offset, offset + len(line), line.strip()))
            offset += len(line)
        for start, end, line in (lines[:1] + lines[-1:]):
            if any(re.fullmatch(pattern, line, re.I) for pattern in patterns):
                spans.append((start, end))
        page_offset += len(page) + 1
    return spans


def build_report(document_id, config, sections, anomalies, metrics, applicable):
    actionable = [a for a in anomalies if a['severity'] != 'informativa']
    status = ('anomalie_rilevate' if any(a['status'] == 'rilevata' for a in actionable)
              else 'da_verificare' if actionable else 'nessuna_anomalia_rilevata')
    return dict(document_id=document_id, status=status, config=asdict(config),
                checks=dict(structure='applicabile' if applicable else 'non_applicabile',
                            semantic_preservation='non_dimostrata'),
                metrics=metrics, sections=sections, anomalies=anomalies)


def validate_document(original_text, cleaned_text, config=None, document_id=None):
    """Return a JSON-serializable report; never change either input text."""
    config = config or ValidationConfig()
    original = extract_sections(original_text, config.section_patterns)
    cleaned = extract_sections(cleaned_text, config.section_patterns)
    anomalies = []
    def add(kind, section=None, severity='alta', status='rilevata', **details):
        anomalies.append(dict(type=kind, section=section, severity=severity,
                              status=status, **details))
    for finding in compare_section_structure(original, cleaned):
        add(finding.pop('type'), **finding)
    applicable = any(s['id'] is not None for s in original + cleaned)
    if config.expect_sections and not applicable:
        add('section_structure_unrecognized', severity='media', status='da_verificare')

    allowed = _allowed_spans(original_text, config.allowed_boundary_patterns)
    section_reports = []
    for section in original:
        matches = [s for s in cleaned if s['id'] == section['id']]
        unique = len(matches) == 1 and sum(s['id'] == section['id'] for s in original) == 1
        target = matches[0] if unique else None
        if matches and not unique:
            add('section_alignment_ambiguous', section['id'], 'media', 'da_verificare')
        metrics = measure_removal(section['text'], target['text'] if target else '') if unique or not matches else None
        section_reports.append(dict(id=section['id'], title=section['title'],
                                    original_span=[section['start'], section['end']],
                                    cleaned_span=[target['start'], target['end']] if target else None,
                                    metrics=metrics))
        if not unique:
            continue
        for diff in align_passages(section['text'], target['text']):
            for field, base in [('original_span', section['start']), ('cleaned_span', target['start'])]:
                diff[field] = [n + base for n in diff[field]]
            left, right = diff['original_span']
            permitted = (not diff['cleaned'] and right > left and
                         any(a <= left and right <= b for a, b in allowed))
            if permitted:
                add('allowed_boundary_removed', section['id'], 'informativa', **diff)
                continue
            status = 'rilevata' if diff['confidence'] >= config.alignment_threshold else 'da_verificare'
            severity = 'alta' if status == 'rilevata' else 'media'
            found = False
            for kind, check in [('numbers_changed', compare_numbers), ('negations_changed', compare_negations)]:
                if check(diff['original'], diff['cleaned'], config):
                    add(kind, section['id'], severity, status, **diff)
                    found = True
            if not found:
                add('content_changed', section['id'], 'media', 'da_verificare', **diff)
        allowed_count = sum(
            sum(not char.isspace() for char in original_text[a['original_span'][0]:a['original_span'][1]])
            for a in anomalies if a['type'] == 'allowed_boundary_removed'
            and section['start'] <= a['original_span'][0] < section['end'])
        metrics['allowed_removed_characters'] = allowed_count
        metrics['allowed_removed_percent'] = round(
            100 * allowed_count / metrics['original_characters'], 2) if metrics['original_characters'] else 0.0
        if metrics['removed_percent'] - metrics['allowed_removed_percent'] > config.removal_threshold:
            add('section_removal_threshold', section['id'], 'media', 'da_verificare', metrics=metrics)

    metrics = measure_removal(original_text, cleaned_text)
    permitted_chars = set()
    for anomaly in anomalies:
        if anomaly['type'] == 'allowed_boundary_removed':
            a, b = anomaly['original_span']
            permitted_chars.update(i for i in range(a, b) if not original_text[i].isspace())
    metrics['allowed_removed_characters'] = len(permitted_chars)
    metrics['allowed_removed_percent'] = round(100 * len(permitted_chars) / metrics['original_characters'], 2) if metrics['original_characters'] else 0.0
    if metrics['removed_percent'] - metrics['allowed_removed_percent'] > config.removal_threshold:
        add('document_removal_threshold', severity='media', status='da_verificare', metrics=metrics)
    return build_report(document_id, config, section_reports, anomalies, metrics, applicable)
