from publisher import publish_brief

from awptools import prompting
from awptools import utils
import classifier
import json
import textprocessor
import company_lookup

## Load prompts
db = utils.connect_db("ai_texts")
sql_stmt = "SELECT id FROM ai_texts.prompts;"
cursor = db.cursor()
cursor.execute(sql_stmt)
prompt_ids = cursor.fetchall()
db.close()

company = company_lookup.get_company("CH0127480363")
prompt = "prompt1" + company['id']
if prompt in prompt_ids:
    print("success")

print(publish_brief(headline="LUKB: Wahl von Bernadette Koch in den Verwaltungsrat geplant",
                    text="Luzern, 28. November 2025 – Der Verwaltungsrat der Luzerner Kantonalbank AG (LUKB) "
                         "beantragt an der Generalversammlung vom 13. April 2026 die Wahl von Bernadette Koch als "
                         "neues Mitglied des Verwaltungsrates. Die eidg. dipl. Wirtschaftsprüferin aus dem "
                         "luzernischen Oberkirch ist eine erfahrene Verwaltungsrätin und ehemalige Partnerin bei der "
                         "Ernst & Young AG (EY). Mit der Nomination von Bernadette Koch stärkt die LUKB ihren "
                         "Verwaltungsrat mit einer erfahrenen Persönlichkeit aus dem Bereich Audit. Nach erfolgter "
                         "Wahl von Bernadette Koch wird der LUKB-Verwaltungsrat aus neun Personen bestehen und einen "
                         "Frauenanteil von 44 % aufweisen. Die Luzerner Kantonalbank AG (LUKB) überprüft regelmässig "
                         "das Kompetenzenprofil ihres Verwal-tungsrats. Ziel ist es, das oberste Organ der Bank "
                         "vorausschauend mit den passenden Kompetenzen auszustatten. Im Hinblick auf die zunehmenden "
                         "regulatorischen Anforderungen schlägt der Verwaltungsrat eine Erweiterung des Gremiums um "
                         "ein starkes Audit-Profil vor. Das Gremium hat Bernadette Koch (Jahrgang 1968) als neues "
                         "Mitglied des Verwaltungsrates nominiert. Optimales Kompetenzenprofil und enge "
                         "Verbundenheit mit dem Kanton Luzern Bernadette Koch ist im Kanton Luzern geboren und "
                         "aufgewachsen und lebt seit vielen Jahren in der Luzerner Gemeinde Oberkirch. Mit den "
                         "wirtschaftlichen und politischen Verhältnissen im Wirtschaftraum Luzern ist sie bestens "
                         "vertraut. Die eidg. dipl. Wirtschaftsprüferin verfügt über ein CAS in Sustainable Finance "
                         "und ist seit 2018 als professionelle Verwaltungsrätin tätig: Aktuell nimmt sie VR-Mandate "
                         "wahr bei der Schweizerischen Post AG (Vizepräsidentin) und deren Tochtergesellschaft "
                         "Postfinance AG, Mobimo Holding AG, Geberit AG und Energie Oberkirch AG. Zuvor war "
                         "Bernadette Koch 25 Jahre im Audit bei Ernst & Young AG tätig, davon zehn Jahre als Leitende "
                         "Prüferin und Partnerin. Mit Blick auf die Nomination zur Wahl in den LUKB-Verwaltungsrat "
                         "wird Bernadette Koch ihr Verwaltungsratsmandat bei der Postfinance AG sowie den Vorsitz des "
                         "Verwaltungsratsausschusses Audit, Risk & Compliance (Kompetenzgremium für "
                         "Postfinance-Themen) bei der Schweizerischen Post AG auf Ende März 2026 niederlegen. Die "
                         "Wahl von Bernadette Koch in den LUKB-Verwaltungsrat wird der Generalversammlung vom 13. "
                         "April 2026 beantragt. Bei Annahme der Wahl wird sich der Verwaltungsrat der LUKB neu aus "
                         "neun Mitgliedern konstituieren und einen Frauenanteil von 44 % aufweisen. Gemäss den "
                         "Statuten der LUKB muss der Verwaltungsrat sieben bis neun Mitglieder umfassen. Die "
                         "Eignerstrategie 2025 gibt vor, dass beide Geschlechter mindestens zu je 30 % im "
                         "Verwaltungsrat der LUKB vertreten sind. Zusatzinformationen und Bildmaterial",
                    isin="CH1252930610",
                    test=True))
