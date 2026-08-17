import unittest

from awptools import textprocessing 


class TestPostprocess(unittest.TestCase):
    def test_post_process1(self):
        text = ("Cham Swiss Properties AG hat für das erste Halbjahr 2025 einen Konzerngewinn von 144.0 Mio. CHF "
                "gemeldet. Das betriebliche Ergebnis vor Neubewertung betrug 39.0 Mio. CHF, wobei ein signifikanter "
                "Beitrag von 37.3 Mio. CHF aus dem Verkauf von Promotionsliegenschaften resultierte. Der Ertrag aus "
                "Vermietung belief sich auf 9.1 Mio. CHF. Der Gewinn pro Aktie lag bei 3.73 CHF. Die "
                "Eigenkapitalquote betrug 61.1 %, während der LTV bei 29.2 % lag. Cham Swiss Properties meldete "
                "Fortschritte bei ihren Bau- und Entwicklungsvorhaben, darunter der Baustart in Genf und der "
                "Fortschritt der Arbeiten für das Casino in Winterthur. Ein Vergleich mit den Vorjahresergebnissen "
                "ist aufgrund der Fusion der Ina Invest AG und der Cham Group AG im Jahr 2025 nicht aussagekräftig.")
        text_processed = textprocessing.awp_format_text_de(text, number_format=True, paragraphs=True)
        text_expected = ("Cham Swiss Properties AG hat für das erste Halbjahr 2025 einen Konzerngewinn "
                         "von 144,0 Millionen Franken gemeldet. Das betriebliche Ergebnis vor Neubewertung betrug "
                         "39,0 Millionen Franken, wobei ein signifikanter Beitrag von 37,3 Millionen Franken aus dem "
                         "Verkauf von Promotionsliegenschaften resultierte.\n\nDer Ertrag aus Vermietung belief sich "
                         "auf 9,1 Millionen Franken. Der Gewinn pro Aktie lag bei 3,73 Franken.\n\nDie "
                         "Eigenkapitalquote betrug 61,1 Prozent, während der LTV bei 29,2 Prozent lag. Cham Swiss "
                         "Properties meldete Fortschritte bei ihren Bau- und Entwicklungsvorhaben, darunter der "
                         "Baustart in Genf und der Fortschritt der Arbeiten für das Casino in Winterthur.\n\nEin "
                         "Vergleich mit den Vorjahresergebnissen ist aufgrund der Fusion der Ina Invest AG und der "
                         "Cham Group AG im Jahr 2025 nicht aussagekräftig.")
        self.assertEqual(text_expected, text_processed)

    def test_post_process2(self):
        text = ("Baloise Holding AG meldete für das erste Halbjahr 2025 einen Aktionärsgewinn von 275,9 Millionen "
                "Franken, was einem Anstieg von 25,5 Prozent gegenüber dem gleichen Zeitraum des Vorjahres "
                "entspricht. Die annualisierte Eigenkapitalrendite erreichte 15,5 Prozent, verglichen mit 13,"
                "0 Prozent im ersten Halbjahr 2024. Das Prämienvolumen der Gruppe belief sich auf 545'662,6 Millionen "
                "Franken und lag damit leicht unter dem Vorjahreswert von 4,878.0 Millionen Franken. Der "
                "Schaden-Kosten-Satz verbesserte sich auf 90,6 Prozent von 93,2 Prozent im Vorjahr. Das "
                "Anlageergebnis im Segment Nichtleben stieg auf 136,7 Millionen Franken von 109,0 Millionen Franken "
                "im Vorjahr. Das Schweizer Geschäft trug maßgeblich zum EBIT bei, das um 58,3 Prozent auf 254,"
                "4 Millionen Franken gesteigert wurde. In Deutschland erhöhte sich der EBIT-Beitrag um 11,"
                "9 Prozent auf 51,9 Millionen Franken. Die Unternehmensstrategie fokussiert sich weiterhin auf die "
                "Optimierung des Kerngeschäfts und die Verbesserung der Profitabilität.")
        text_processed = textprocessing.awp_format_text_de(text, number_format=True, paragraphs=True)
        text_expected = ("Baloise Holding AG meldete für das erste Halbjahr 2025 einen Aktionärsgewinn von 275,"
                         "9 Millionen Franken, was einem Anstieg von 25,5 Prozent gegenüber dem gleichen Zeitraum des "
                         "Vorjahres entspricht. Die annualisierte Eigenkapitalrendite erreichte 15,5 Prozent, "
                         "verglichen mit 13,0 Prozent im ersten Halbjahr 2024. Das Prämienvolumen der Gruppe belief "
                         "sich auf 545'662,6 Millionen Franken und lag damit leicht unter dem Vorjahreswert von 4878,"
                         "0 Millionen Franken.\n\nDer Schaden-Kosten-Satz verbesserte sich auf 90,6 Prozent von 93,"
                         "2 Prozent im Vorjahr. Das Anlageergebnis im Segment Nichtleben stieg auf 136,7 Millionen "
                         "Franken von 109,0 Millionen Franken im Vorjahr.\n\nDas Schweizer Geschäft trug massgeblich zum "
                         "EBIT bei, das um 58,3 Prozent auf 254,4 Millionen Franken gesteigert wurde. In Deutschland "
                         "erhöhte sich der EBIT-Beitrag um 11,9 Prozent auf 51,9 Millionen Franken.\n\nDie "
                         "Unternehmensstrategie fokussiert sich weiterhin auf die Optimierung des Kerngeschäfts und "
                         "die Verbesserung der Profitabilität.")
        self.assertEqual(text_expected, text_processed)

    def test_post_process3(self):
        text = ("u-blox Holding AG hat das vorläufige Zwischenergebnis des öffentlichen Übernahmeangebots von ZI "
                "Zenith S.à r.l., einer Tochter von Advent International, veröffentlicht. Nach Abschluss der "
                "Angebotsfrist am 9. Oktober 2025 wurden insgesamt 4.774.528 u-blox-Aktien angedient. Unter "
                "Berücksichtigung bereits gehaltener Aktien und unwiderruflicher Andienungszusagen beläuft sich der "
                "Anteil von Zenith an u-blox auf insgesamt 64,64 % des ausgegebenen Aktienkapitals und der "
                "Stimmrechte. Das endgültige Zwischenergebnis wird voraussichtlich am 15. Oktober 2025 "
                "veröffentlicht. Der Abschluss der Transaktion wird im vierten Quartal 2025 erwartet.")
        text_processed = textprocessing.awp_format_text_de(text, number_format=True, paragraphs=True)
        text_expected = ("u-blox Holding AG hat das vorläufige Zwischenergebnis des öffentlichen Übernahmeangebots "
                         "von ZI Zenith S.à r.l., einer Tochter von Advent International, veröffentlicht. Nach "
                         "Abschluss der Angebotsfrist am 9. Oktober 2025 wurden insgesamt 4'774'528 u-blox-Aktien "
                         "angedient.\n\nUnter Berücksichtigung bereits gehaltener Aktien und unwiderruflicher "
                         "Andienungszusagen beläuft sich der Anteil von Zenith an u-blox auf insgesamt 64,64 Prozent "
                         "des ausgegebenen Aktienkapitals und der Stimmrechte. Das endgültige Zwischenergebnis wird "
                         "voraussichtlich am 15. Oktober 2025 veröffentlicht.\n\nDer Abschluss der Transaktion wird im "
                         "vierten Quartal 2025 erwartet.")
        self.assertEqual(text_expected, text_processed)

    def test_post_process4(self):
        text = ("Die Banque Cantonale de Genève (BCGE) führt einen 10-zu-1 Aktiensplit durch. Die Anzahl der Aktien "
                "erhöht sich von 7.200.000 auf 72.000.000, während der Nennwert je Aktie von CHF 50 auf CHF 5 gesenkt "
                "wird. Die Stimmrechte der Aktionäre bleiben unverändert. Der Aktiensplit tritt am 15. Oktober 2025 "
                "in Kraft; ab diesem Datum gelten eine neue Valorennummer (148589935) und ISIN (CH1485899350).")
        text_processed = textprocessing.awp_format_text_de(text, number_format=True, paragraphs=True)
        text_expected = ("Die Banque Cantonale de Genève (BCGE) führt einen 10-zu-1 Aktiensplit durch. Die Anzahl der "
                         "Aktien erhöht sich von 7'200'000 auf 72'000'000, während der Nennwert je Aktie von 50 Fr. "
                         "auf 5 Fr. gesenkt wird.\n\nDie Stimmrechte der Aktionäre bleiben unverändert. Der Aktiensplit "
                         "tritt am 15. Oktober 2025 in Kraft; ab diesem Datum gelten eine neue Valorennummer ("
                         "148589935) und ISIN (CH1485899350).")
        self.assertEqual(text_expected, text_processed)

    def test_post_process5(self):
        text = ("Die Plazza AG hat eine neue Präsentation veröffentlicht. Das Immobilienportfolio beläuft sich auf CHF "
                "1'229 Mio., wobei der Wohnanteil am Soll-Netto-Mietertrag 85 % beträgt. Der annualisierte "
                "Liegenschaftenertrag liegt bei CHF 39 Mio. und die Eigenkapitalquote bei 61 %. Das Unternehmen weist "
                "einen Gewinn nach Steuern von CHF 25,3 Mio. aus, gegenüber CHF 20,5 Mio. im Vorjahr. Der Leerstand "
                "im Wohnsegment beträgt 7,2 %, im Geschäftshausbereich 4,8 %. Die Übernahme der A. Schönbächler & Co "
                "AG wurde abgeschlossen und die Entwicklungsprojekte verlaufen planmäßig. Die vollständige "
                "Präsentation können Sie über den untenstehenden Link abrufen.")
        text_processed = textprocessing.awp_format_text_de(text, number_format=True, paragraphs=True)
        text_expected = ("Die Plazza AG hat eine neue Präsentation veröffentlicht. Das Immobilienportfolio beläuft "
                         "sich auf 1229 Millionen Franken, wobei der Wohnanteil am Soll-Netto-Mietertrag 85 Prozent "
                         "beträgt.\n\nDer annualisierte Liegenschaftenertrag liegt bei 39 Millionen Franken und die "
                         "Eigenkapitalquote bei 61 Prozent. Das Unternehmen weist einen Gewinn nach Steuern von 25,"
                         "3 Millionen Franken aus, gegenüber 20,5 Millionen Franken im Vorjahr.\n\nDer Leerstand im "
                         "Wohnsegment beträgt 7,2 Prozent, im Geschäftshausbereich 4,8 Prozent. Die Übernahme der A. "
                         "Schönbächler &amp; Co AG wurde abgeschlossen und die Entwicklungsprojekte verlaufen "
                         "planmässig.\n\nDie vollständige Präsentation können Sie über den untenstehenden Link abrufen.")
        self.assertEqual(text_expected, text_processed)

    def test_post_process6(self):
        text = ("Die Asmallworld AG lädt zu einer außerordentlichen Generalversammlung am 19. Dezember 2025 ein. Zur "
                "Abstimmung stehen die maximale Ausweitung des Kapitalbands mit einer neuen Untergrenze von CHF "
                "7.230.729,00 und einer neuen Obergrenze von CHF 21.692.185,00 sowie die Ermächtigung des "
                "Verwaltungsrats, das Aktienkapital innerhalb dieses Rahmens bis zum 30. November 2030 anzupassen. "
                "Weiterhin wird eine Erhöhung des bedingten Kapitals für Beteiligungsprogramme um CHF 2.820.485,"
                "00 auf CHF 4.820.485,00 vorgeschlagen, ebenso eine Erhöhung des bedingten Kapitals für "
                "Finanzierungszwecke um CHF 1.410.242,00 auf CHF 2.410.242,00.")
        text_processed = textprocessing.awp_format_text_de(text, number_format=True, paragraphs=True)
        text_expected = ("Die Asmallworld AG lädt zu einer ausserordentlichen Generalversammlung am 19. Dezember 2025 "
                         "ein. Zur Abstimmung stehen die maximale Ausweitung des Kapitalbands mit einer neuen "
                         "Untergrenze von 7'230'729,00 Fr. und einer neuen Obergrenze von 21'692'185,00 Fr. sowie die "
                         "Ermächtigung des Verwaltungsrats, das Aktienkapital innerhalb dieses Rahmens bis zum 30. "
                         "November 2030 anzupassen.\n\nWeiterhin wird eine Erhöhung des bedingten Kapitals für "
                         "Beteiligungsprogramme um 2'820'485,00 Fr. auf 4'820'485,00 Fr. vorgeschlagen, ebenso eine "
                         "Erhöhung des bedingten Kapitals für Finanzierungszwecke um 1'410'242,00 Fr. auf 2'410'242,"
                         "00 Fr.")
        self.assertEqual(text_expected, text_processed)


if __name__ == "__main_":
    unittest.main()
