/* =============================================================================
   Vista dei carichi di magazzino per il modello "Analisi acquisti".
   Dialetto: T-SQL. Schema del gestionale generico e inventato:
     erp.MOV_MAGAZZINO      movimenti di magazzino
     erp.CAUSALI_MAG        causali (carico da fornitore, carico interno, reso...)
     erp.LISTINI_FORNITORE  prezzi di listino con periodo di validità
   ============================================================================= */
CREATE OR ALTER VIEW bi.vw_acquisti AS
WITH carichi AS (
    SELECT
        m.ID_MOVIMENTO,
        CAST(m.DATA_MOVIMENTO AS date)              AS DATA_DOC,
        NULLIF(LTRIM(RTRIM(m.NUMERO_DOC_ESTERNO)), '') AS NUMERO_DOC,
        c.DESCRIZIONE                               AS TIPO_MOVIMENTO,
        m.COD_FORNITORE,
        m.COD_ARTICOLO,
        m.QUANTITA * c.SEGNO                        AS QUANTITA,          -- i resi a fornitore hanno segno negativo
        m.VALORE_TOTALE * c.SEGNO                   AS COSTO_TOTALE
    FROM erp.MOV_MAGAZZINO AS m
    JOIN erp.CAUSALI_MAG AS c
        ON c.COD_CAUSALE = m.COD_CAUSALE
    WHERE c.TIPO = 'CARICO'
),
listino AS (
    -- per ogni carico prende il listino valido alla data del movimento;
    -- se ce ne sono più di uno, vince il più recente
    SELECT
        k.ID_MOVIMENTO,
        l.PREZZO,
        ROW_NUMBER() OVER (PARTITION BY k.ID_MOVIMENTO ORDER BY l.DATA_INIZIO_VALIDITA DESC) AS rn
    FROM carichi AS k
    JOIN erp.LISTINI_FORNITORE AS l
        ON  l.COD_FORNITORE = k.COD_FORNITORE
        AND l.COD_ARTICOLO  = k.COD_ARTICOLO
        AND k.DATA_DOC BETWEEN l.DATA_INIZIO_VALIDITA AND COALESCE(l.DATA_FINE_VALIDITA, '9999-12-31')
)
SELECT
    k.DATA_DOC                                       AS [Data Documento],
    k.NUMERO_DOC                                     AS [Numero Documento],
    k.TIPO_MOVIMENTO                                 AS [Tipo Movimento],
    k.COD_FORNITORE                                  AS [Codice Fornitore],
    k.COD_ARTICOLO                                   AS [Codice Articolo],
    k.QUANTITA                                       AS [Quantita],
    k.COSTO_TOTALE                                   AS [Costo Totale],
    k.QUANTITA * l.PREZZO                            AS [Listino Totale]  -- NULL se manca il listino: lo segnala il report
FROM carichi AS k
LEFT JOIN listino AS l
    ON l.ID_MOVIMENTO = k.ID_MOVIMENTO
   AND l.rn = 1;
GO

/* -----------------------------------------------------------------------------
   Controllo qualità: articoli caricati senza listino valido negli ultimi 90 giorni
   ----------------------------------------------------------------------------- */
SELECT
    a.[Codice Articolo],
    COUNT(*)                     AS righe_senza_listino,
    SUM(a.[Costo Totale])        AS costo_coinvolto,
    MAX(a.[Data Documento])      AS ultimo_carico
FROM bi.vw_acquisti AS a
WHERE a.[Listino Totale] IS NULL
  AND a.[Data Documento] >= DATEADD(DAY, -90, (SELECT MAX([Data Documento]) FROM bi.vw_acquisti))
GROUP BY a.[Codice Articolo]
ORDER BY costo_coinvolto DESC;

/* -----------------------------------------------------------------------------
   Variazione del prezzo medio di carico per articolo, anno su anno
   ----------------------------------------------------------------------------- */
WITH prezzi AS (
    SELECT
        [Codice Articolo]                                 AS cod_articolo,
        YEAR([Data Documento])                            AS anno,
        SUM([Costo Totale]) / NULLIF(SUM([Quantita]), 0)  AS prezzo_medio
    FROM bi.vw_acquisti
    GROUP BY [Codice Articolo], YEAR([Data Documento])
)
SELECT
    cod_articolo,
    anno,
    prezzo_medio,
    LAG(prezzo_medio) OVER (PARTITION BY cod_articolo ORDER BY anno)                 AS prezzo_medio_ap,
    prezzo_medio / NULLIF(LAG(prezzo_medio) OVER (PARTITION BY cod_articolo ORDER BY anno), 0) - 1 AS var_perc
FROM prezzi
ORDER BY cod_articolo, anno;
