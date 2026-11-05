# Data & BI Portfolio – Simone Agostini

Data Analyst e BI Developer, laureato in Statistica all'Università di Milano-Bicocca. Lavoro ogni giorno con **SQL**, **Power BI** e **Qlik Sense**: porto i dati dal gestionale alla dashboard e trasformo le richieste dei clienti in KPI e report. Uso anche Excel avanzato e Python per l'analisi dei dati.

Questo repository raccoglie progetti ricostruiti in forma generica a partire da casi reali (vendite e crediti, acquisti, pipeline commerciale, produzione), più un report Excel sugli stessi dati.

> **Nota sui dati.** Tutti i dati sono inventati e generati con [uno script Python](strumenti/genera_dati.py). I progetti riprendono tecniche e problemi affrontati nel lavoro, ma non contengono dati, nomi, codice o logiche proprietarie di aziende clienti.

## Progetti

| # | Progetto | Strumenti | In evidenza |
|---|---|---|---|
| 01 | [Analisi vendite e crediti](01-powerbi-vendite-crediti) | Power BI, DAX, SQL | Periodo dinamico vs anno precedente, ABC clienti, DSO e scaduto, clienti nuovi e persi |
| 02 | [Analisi acquisti e ABC](02-powerbi-acquisti-abc) | Power BI, DAX, SQL | Inflazione dei prezzi di carico, ABC su tre livelli, controlli sul listino |
| 03 | [Pipeline commerciale](03-powerbi-pipeline-commerciale) | Power BI, DAX, SQL | Win rate con relazioni inattive, backlog, budget e forecast, selettore di misura |
| 04 | [Produzione: scarti e produttività](04-powerbi-produzione-scarti) | Power BI, DAX, SQL | KPI di reparto, target parametrico, scarto oltre target per linea |
| 05 | [Vendite e margini in Qlik](05-qlik-vendite-margini) | Qlik Sense, script, set analysis | Architettura a due livelli con QVD, ABC nello script, livello di servizio |
| 06 | [Report vendite interattivo](06-excel-report-vendite) | Excel | Filtri a tendina, SOMMA.PIÙ.SE, intervalli dinamici, classifica con INDICE/CONFRONTA, grafico collegato |

## Competenze mostrate

- **SQL**: viste per il modello dati, CTE, funzioni finestra (`ROW_NUMBER`, `RANK`, `LAG`, `SUM() OVER` con frame), pivot con `CASE`, controlli di qualità del dato
- **Power BI**: modellazione a stella, DAX avanzato (time intelligence personalizzata, `USERELATIONSHIP`, tabelle virtuali, ABC dinamica, parametri), report in formato PBIP/PBIR versionabile su Git
- **Qlik Sense**: script di caricamento a livelli, QVD, mapping, calendario master, set analysis con ricerche avanzate e funzioni `P()`
- **Python**: generazione di dataset realistici con pandas e numpy
- **Excel**: report interattivi solo con formule (SOMMA.PIÙ.SE, MAX.PIÙ.SE, INDICE/CONFRONTA, intervalli dinamici), convalida dati e formattazione condizionale
- **Statistica e analisi**: Pareto/ABC, confronti anno su anno, indicatori finanziari (DSO) e di produzione

## Come è organizzato

I progetti 01–04 sono salvati in formato **PBIP**: il modello semantico è in TMDL e il report in PBIR. Sono file di testo, quindi su GitHub si leggono misure, relazioni e query senza installare nulla. Per aprirli serve Power BI Desktop: le istruzioni sono nel README di ogni progetto.

```
data-portfolio/
├── 01-powerbi-vendite-crediti/
├── 02-powerbi-acquisti-abc/
├── 03-powerbi-pipeline-commerciale/
├── 04-powerbi-produzione-scarti/
├── 05-qlik-vendite-margini/
├── 06-excel-report-vendite/
└── strumenti/genera_dati.py
```

## Come è stato costruito

Uso l'intelligenza artificiale (Claude, Claude Code) come strumento di lavoro quotidiano: per scrivere e rivedere SQL, DAX e script Qlik, generare dati di test e documentare. Ho realizzato anche server MCP che collegano un assistente AI ai database, per interrogare i dati e generare script di analisi.

## Contatti

[LinkedIn](https://www.linkedin.com/in/simoneagostini-)
