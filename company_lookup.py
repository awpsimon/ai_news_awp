import pandas as pd
from db_pool import pool


def get_company(isin: str) -> pd.Series:
    """
    Function to fetch company metadata from db
    :param isin: company isin
    :return: df with company metadata full_name, name, id, place_de, place_fr, name_fr, synonyms
    """
    if isin == "":
        company = None
    else:
        db = pool.get_connection()
        sql_stmt = ("""SELECT 
            c.Name AS full_name,
            CASE
            WHEN c.Kurzname = '' THEN name
            ELSE c.Kurzname
        END name,
        c.ID AS id,
        c.Ort AS place_de,
        CASE
            WHEN NOT l.Name_f IS NULL THEN l.Name_f
            ELSE c.Ort
        END place_fr,
        CASE
            WHEN NOT f.fr_Name_kurz IS NULL THEN f.fr_Name_kurz
            ELSE c.Kurzname
        END name_fr,
        CONCAT_WS(', ', s.synonym_A, s.synonym_B, s.synonym_C) AS synonyme,
        CONCAT_WS(', ', s.synonym_A_fr, s.synonym_B_fr, s.synonym_C_fr) AS synonyme_fr
    FROM
        (SELECT 
            *
        FROM
            masterdata.companies
        WHERE
            ISINs LIKE '%""" + isin + """%') c
            LEFT JOIN
        dictionaries.companies_differentnames f ON c.ID = f.company_ID
            LEFT JOIN
        (SELECT 
            Name_d, Name_f
        FROM
            masterdata.locations) l ON c.Ort = l.Name_d
            LEFT JOIN
            (SELECT ID, synonym_A, synonym_B, synonym_C, synonym_A_fr, synonym_B_fr, synonym_C_fr FROM
        masterdata.companies_synonyms) s ON s.ID = c.ID;""")
        company_df = pd.read_sql(sql_stmt, db)
        db.close()
        company = None
        if len(company_df) > 0:
            company = company_df.iloc[0]
    return company
