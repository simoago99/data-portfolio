/* =============================================================================
   Viste per il modello "Pipeline commerciale".
   Dialetto: T-SQL. Schema generico e inventato:
     crm.OPPORTUNITA       trattative del CRM
     crm.STATI_OPPORTUNITA decodifica degli stati
     erp.ORDINI_CLIENTE    ordini confermati (collegati alla trattativa)
     erp.FATTURE_RIGHE     righe fatturate (collegate all'ordine)
   ============================================================================= */

-- -----------------------------------------------------------------------------
-- Trattative con stato normalizzato e motivo di perdita
-- -----------------------------------------------------------------------------
CREATE OR ALTER VIEW bi.vw_trattative AS
SELECT
    o.ID_OPPORTUNITA                                    AS [ID Trattativa],
    CAST(o.DATA_CREAZIONE AS date)                      AS [Data Apertura],
    CAST(o.DATA_CHIUSURA AS date)                       AS [Data Chiusura],
    CASE s.CATEGORIA
        WHEN 'WON'  THEN 'Vinta'
        WHEN 'LOST' THEN 'Persa'
        WHEN 'NEGO' THEN 'In negoziazione'
        ELSE 'Aperta'
    END                                                 AS [Stato],
    CASE WHEN s.CATEGORIA = 'LOST' THEN COALESCE(o.MOTIVO_PERDITA, 'Non indicato') END AS [Motivo Perdita],
    o.COD_CLIENTE                                       AS [Codice Cliente],
    o.COD_COMMERCIALE                                   AS [Codice Commerciale],
    o.LINEA_PRODOTTO                                    AS [Linea Prodotto],
    CASE WHEN o.FLAG_CANONE = 1 THEN 'Ricorrente' ELSE 'One-off' END AS [Tipo Ricavo],
    o.VALORE_STIMATO                                    AS [Valore]
FROM crm.OPPORTUNITA AS o
JOIN crm.STATI_OPPORTUNITA AS s
    ON s.COD_STATO = o.COD_STATO
WHERE o.FLAG_TEST = 0;
GO

-- -----------------------------------------------------------------------------
-- Backlog per ordine: ordinato meno fatturato, con percentuale di avanzamento
-- -----------------------------------------------------------------------------
CREATE OR ALTER VIEW bi.vw_backlog_ordini AS
WITH fatturato AS (
    SELECT NUMERO_ORDINE, SUM(IMPORTO) AS FATTURATO, MAX(DATA_FATTURA) AS ULTIMA_FATTURA
    FROM erp.FATTURE_RIGHE
    GROUP BY NUMERO_ORDINE
)
SELECT
    oc.NUMERO_ORDINE                                    AS [Numero Ordine],
    oc.COD_CLIENTE                                      AS [Codice Cliente],
    oc.LINEA_PRODOTTO                                   AS [Linea Prodotto],
    oc.VALORE_ORDINE                                    AS [Valore Ordine],
    COALESCE(f.FATTURATO, 0)                            AS [Fatturato],
    oc.VALORE_ORDINE - COALESCE(f.FATTURATO, 0)         AS [Backlog],
    COALESCE(f.FATTURATO, 0) / NULLIF(oc.VALORE_ORDINE, 0) AS [% Avanzamento],
    f.ULTIMA_FATTURA                                    AS [Ultima Fattura]
FROM erp.ORDINI_CLIENTE AS oc
LEFT JOIN fatturato AS f
    ON f.NUMERO_ORDINE = oc.NUMERO_ORDINE
WHERE oc.STATO <> 'ANNULLATO';
GO

/* -----------------------------------------------------------------------------
   Win rate trimestrale per commerciale e confronto con la media del team
   ----------------------------------------------------------------------------- */
WITH chiuse AS (
    SELECT
        [Codice Commerciale]                                       AS commerciale,
        DATEFROMPARTS(YEAR([Data Chiusura]), (DATEPART(QUARTER, [Data Chiusura]) - 1) * 3 + 1, 1) AS trimestre,
        SUM(CASE WHEN [Stato] = 'Vinta' THEN [Valore] ELSE 0 END)  AS valore_vinto,
        SUM([Valore])                                              AS valore_chiuso
    FROM bi.vw_trattative
    WHERE [Stato] IN ('Vinta', 'Persa')
    GROUP BY [Codice Commerciale],
             DATEFROMPARTS(YEAR([Data Chiusura]), (DATEPART(QUARTER, [Data Chiusura]) - 1) * 3 + 1, 1)
)
SELECT
    commerciale,
    trimestre,
    valore_vinto / NULLIF(valore_chiuso, 0)                                         AS win_rate,
    SUM(valore_vinto) OVER (PARTITION BY trimestre)
        / NULLIF(SUM(valore_chiuso) OVER (PARTITION BY trimestre), 0)               AS win_rate_team,
    AVG(valore_vinto / NULLIF(valore_chiuso, 0)) OVER (
        PARTITION BY commerciale ORDER BY trimestre ROWS BETWEEN 3 PRECEDING AND CURRENT ROW) AS win_rate_media_mobile_4t
FROM chiuse
ORDER BY commerciale, trimestre;

/* -----------------------------------------------------------------------------
   Imbuto: dalla trattativa all'ordine e alla prima fattura, per anno di apertura
   ----------------------------------------------------------------------------- */
SELECT
    YEAR(t.[Data Apertura])                                        AS anno,
    COUNT(*)                                                       AS trattative,
    COUNT(CASE WHEN t.[Stato] IN ('Vinta', 'Persa') THEN 1 END)    AS chiuse,
    COUNT(oc.NUMERO_ORDINE)                                        AS con_ordine,
    COUNT(b.[Ultima Fattura])                                      AS con_fattura,
    AVG(CASE WHEN oc.NUMERO_ORDINE IS NOT NULL
             THEN DATEDIFF(DAY, t.[Data Apertura], b.[Ultima Fattura]) END) AS giorni_medi_apertura_fattura
FROM bi.vw_trattative AS t
LEFT JOIN erp.ORDINI_CLIENTE AS oc   ON oc.ID_OPPORTUNITA = t.[ID Trattativa]
LEFT JOIN bi.vw_backlog_ordini AS b  ON b.[Numero Ordine] = oc.NUMERO_ORDINE
GROUP BY YEAR(t.[Data Apertura])
ORDER BY anno;
