/* =============================================================================
   Viste che alimentano il modello Power BI "Analisi vendite e crediti".
   Dialetto: T-SQL (SQL Server). Lo schema del gestionale è generico e inventato:
     erp.DOC_TESTATE   testate dei documenti di vendita
     erp.DOC_RIGHE     righe dei documenti
     erp.CLIENTI, erp.ZONE, erp.ARTICOLI, erp.AGENTI, erp.FORNITORI
     erp.SCADENZE      rate da incassare
     erp.INCASSI       pagamenti ricevuti (anche parziali)
   ============================================================================= */

-- -----------------------------------------------------------------------------
-- Righe di fattura: fatture e note di credito (con segno negativo),
-- separazione tra merce venduta, sconti e omaggi.
-- -----------------------------------------------------------------------------
CREATE OR ALTER VIEW bi.vw_fatture_righe AS
WITH documenti AS (
    SELECT
        t.ID_DOCUMENTO,
        t.NUMERO_DOC,
        t.DATA_DOC,
        t.COD_CLIENTE,
        t.COD_AGENTE,
        CASE t.TIPO_DOC WHEN 'NC' THEN -1 ELSE 1 END          AS SEGNO
    FROM erp.DOC_TESTATE AS t
    WHERE t.TIPO_DOC IN ('FT', 'FD', 'NC')                    -- fattura, fattura differita, nota di credito
      AND t.STATO <> 'ANNULLATO'
)
SELECT
    d.NUMERO_DOC                                               AS [Numero Fattura],
    CAST(d.DATA_DOC AS date)                                   AS [Data Fattura],
    d.COD_CLIENTE                                              AS [Codice Cliente],
    d.COD_AGENTE                                               AS [Codice Agente],
    r.COD_ARTICOLO                                             AS [Codice Articolo],
    d.SEGNO * r.QUANTITA                                       AS [Quantita],
    r.PREZZO_LISTINO                                           AS [Prezzo Listino],
    COALESCE(r.PERC_SCONTO, 0)                                 AS [Sconto %],
    CASE WHEN r.FLAG_OMAGGIO = 1 THEN 0
         ELSE d.SEGNO * r.IMPORTO_NETTO END                    AS [Imponibile],
    CASE WHEN r.FLAG_OMAGGIO = 1 THEN d.SEGNO * r.QUANTITA * r.PREZZO_LISTINO
         ELSE 0 END                                            AS [Valore Omaggio]
FROM documenti AS d
JOIN erp.DOC_RIGHE AS r
    ON r.ID_DOCUMENTO = d.ID_DOCUMENTO
WHERE r.TIPO_RIGA = 'ARTICOLO';                                -- esclude righe descrittive e spese
GO

-- -----------------------------------------------------------------------------
-- Clienti con data di acquisizione = data della prima fattura.
-- -----------------------------------------------------------------------------
CREATE OR ALTER VIEW bi.vw_clienti AS
WITH prima_fattura AS (
    SELECT COD_CLIENTE, MIN(DATA_DOC) AS DATA_PRIMA_FATTURA
    FROM erp.DOC_TESTATE
    WHERE TIPO_DOC IN ('FT', 'FD') AND STATO <> 'ANNULLATO'
    GROUP BY COD_CLIENTE
)
SELECT
    c.COD_CLIENTE                                              AS [Codice Cliente],
    c.RAGIONE_SOCIALE                                          AS [Ragione Sociale],
    c.PROVINCIA                                                AS [Provincia],
    z.DESCRIZIONE_ZONA                                         AS [Zona],
    c.CANALE                                                   AS [Canale],
    c.COD_AGENTE                                               AS [Codice Agente],
    CAST(pf.DATA_PRIMA_FATTURA AS date)                        AS [Data Acquisizione],
    c.GIORNI_PAGAMENTO                                         AS [Giorni Pagamento]
FROM erp.CLIENTI AS c
LEFT JOIN erp.ZONE AS z          ON z.COD_ZONA = c.COD_ZONA
LEFT JOIN prima_fattura AS pf    ON pf.COD_CLIENTE = c.COD_CLIENTE
WHERE c.FLAG_ANNULLATO = 0;
GO

-- -----------------------------------------------------------------------------
-- Scadenze: importo, data dell'ultimo incasso e stato della rata.
-- Una rata è pagata quando la somma degli incassi copre l'importo.
-- -----------------------------------------------------------------------------
CREATE OR ALTER VIEW bi.vw_scadenze AS
WITH incassi AS (
    SELECT
        i.ID_SCADENZA,
        SUM(i.IMPORTO)                                         AS IMPORTO_INCASSATO,
        MAX(i.DATA_INCASSO)                                    AS DATA_ULTIMO_INCASSO
    FROM erp.INCASSI AS i
    GROUP BY i.ID_SCADENZA
)
SELECT
    t.NUMERO_DOC                                               AS [Numero Fattura],
    s.COD_CLIENTE                                              AS [Codice Cliente],
    CAST(t.DATA_DOC AS date)                                   AS [Data Fattura],
    CAST(s.DATA_SCADENZA AS date)                              AS [Data Scadenza],
    s.IMPORTO                                                  AS [Importo],
    -- confronto arrotondato ai centesimi: evita che acconto + saldo risultino
    -- "quasi" uguali all'importo per errori di arrotondamento
    CASE WHEN ROUND(COALESCE(i.IMPORTO_INCASSATO, 0), 2) >= ROUND(s.IMPORTO, 2)
         THEN CAST(i.DATA_ULTIMO_INCASSO AS date) END          AS [Data Pagamento]
FROM erp.SCADENZE AS s
JOIN erp.DOC_TESTATE AS t   ON t.ID_DOCUMENTO = s.ID_DOCUMENTO
LEFT JOIN incassi AS i      ON i.ID_SCADENZA = s.ID_SCADENZA;
GO
