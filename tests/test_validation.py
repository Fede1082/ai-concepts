import json
import unittest

from rag.ingestion.validation import ValidationConfig, validate_document


class ValidationTests(unittest.TestCase):
    def kinds(self, report):
        return {a['type'] for a in report['anomalies']}

    def test_negation_removed(self):
        report = validate_document('Il cliente non deve pagare la quota.',
                                   'Il cliente deve pagare la quota.')
        self.assertIn('negations_changed', self.kinds(report))
        finding = next(a for a in report['anomalies'] if a['type'] == 'negations_changed')
        self.assertEqual(finding['severity'], 'alta')
        self.assertEqual(finding['original_span'], [11, 14])

    def test_percentage_removed(self):
        report = validate_document('Lo sconto previsto è del 25% sul totale.',
                                   'Lo sconto previsto è sul totale.')
        self.assertIn('numbers_changed', self.kinds(report))

    def test_missing_section(self):
        report = validate_document('Art. 1\nPrimo testo.\nArt. 2\nSecondo testo.',
                                   'Art. 1\nPrimo testo.')
        self.assertIn('section_missing', self.kinds(report))
        self.assertEqual(report['sections'][1]['metrics']['removed_percent'], 100)

    def test_whitespace_only(self):
        report = validate_document('Un   testo\n\ncon\tspazi.', 'Un testo con spazi.')
        self.assertEqual(report['anomalies'], [])
        self.assertEqual(report['metrics']['removed_percent'], 0)

    def test_allowed_headers(self):
        report = validate_document('HEADER\nIl primo contenuto.\fHEADER\nIl secondo contenuto.',
                                   'Il primo contenuto.\nIl secondo contenuto.',
                                   ValidationConfig(allowed_boundary_patterns=('HEADER',)))
        self.assertEqual(report['status'], 'nessuna_anomalia_rilevata')
        self.assertEqual(len(report['anomalies']), 2)
        self.assertGreater(report['metrics']['allowed_removed_characters'], 0)

    def test_boundary_rule_does_not_allow_body_deletion(self):
        report = validate_document('Inizio\nHEADER\nFine', 'Inizio\nFine',
                                   ValidationConfig(allowed_boundary_patterns=('HEADER',)))
        self.assertIn('content_changed', self.kinds(report))

    def test_order_and_duplicates(self):
        original = 'Art. 1\nUno\nArt. 2\nDue'
        reordered = 'Art. 2\nDue\nArt. 1\nUno'
        self.assertIn('section_order_changed', self.kinds(validate_document(original, reordered)))
        self.assertIn('section_added_or_duplicated', self.kinds(validate_document(original, original + '\nArt. 2\nDue')))

    def test_ambiguous_and_json(self):
        report = validate_document('Contenuto iniziale', 'Testo diverso',
                                   ValidationConfig(expect_sections=True))
        self.assertEqual(report['status'], 'da_verificare')
        json.dumps(report, ensure_ascii=False)

    def test_numeric_format_and_percentage_change(self):
        report = validate_document('Quota pari a 12,5%.', 'Quota pari a 125.')
        self.assertIn('numbers_changed', self.kinds(report))

    def test_negation_added(self):
        self.assertIn('negations_changed', self.kinds(validate_document(
            'Il cliente deve pagare la quota.', 'Il cliente non deve pagare la quota.')))


if __name__ == '__main__':
    unittest.main()
