from typing import Any
import re
import pandas as pd
from awptools import prompting
from awptools import utils
from awptools import textprocessing

import classifier
import json
import textprocessor
import company_lookup
import time
from db_pool import pool
from db_pool import insert_dict
from datetime import datetime, time
import logging

# Load available prompts
db = pool.get_connection()
sql_stmt = "SELECT id FROM ai_texts.prompts;"
cursor = db.cursor()
cursor.execute(sql_stmt)
prompt_ids = [row[0] for row in cursor.fetchall()]
db.close()

# weekdays
weekdays_de = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag"]
weekdays_fr = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"]


# timecheck
def is_time_in_range(start: time, end: time) -> bool:
    """Check if the current time is within the given range (inclusive)."""
    now = datetime.now().time().replace(second=0, microsecond=0)
    if start <= end:
        return start <= now <= end
    # Handles overnight ranges (e.g. 22:00 to 06:00)
    return now >= start or now <= end


def is_time_in_publication_window() -> bool:
    """Check if the current time is inside typcal company publication window."""
    return (is_time_in_range(time(5, 0), time(7, 20)) and
            is_time_in_range(time(17, 30), time(20, 0)))


def publish_brief(headline: str, text: str, isin: str, test: bool, provider="", link="", origin="", pubt_code=""):
    """
    Function to classify a message, fetch metadata, generate and publish news brief
    :param headline: headline of news release
    :param text: text of news release
    :param isin: company isin
    :param test: if true use test environment
    :param provider: default empty, use for wire providers like 'EQS', 'GNW', ...
    :param link: link to release if available
    :param origin: origin (distribution) of media release
    :param pubt_code: Pubt code if available
    :return: json string to indicate if german and French briefs were published
    """
    # Clean input texts and discard too short texts
    if origin == "eqs":
        if "----" in text:
            text = re.split("-{4,}", text)[1]
        ad_hoc_search = "ad hoc announcement pursuant to art.* 53 lr|veröffentlichung einer ad-hoc-mitteilung gemäss "
        "art.* 53 kr|release of an ad hoc announcement pursuant to art.* 53 lr"
        if re.search(ad_hoc_search, text.lower()) is not None:
            text = re.split(ad_hoc_search, text.lower())[1]
        end_search = ("end of media release|ende der medienmitteilung|fin du communiqu|end of inside information|ende "
                      "der adhoc-mitteilung")
        text = re.split(end_search, text.lower())[0]
        if re.search("16 KR|16 LR|16 Kotierungsreglement der BX|Art. 16", text) is not None:
            text = re.split("16 KR|16 LR|16 Kotierungsreglement der BX|Art. 16", text)[1]
    if origin == "email" or origin == "emsure" or origin == "emsure test":
        if headline in text:
            text = text.split(headline)[1]
        elif "Art. 53" in text:
            text = re.split("Art\\. 53 .R|Art\\. 53 of the Listing Rules|Art\\. 53|Article 53", text)[1]
    if len(classifier.reduce_text(text)) < 550:
        logging.warning("Release text %s too short for processing", headline[:80])
        return {"result": "Release text too short for processing"}
    # Classify
    if pubt_code == "":
        classification = classifier.classify(headline, text, False)
    else:
        classification = classifier.get_pubt_classification(pubt_code)
        # Discard PUBT documents not tagged with BRF and not sent in peak publication times
        if "PBLptg:NTG102301" not in pubt_code and not is_time_in_publication_window():
            logging.warning("PUBT doc %s discarded (missing BRF code and not in peak publication times) for %s",
                            headline[:50], isin)
            return {"result": "Document discarded"}
    if classification['label'] is None:
        logging.warning("No classification determined for %s (ISIN %s) and origin %s",
                        headline[:50], isin, origin)
        return {"result": "No classification determined"}
    # Check for company
    company = company_lookup.get_company(isin)
    if company is not None:
        if str(company['id']) == '-2147197664':
            logging.warning("no briefs for SNB BNS")
            return {"result": "no briefs for SNB BNS"}
        # Check for existing brief
        con = pool.get_connection()
        query = f"""SELECT * FROM 
                (SELECT * FROM ai_texts.briefs WHERE CAST(datetime AS DATE) = CURRENT_DATE()
                AND isin <> '' 
                AND tags = '{classification['subject_codes']}'
                AND (origin = '{origin}' OR origin <> 'emsure test')
                AND (body <> '-' OR headline LIKE 'No German Article published%')
                ) b
                JOIN (SELECT * FROM masterdata.companies  WHERE ID = '{company['id']}') c 
                ON c.ISINs LIKE CONCAT('%', b.isin, '%');"""
        prior_briefs = pd.read_sql(query, con)
        con.close()
        if len(prior_briefs) > 0:
            logging.info("Prior briefs detected for company %s and classification %s", company['name'],
                         classification['subject_codes'])
            return {"result": "Brief for this company and this topic already generated"}
        else:
            # Include headline in text sent to the AI
            text = headline + "\n\n" + text
            # Generate and publish Flashes
            publish_fl_de = publish_flash_de(text, classification, company, test)
            publish_fl_fr = publish_flash_fr(text, classification, company, True)  # Never send FrenchFlashes to prod
            # Generate and publish Brief
            publish_de = publish_brief_de(text, classification, company, test, provider, link)
            publish_fr = publish_brief_fr(text, classification, company, test, provider, link)
            date = datetime.today().strftime("%Y-%m-%d %H:%M:%S")
            brief_meta = {"filename": date + classification['label'] + company['id'], "datetime": date,
                          "link": link, "origin": origin, "tags": str(classification['subject_codes'] or ""),
                          "isin": isin, "topic": str(classification['label'] or "")}
            # Update DB
            brief_meta.update(publish_de)
            brief_meta.update(publish_fr)
            brief_meta.update(publish_fl_de)
            brief_meta.update(publish_fl_fr)
            con = pool.get_connection()
            cur = con.cursor()
            query = insert_dict("ai_texts.briefs", brief_meta)
            cur.execute(query)
            con.commit()
            con.close()
            # Return results
            return {"result_de": publish_de, "result_fr": publish_fr}
    else:
        logging.warning("No company found for isin %s", isin)
        return {"result": "No company found"}


def publish_flash_de(text: str, classification: dict, company: pd.Series, test: bool) -> Any:
    """
   Function to generate and publish German Flashes
   :param text: text of news release
   :param classification: dictionary with classification label, prompt and subject codes
   :param company: Series with company metadata
   :param test: if true use test environment
   :return: str to indicate success
   """
    prompt_id_flash = classification['prompt_id_flash_de']
    if test:
        status = "Withheld"
    else:
        status = "Withheld"
        # Flashes first
    if prompt_id_flash is None:
        return {"flashes_de": "-"}
    else:
        # Check for company specific flash prompt
        if (prompt_id_flash + company['id']) in prompt_ids:
            prompt_id_flash = prompt_id_flash + company['id']
        response = prompting.execute_prompt(prompt_id=prompt_id_flash,
                                            discord_notifications=False,
                                            company_shortname=company['name'],
                                            release_text=text)
        # Clean up answer
        json_data = textprocessing.clean_json(response)
        # Read json
        try:
            headlines = json.loads(json_data)
            headlines = headlines['AWP_Headlines']
            for headline in headlines:
                headline = "***" + textprocessing.awp_format_headline_de(headline)
                try:
                    utils.create_newsItemBW2(title=headline, text="",
                                             comp=[company['full_name']],
                                             subj=classification['subject_codes'].split(";"),
                                             path="C:\\Automatisierungen\\ai_news_api\\_output",
                                             name="ai_flash", status=status, flash=True, test=test)
                except Exception as e:
                    logging.exception(e)
            return {"flashes_de": "\n".join(map(str, headlines))}
        except json.JSONDecodeError as e:
            logging.exception(e)
            logging.error(json_data)
            return {"flashes_de": "-"}


def publish_flash_fr(text: str, classification: dict, company: pd.Series, test: bool) -> Any:
    """
   Function to generate and publish French Flashes
   :param text: text of news release
   :param classification: dictionary with classification label, prompt and subject codes
   :param company: Series with company metadata
   :param test: if true use test environment
   :return: str to indicate success
   """
    prompt_id_flash = classification['prompt_id_flash_fr']
    if test:
        status = "Withheld"
    else:
        status = "Withheld"
        # Flashes first
    if prompt_id_flash is None:
        return {"flashes_fr": "-"}
    else:
        # Check for company specific flash prompt
        if (prompt_id_flash + company['id']) in prompt_ids:
            prompt_id_flash = prompt_id_flash + company['id']
        response = prompting.execute_prompt(prompt_id=prompt_id_flash,
                                            discord_notifications=False,
                                            company_shortname=company['name'],
                                            release_text=text)
        # Clean up answer
        json_data = textprocessing.clean_json(response)
        # Read json
        try:
            headlines = json.loads(json_data)
            headlines = headlines['AWP_Headlines']
            for headline in headlines:
                headline = "***" + textprocessing.awp_format_headline_fr(headline)
                try:
                    utils.create_newsItemBW2(title=headline, text="",
                                             comp=[company['full_name']], lang="fr",
                                             subj=classification['subject_codes'].split(";"),
                                             path="C:\\Automatisierungen\\ai_news_api\\_output",
                                             name="ai_flash", status=status, flash=True, test=test)
                except Exception as e:
                    logging.exception(e)
            return {"flashes_fr": "\n".join(map(str, headlines))}
        except json.JSONDecodeError as e:
            logging.exception(e)
            logging.error(json_data)
            return {"flashes_fr": "-"}


def publish_brief_de(text: str, classification: dict, company: pd.Series, test: bool, provider="", link="") -> Any:
    """
    Function to generate and publish German Briefs
    :param text: text of news release
    :param classification: dictionary with classification label, prompt and subject codes
    :param company: Series with company metadata
    :param test: if true use test environment
    :param provider: default empty, use for wire providers like 'EQS', 'GNW', ...
    :param link: link to release if available
    :return: str to indicate success
    """
    prompt_id = classification['prompt_id_de']
    if prompt_id is None:
        return {"headline": "No German Article published for classification " + classification['label'],
                "headline_original": "-", "body": "-",
                "body_original": "-"}
    else:
        if test:
            status = "Withheld"
        else:
            status = "Withheld"
        # Check for company specific prompt
        if (prompt_id + company['id']) in prompt_ids:
            prompt_id = prompt_id + company['id']
        # Send AI request
        response = prompting.execute_prompt(prompt_id=prompt_id,
                                            discord_notifications=False,
                                            company_shortname=company['name'],
                                            company_synonyms=company['synonyme'],
                                            weekday=weekdays_de[datetime.today().weekday()],
                                            release_text=text)
        # Clean up answer
        json_data = textprocessing.clean_json(response)
        # Read json
        try:
            brief = json.loads(json_data)
        except json.JSONDecodeError as e:
            logging.exception(e)
            logging.error(json_data)
            return {"headline": "JSON-Decode error",
                    "headline_original": "-", "body": "-",
                    "body_original": "-"}
        # Process text
        text = textprocessing.awp_format_text_de(brief['AWP_Text'], number_format=True, paragraphs=True)
        text = textprocessor.add_footer_and_start_de(text, company['name'], company['place_de'], link=link,
                                                     provider=provider)
        title = textprocessing.awp_format_headline_de(brief['AWP_Titel'])
        # Add BRF tag to subjects
        subjects = classification['subject_codes'].split(";") + ['BRF']
        try:
            utils.create_newsItemBW2(title=title, text=text,
                                     comp=[company['full_name']], subj=subjects,
                                     path="C:\\Automatisierungen\\ai_news_api\\_output",
                                     name="ai_text", status=status, test=test, hint="")
        except Exception as e:
            logging.exception(e)
        return {"headline": title, "headline_original": brief['AWP_Titel'], "body": text,
                "body_original": brief['AWP_Text']}


def publish_brief_fr(text: str, classification: dict, company: pd.Series, test: bool, provider="", link="") -> Any:
    """
    Function to generate and publish French Briefs
    :param text: text of news release
    :param classification: dictionary with classification label, prompt and subject codes
    :param company: Series with company metadata
    :param test: if true use test environment
    :param provider: default empty, use for wire providers like 'EQS', 'GNW', ...
    :param link: link to release if available
    :return: str to indicate success
    """
    prompt_id = classification['prompt_id_fr']
    if prompt_id is None:
        return {"headline_fr": "No French Article published for classification " + classification['label'],
                "body_fr": "-"}
    else:
        # Check for company specific prompt
        if (prompt_id + company['id']) in prompt_ids:
            prompt_id = prompt_id + company['id']
        # Send AI request
        response = prompting.execute_prompt(prompt_id=prompt_id,
                                            discord_notifications=False,
                                            company_shortname=company['name_fr'],
                                            company_synonyms=company['synonyme_fr'],
                                            weekday=weekdays_fr[datetime.today().weekday()],
                                            release_text=text)
        # Clean up answer
        json_data = textprocessing.clean_json(response)
        # Read json
        try:
            brief = json.loads(json_data)
        except json.JSONDecodeError as e:
            logging.exception(e)
            logging.error(json_data)
            return {"headline_fr": "Json decode error",
                    "body_fr": "-"}
        if test:
            status = "Withheld"
        else:
            status = "Withheld"
        # Process text
        text = textprocessing.awp_format_text_fr(brief['AWP_Text'], number_format=True, paragraphs=True)
        text = textprocessor.add_footer_and_start_fr(text, company['name'], company['place_fr'], link=link,
                                                     provider=provider)
        title = textprocessing.awp_format_headline_fr(brief['AWP_Titel'])
        # Add BRF tag to subjects
        subjects = classification['subject_codes'].split(";") + ['BRF']
        try:
            utils.create_newsItemBW2(title=title, text=text,
                                     comp=[company['full_name']], lang="fr", subj=subjects,
                                     path="C:\\Automatisierungen\\ai_news_api\\_output",
                                     name="ai_text", status=status, test=test, hint="")
        except Exception as e:
            logging.exception(e)
        return {"headline_fr": title, "body_fr": text}


def getProviderTag(provider: str):
    match provider:
        case "Business Wire":
            return "BSW"
        case "PR Newswire":
            return "PRN"
        case "Cision":
            return "CSI"
        case "EQS":
            return "EQS"
        case "GlobeNewswire":
            return "GNW"
        case _:
            return ""
