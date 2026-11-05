# Misure master e dimensioni

Espressioni da creare come **elementi principali** (master items) nell'app Qlik Sense.
Le variabili `vSetYTD`, `vSetLYTD`, `vTolleranza…` e `vDataRif` sono definite nello script ([02_App_Vendite.qvs](../script/02_App_Vendite.qvs)).

## Vendite

| Misura | Espressione | Note |
|---|---|---|
| Fatturato | `Sum({<Fonte={'Fatturato'}>} Valore)` | Rispetta tutte le selezioni |
| Fatturato YTD | `Sum({<Fonte={'Fatturato'}, $(vSetYTD)>} Valore)` | Da inizio anno alla data di riferimento, ignora le selezioni sul calendario |
| Fatturato LYTD | `Sum({<Fonte={'Fatturato'}, $(vSetLYTD)>} Valore)` | Stesso periodo dell'anno precedente |
| Var % YTD | `[Fatturato YTD] / [Fatturato LYTD] - 1` | Riferimento a misure master |
| Fatturato anno precedente (dinamico) | `Sum({<Fonte={'Fatturato'}, Anno={$(=Max(Anno)-1)}>} Valore)` | Espansione `$(=...)`: l'anno si adatta alla selezione |
| Clienti attivi | `Count({<Fonte={'Fatturato'}, Valore={">0"}>} DISTINCT CodCliente)` | |
| Fatturato medio per cliente | `[Fatturato] / [Clienti attivi]` | |
| Incidenza % sconti e omaggi | `Sum({<Fonte={'Fatturato'}>} [Valore Sconto] + [Valore Omaggio]) / Sum({<Fonte={'Fatturato'}>} Valore + [Valore Sconto] + [Valore Omaggio])` | Sul valore a listino |

## Margini

| Misura | Espressione |
|---|---|
| Margine € | `Sum({<Fonte={'Fatturato'}>} Margine)` |
| Margine % | `Sum({<Fonte={'Fatturato'}>} Margine) / Sum({<Fonte={'Fatturato'}>} Valore)` |
| Margine % YTD | `Sum({<Fonte={'Fatturato'}, $(vSetYTD)>} Margine) / Sum({<Fonte={'Fatturato'}, $(vSetYTD)>} Valore)` |
| Delta margine % vs LYTD (punti) | `Sum({<Fonte={'Fatturato'}, $(vSetYTD)>} Margine) / Sum({<Fonte={'Fatturato'}, $(vSetYTD)>} Valore) - Sum({<Fonte={'Fatturato'}, $(vSetLYTD)>} Margine) / Sum({<Fonte={'Fatturato'}, $(vSetLYTD)>} Valore)` |

## Budget

| Misura | Espressione |
|---|---|
| Budget | `Sum({<Fonte={'Budget'}>} [Valore Budget])` |
| Budget YTD | `Sum({<Fonte={'Budget'}, $(vSetYTD)>} [Valore Budget])` |
| % raggiungimento budget YTD | `[Fatturato YTD] / [Budget YTD]` |

## Ordini e livello di servizio

| Misura | Espressione |
|---|---|
| Ordinato | `Sum({<Fonte={'Ordinato'}>} Valore)` |
| Portafoglio aperto | `Sum({<Fonte={'Ordinato'}, [Stato Riga]={'Aperta'}>} Valore)` |
| Portafoglio scaduto | `Sum({<Fonte={'Ordinato'}, [Stato Riga]={'Aperta'}, [Data Consegna Richiesta]={"<$(=Date(vDataRif))"}>} Valore)` |
| % righe puntuali | `Count({<Fonte={'Ordinato'}, [Esito Consegna]={'Puntuale'}>} DISTINCT %RigaOrdine) / Count({<Fonte={'Ordinato'}, [Stato Riga]={'Evasa'}>} DISTINCT %RigaOrdine)` |
| % righe in ritardo | `Count({<Fonte={'Ordinato'}, [Esito Consegna]={'In ritardo'}>} DISTINCT %RigaOrdine) / Count({<Fonte={'Ordinato'}, [Stato Riga]={'Evasa'}>} DISTINCT %RigaOrdine)` |
| Ritardo medio (gg) | `Avg({<Fonte={'Ordinato'}, [Esito Consegna]={'In ritardo'}>} [Giorni Ritardo])` |

## Set analysis avanzata

| Misura | Espressione | Cosa mostra |
|---|---|---|
| Clienti in calo > 20% | `Count({<CodCliente={"=Sum({<Fonte={'Fatturato'}, $(vSetYTD)>} Valore) < 0.8 * Sum({<Fonte={'Fatturato'}, $(vSetLYTD)>} Valore)"}>} DISTINCT CodCliente)` | Ricerca avanzata dentro il set |
| Clienti caffè senza dolci | `Count({<CodCliente = P({<Famiglia={'Caffè'}>} CodCliente) - P({<Famiglia={'Dolci e snack'}>} CodCliente)>} DISTINCT CodCliente)` | Opportunità di cross-selling con `P()` |
| Fatturato clienti classe A | `Sum({<Fonte={'Fatturato'}, [Classe ABC]={'A'}>} Valore)` | Usa la classificazione calcolata nello script |

## Dimensioni calcolate

| Dimensione | Espressione |
|---|---|
| Top 10 clienti + Altri | `=Aggr(If(Rank(Sum({<Fonte={'Fatturato'}>} Valore)) <= 10, Cliente, 'Altri'), Cliente)` |
| Fascia di ritardo | `=If([Giorni Ritardo] <= 0, '0. In tempo', If([Giorni Ritardo] <= 3, '1. 1-3 gg', If([Giorni Ritardo] <= 7, '2. 4-7 gg', '3. Oltre 7 gg')))` |
