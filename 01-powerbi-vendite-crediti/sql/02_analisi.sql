/* =============================================================================
   Query di analisi sulle viste del modello: le stesse logiche del report,
   scritte in SQL con CTE e funzioni finestra.
   ============================================================================= */

-- -----------------------------------------------------------------------------
-- 1. Fatturato mensile, confronto con lo stesso mese dell'anno precedente
--    e progressivo da inizio anno (LAG + SUM OVER).
--    LAG su 12 righe presuppone che nella serie siano presenti tutti i mesi.
-- -----------------------------------------------------------------------------
WITH mensile AS (
    SELECT
        YEAR([Data Fattura])                       AS anno,
        MONTH([Data Fattura])                      AS mese,
        SUM([Imponibile])                          AS fatturato
    FROM bi.vw_fatture_righe
    GROUP BY YEAR([Data Fattura]), MONTH([Data Fattura])
)
SELECT
    anno,
    mese,
    fatturato,
    LAG(fatturato, 12) OVER (ORDER BY anno, mese)                          AS fatturato_ap,
    fatturato / NULLIF(LAG(fatturato, 12) OVER (ORDER BY anno, mese), 0) - 1 AS var_perc_ap,
    SUM(fatturato) OVER (PARTITION BY anno ORDER BY mese
                         ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW)  AS fatturato_ytd
FROM mensile
ORDER BY anno, mese;

-- -----------------------------------------------------------------------------
-- 2. Classificazione ABC dei clienti per anno (curva di Pareto).
-- -----------------------------------------------------------------------------
WITH per_cliente AS (
    SELECT
        YEAR(f.[Data Fattura])                     AS anno,
        f.[Codice Cliente]                         AS cod_cliente,
        SUM(f.[Imponibile])                        AS fatturato
    FROM bi.vw_fatture_righe AS f
    GROUP BY YEAR(f.[Data Fattura]), f.[Codice Cliente]
    HAVING SUM(f.[Imponibile]) > 0
),
cumulato AS (
    SELECT
        anno,
        cod_cliente,
        fatturato,
        SUM(fatturato) OVER (PARTITION BY anno ORDER BY fatturato DESC, cod_cliente
                             ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW)
            / SUM(fatturato) OVER (PARTITION BY anno)                       AS quota_cumulata,
        DENSE_RANK() OVER (PARTITION BY anno ORDER BY fatturato DESC)        AS posizione
    FROM per_cliente
)
SELECT
    anno,
    posizione,
    cod_cliente,
    fatturato,
    quota_cumulata,
    CASE WHEN quota_cumulata <= 0.80 THEN 'A'
         WHEN quota_cumulata <= 0.95 THEN 'B'
         ELSE 'C' END                                                       AS classe_abc
FROM cumulato
ORDER BY anno, posizione;

-- -----------------------------------------------------------------------------
-- 3. Esposizione per cliente con fasce di scaduto (aging) alla data di riferimento.
-- -----------------------------------------------------------------------------
DECLARE @DataRif date = (SELECT MAX([Data Fattura]) FROM bi.vw_fatture_righe);

WITH aperte AS (
    SELECT
        s.[Codice Cliente]                         AS cod_cliente,
        s.[Importo]                                AS importo,
        DATEDIFF(DAY, s.[Data Scadenza], @DataRif) AS giorni_scaduto
    FROM bi.vw_scadenze AS s
    WHERE s.[Data Pagamento] IS NULL
)
SELECT
    c.[Ragione Sociale],
    SUM(a.importo)                                                         AS credito_aperto,
    SUM(CASE WHEN a.giorni_scaduto <= 0 THEN a.importo ELSE 0 END)         AS a_scadere,
    SUM(CASE WHEN a.giorni_scaduto BETWEEN 1 AND 30 THEN a.importo ELSE 0 END)  AS scaduto_1_30,
    SUM(CASE WHEN a.giorni_scaduto BETWEEN 31 AND 90 THEN a.importo ELSE 0 END) AS scaduto_31_90,
    SUM(CASE WHEN a.giorni_scaduto > 90 THEN a.importo ELSE 0 END)         AS scaduto_oltre_90
FROM aperte AS a
JOIN bi.vw_clienti AS c ON c.[Codice Cliente] = a.cod_cliente
GROUP BY c.[Ragione Sociale]
HAVING SUM(CASE WHEN a.giorni_scaduto > 0 THEN a.importo ELSE 0 END) > 0
ORDER BY scaduto_oltre_90 DESC, credito_aperto DESC;
