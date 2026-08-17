import re
from datetime import datetime


def post_process_brief_de(text: str) -> str:
    """
    Format German brief text
    :param text: raw text
    :return: formatted text
    """
    text = replace_abbreviations_and_specials_de(text)
    text = structure_paragraphs(text)
    return text


def post_process_brief_fr(text: str) -> str:
    """
    Format French brief text
    :param text: raw text
    :return: formatted text
    """
    text = replace_special_chars(text)
    text = replace_number_format(text)
    text = structure_paragraphs(text)
    return text


def add_footer_and_start_de(text: str, company_name: str, company_place: str,
                            link="", provider="", content_datetime=None) -> str:
    """
    Function to add awp start and footer in German
    :param text: article text
    :param company_name: company name
    :param company_place: company place
    :param link: link to news release if available
    :param provider: wire provider if available
    :param content_datetime: timestamp of content
    :return: text including start and footer
    """
    if content_datetime is None:
        content_datetime = datetime.today()
    date = content_datetime.strftime("%d.%m.%Y")

    if provider.strip() == "":
        disclaimer = (
            "Disclaimer: Diese Kurzzusammenfassung wurde mit Unterstützung von generativer künstlicher "
            "Intelligenz erstellt. Die Mitteilung, auf der die Kurzzusammenfassung beruht, wurde von "
            f"{company_name} am {date} publiziert. Für den Inhalt der Mitteilung ist ausschliesslich "
            f"{company_name} verantwortlich."
        )
    else:
        disclaimer = (
            "Disclaimer: Diese Kurzzusammenfassung wurde mit Unterstützung von generativer künstlicher "
            "Intelligenz erstellt. Die Mitteilung, auf der die Kurzzusammenfassung beruht, wurde von "
            f"{company_name} am {date} via Distributor {provider} publiziert. Für den Inhalt der Mitteilung "
            f"ist ausschliesslich {company_name} verantwortlich."
        )

    if link == "":
        link_sentence = ""
    else:
        link_sentence = f"Link zum Originaltext: {link}\n\n"

    text = (
        f"{company_place} (awp) - "
        f"{text}\n\n"
        f"{link_sentence}"
        f"awp-robot/"
    )

    return text


def add_footer_and_start_fr(text: str, company_name: str, company_place: str,
                            link="", provider="", content_datetime=None) -> str:
    """
    Function to add awp start and footer in French
    :param text: article text
    :param company_name: company name
    :param company_place: company place
    :param link: link to news release if available
    :param provider: wire provider if available
    :param content_datetime: timestamp of content
    :return: text including start and footer
    """
    if content_datetime is None:
        content_datetime = datetime.today()
    date = content_datetime.strftime("%d.%m.%Y")

    if provider.strip() == "":
        disclaimer = (
            "Avertissement: ce résumé a été généré par l'intelligence artificielle générative. "
            f"Le communiqué sur lequel se base ce texte a été publié par {company_name} le {date}. "
            f"{company_name} est seul responsable du contenu de ce communiqué."
        )
    else:
        disclaimer = (
            "Avertissement: ce résumé a été généré par l'intelligence artificielle générative. "
            f"Le communiqué sur lequel se base ce texte a été publié par {company_name} le {date} "
            f"via le distributeur {provider}. {company_name} est seul responsable du contenu de ce communiqué."
        )

    if link == "":
        link_sentence = ""
    else:
        link_sentence = f"Lien vers le texte officiel: {link}\n\n"

    text = (
        f"{company_place} (awp) - "
        f"{text}\n\n"
        f"{link_sentence}"
        f"awp-robot/"
    )
    return text


def structure_paragraphs(text: str) -> str:
    """
    Function to break down text into paragraphs
    :param text: original text
    :return: processed text
    """
    # split sentences
    sentences = re.split(r"(?<!\d)(?<!Fr)(?<!\s[A-Z])\.\s(?=[A-Z])", text.strip())
    result = ""
    breakingPoint = 3
    for i in range(0, len(sentences)):
        result = result + sentences[i].strip()
        if i < len(sentences) - 1:
            result = result + ". "  # Add punctuation and space back, except on the last sentence
        # Add linebreak already after 2 sentences,
        # if the current paragraph is too long or if a lonely sentence at the end can be avoided
        if len(result.replace(".*(?=\n\n)", "")) + len(sentences[i]) > 300 | (len(sentences) - i) % 2 != 1 & (
                len(sentences) - 1 % 2 == 0):
            breakingPoint = 2
        # Add line break after every 3 sentences
        if (i + 1) % breakingPoint == 0:
            result = result.strip() + "\n\n"

    return result.strip()


def replace_special_chars(text: str) -> str:
    """
    Function to replace special characters
    :param text: original text
    :return: edited text
    """
    text = re.sub("&", "&amp;", text)
    text = text.replace("«", "\"")
    text = text.replace("»", "\"")
    text = text.replace("–", "-")
    text = text.replace("™", "")
    text = re.sub("\u0095", " - ", text)
    text = re.sub("\u0027", "'", text)
    text = re.sub("\u0091|\u0092|\u00B4|\u2019", "'", text)
    text = re.sub("\u201c|\u201d", "\"", text)
    text = re.sub("\u002C", ",", text)
    text = re.sub("\u002D", "-", text)
    text = re.sub("\u003C", "&lt;", text)
    text = re.sub("\u003E", "&gt;", text)
    text = text.replace("·", "-")
    text = re.sub(r"(?<=\d)\?(?=\d)", "'", text)
    text = text.replace("®", "")
    text = text.replace("ß", "ss")
    text = text.replace("€", "EUR ")
    text = text.replace("US$", "USD ")
    text = text.replace("$", "USD ")
    text = text.replace("£", "GBP ")
    text = text.replace("ș", "s")
    text = text.replace("ă", "a")
    text = re.sub(r"[^\u0020-\u007e\u00a0-\u00ff]", "", text)
    text = re.sub(r"\bDr\. ", "", text)
    text = re.sub(r"(\d)m2|m²", "$1 Quadratmeter", text)
    text = re.sub(r"\bm2\b|m²", "Quadratmeter", text)

    return text


def replace_abbreviations_and_specials_de(text: str) -> str:
    """
    Function to format text according to awp style
    :param text: original text
    :return: edited text
    """
    text = replace_special_chars(text)
    text = replace_number_format(text)

    text = re.sub(r"(?<=\d)%ig", "-prozentig", text)
    text = re.sub(r"%ig", "prozentig", text)
    text = re.sub(r"\s?%", " Prozent", text)
    text = re.sub(r"(Mio)\.?", "Millionen", text)
    text = re.sub(r"(Mrd|Mia)\.?", "Milliarden", text)

    text = re.sub(r"\b((CHF|Fr\.)(?=[\s\d])\s?)([\d,\.']+)\s?(Millionen|Milliarden)", r"\3 \4 Franken", text)
    text = re.sub(r"(\b(CHF|Fr\.)(?=[\s\d])\s?)([\d\.,']+\d|\d+)", r"\3 Fr.", text)

    text = re.sub(r"\b(EUR(?=[\s\d])\s?)([\d,\.']+)\s?(Millionen|Milliarden)", r"\2 \3 Euro", text)
    text = re.sub(r"\b(EUR(?=[\s\d])\s?)(\d+[.,']?\d+)", r"\2 Euro", text)

    text = re.sub(r"\b(USD(?=[\s\d])\s?)([\d,\.']+)\s?(Millionen|Milliarden)", r"\2 \3 US-Dollar", text)
    text = re.sub(r"\b(USD(?=[\s\d])\s?)(\d+[.,']?\d+)", r"\2 US-Dollar", text)

    text = re.sub(r"\bCHF\b", "Franken", text)
    text = re.sub(r"\bEUR\b", "Euro", text)
    text = re.sub(r"\bUSD\b", "US-Dollar", text)

    text = re.sub(r"(?<!\.)\.{2}(?!\.)", ".", text)

    return text


def post_process_brief_headline_de(text: str) -> str:
    """
    Function to process and edit German headlines
    :param text: original text
    :return: edited text
    """
    text = replace_special_chars(text)
    text = replace_number_format(text)

    text = re.sub(r"\s%", "%", text)
    text = re.sub(r"\bCHF\b", "Fr.", text)
    text = re.sub(r" Mio\.", " Mio", text)

    text = re.sub(r"\b((CHF|Fr\.)(?=[\s\d])\s?)([\d,\.']+)\s?(Millionen|Mio|Mia|Mrd|Milliarden)", r"\3 \4 Fr.", text)
    text = re.sub(r"(\b(CHF|Fr\.)(?=[\s\d])\s?)(\d+[.,']?\d+)", r"\3 Fr.", text)

    text = re.sub(r"\b(EUR(?=[\s\d])\s?)([\d,\.']+)\s?(Millionen|Mio|Mia|Mrd|Milliarden)", r"\2 \3 EUR", text)
    text = re.sub(r"\b(EUR(?=[\s\d])\s?)(\d+[.,']?\d+)", r"\2 EUR", text)

    text = re.sub(r"\b(USD(?=[\s\d])\s?)([\d,\.']+)\s?(Millionen|Mio|Mia|Mrd|Milliarden)", r"\2 \3 USD", text)
    text = re.sub(r"\b(USD(?=[\s\d])\s?)(\d+[.,']?\d+)", r"\2 USD", text)

    text = re.sub(r"(\d+)\.(\d+)(?=\s(Fr\.|Franken|Euro|EUR|USD|Dollar|Mio|Mrd|Mia|Milli))", r"\1,\2", text)
    text = re.sub(r"(?<!\.)\.{2}(?!\.)", ".", text)

    return text


def replace_number_format(text: str) -> str:
    """
    Function to format numbers according to awp style
    :param text: original text
    :return: edited text
    """
    # Replace commas used as thousands separator
    text = re.sub(r"((?<=\d{3}\,\d{3})|(?<=\d{1}\,\d{3})|(?<=\d{2}\,\d{3}))\,(?! )|\,(?=\d{3}\.\d{3})", "'", text)
    # Replace dots used as thousands separator
    text = re.sub(r"((?<=\d{3}\.\d{3})|(?<=\d{1}\.\d{3})|(?<=\d{2}\.\d{3}))\.(?! )|\.(?=\d{3}\.\d{3})", "'", text)
    # Replace commas used as thousands separator in combination with dot decimal delimiter
    text = re.sub(r"(\d{2,}),(\d+)\.(\d+)", r"\1'\2,\3", text)
    # Replace dots used as thousands separator in combination with comma decimal delimiter
    text = re.sub(r"(\d{2,})\.(\d+)\,(\d+)", r"\1'\2,\3", text)
    # Remove comma as thousands separator for 4 digit values
    text = re.sub(r"(\d),(\d+)\.(\d+)", r"\1\2,\3", text)
    # Replace dot as decimal delimiter with commas
    text = re.sub(r"(?<=[^\d\.])(\d+)\.(\d+)(?!\.|\d)", r"\1,\2", text)
    # Remove thousands separator for 4 digit values
    text = re.sub(r"(\b\d)'(\d{3}\b)(?![\d'])", r"\1\2", text)
    return text


def post_process_brief_headline_fr(text: str) -> str:
    """
    Function to process and edit French headlines
    :param text: original text
    :return: edited text
    """
    text = replace_special_chars(text)
    text = re.sub(r"\s\:(?=\s[a-zA-Z])", ":", text)
    return text
