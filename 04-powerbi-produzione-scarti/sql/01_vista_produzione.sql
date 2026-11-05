/* =============================================================================
   Vista per il modello "Reparto produzione: scarti e produttività".
   Dialetto: T-SQL. Schema generico e inventato:
     mes.DICHIARAZIONI         dichiarazioni di produzione a fine turno (testata)
     mes.DICHIARAZIONI_RIGHE   quantità dichiarate per tipo
     mes.CONSUMI               materiali consumati per dichiarazione
     mes.TIPI_MOVIMENTO        classificazione dei movimenti (prodotto, scarto, rifilo)
   ============================================================================= */
CREATE OR ALTER VIEW bi.vw_produzione AS
WITH movimenti AS (
    -- una riga per dichiarazione, con i chili separati per tipo (pivot con SUM CASE)
    SELECT
        d.ID_DICHIARAZIONE,
        SUM(CASE WHEN tm.CLASSE = 'PRODOTTO' THEN d.QTA_KG ELSE 0 END) AS PRODUZIONE_KG,
        SUM(CASE WHEN tm.CLASSE = 'SCARTO'   THEN d.QTA_KG ELSE 0 END) AS SCARTO_KG,
        SUM(CASE WHEN tm.CLASSE = 'RIFILO'   THEN d.QTA_KG ELSE 0 END) AS RIFILI_KG,
        SUM(CASE WHEN tm.CLASSE = 'PRODOTTO' THEN d.QTA_M2 ELSE 0 END) AS METRI_QUADRI,
        SUM(CASE WHEN tm.CLASSE = 'PRODOTTO' THEN d.NUM_BOBINE ELSE 0 END) AS BOBINE_OK
    FROM mes.DICHIARAZIONI_RIGHE AS d
    JOIN mes.TIPI_MOVIMENTO AS tm ON tm.COD_TIPO = d.COD_TIPO
    GROUP BY d.ID_DICHIARAZIONE
),
consumi AS (
    SELECT ID_DICHIARAZIONE, SUM(QTA_KG) AS CONSUMO_KG
    FROM mes.CONSUMI
    GROUP BY ID_DICHIARAZIONE
)
SELECT
    CAST(t.DATA_TURNO AS date)                         AS [Data],
    t.ORDINE_PRODUZIONE                                AS [Ordine Produzione],
    t.LINEA                                            AS [Linea],
    t.TURNO                                            AS [Turno],
    t.COD_ARTICOLO                                     AS [Codice Articolo],
    DATEDIFF(MINUTE, t.INIZIO, t.FINE) / 60.0          AS [Ore Lavorate],
    c.CONSUMO_KG                                       AS [Consumo Kg],
    m.PRODUZIONE_KG                                    AS [Produzione Kg],
    m.SCARTO_KG                                        AS [Scarto Kg],
    m.RIFILI_KG                                        AS [Rifili Kg],
    m.METRI_QUADRI                                     AS [Metri Quadri],
    m.BOBINE_OK                                        AS [Bobine OK]
FROM mes.DICHIARAZIONI AS t
JOIN movimenti AS m     ON m.ID_DICHIARAZIONE = t.ID_DICHIARAZIONE
LEFT JOIN consumi AS c  ON c.ID_DICHIARAZIONE = t.ID_DICHIARAZIONE
WHERE t.STATO = 'CONFERMATA';
GO

/* -----------------------------------------------------------------------------
   % scarto settimanale per linea, media mobile su 4 settimane
   e posizione della linea nella settimana (1 = scarto più basso)
   ----------------------------------------------------------------------------- */
WITH settimanale AS (
    SELECT
        [Linea]                                                     AS linea,
        DATEADD(DAY, 1 - DATEPART(WEEKDAY, [Data]), [Data])         AS inizio_settimana,
        SUM([Scarto Kg])                                            AS scarto_kg,
        SUM([Consumo Kg])                                           AS consumo_kg
    FROM bi.vw_produzione
    GROUP BY [Linea], DATEADD(DAY, 1 - DATEPART(WEEKDAY, [Data]), [Data])
)
SELECT
    linea,
    inizio_settimana,
    scarto_kg / NULLIF(consumo_kg, 0)                                                     AS perc_scarto,
    SUM(scarto_kg) OVER (PARTITION BY linea ORDER BY inizio_settimana ROWS BETWEEN 3 PRECEDING AND CURRENT ROW)
      / NULLIF(SUM(consumo_kg) OVER (PARTITION BY linea ORDER BY inizio_settimana ROWS BETWEEN 3 PRECEDING AND CURRENT ROW), 0)
                                                                                          AS perc_scarto_mobile_4s,
    RANK() OVER (PARTITION BY inizio_settimana ORDER BY scarto_kg / NULLIF(consumo_kg, 0)) AS posizione
FROM settimanale
ORDER BY inizio_settimana, posizione;
