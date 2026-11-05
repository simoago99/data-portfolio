"""
Genera i dati di esempio (inventati) usati dai progetti del portfolio.

Tutti i nomi, i codici e gli importi sono casuali: il seed fisso rende
i file riproducibili. I dati simulano stagionalità, crescita annua,
clienti con peso diverso (distribuzione log-normale), ritardi di pagamento,
trattative vinte e perse, scarti di produzione in miglioramento.

Uso:  python strumenti/genera_dati.py
Richiede: pandas, numpy
"""
import os
from pathlib import Path

import numpy as np
import pandas as pd
RNG = np.random.default_rng(42)
START, END = pd.Timestamp('2023-01-01'), pd.Timestamp('2026-09-30')
PROVINCE = [('Milano','Nord-Ovest'),('Varese','Nord-Ovest'),('Como','Nord-Ovest'),('Torino','Nord-Ovest'),('Novara','Nord-Ovest'),('Bergamo','Nord-Ovest'),('Brescia','Nord-Ovest'),('Genova','Nord-Ovest'),
            ('Verona','Nord-Est'),('Padova','Nord-Est'),('Bologna','Nord-Est'),('Treviso','Nord-Est'),('Trento','Nord-Est'),
            ('Firenze','Centro'),('Roma','Centro'),('Perugia','Centro'),('Ancona','Centro'),
            ('Napoli','Sud e Isole'),('Bari','Sud e Isole'),('Palermo','Sud e Isole'),('Cagliari','Sud e Isole')]
PREF = ['Market','Bar','Ristorante','Pasticceria','Gastronomia','Hotel','Bottega','Caffè','Trattoria','Minimarket','Pizzeria','Enoteca']
NOMI = ['Aurora','Belvedere','Centrale','del Borgo','Girasole','Il Portico','La Piazzetta','Le Querce','Miramonti','Primavera','Del Sole','Stella','Vittoria','Riviera','Corte Antica','Ai Pini','Due Torri','La Fontana','Il Faro','Mille Gusti','San Marco','Al Ponte','Il Glicine','Bellavista']
NOMI_EXTRA = ['Al Castello','Arcobaleno','Belsito','Del Corso','Dolce Vita','Fiordaliso','Il Mulino','La Rotonda','Le Rondini','Primo Sole','Quattro Venti','San Giorgio','Sette Colli','Terrazza','Vecchia Stazione','Villa Rosa']
NOMI_PERS = ['Marco','Giulia','Luca','Sara','Paolo','Elena','Andrea','Chiara','Davide','Francesca','Matteo','Laura']
COGN = ['Rossi','Bianchi','Ferrari','Colombo','Ricci','Marino','Greco','Bruno','Galli','Conti','Costa','Fontana']
def nomi_aziende(n, suffissi=('Srl','Snc','Sas','Srl','Spa')):
    """Nomi di fantasia unici: se la combinazione è già usata, prende la prossima libera."""
    combinazioni=[f"{p} {q}" for q in NOMI + NOMI_EXTRA for p in PREF]
    out=set(); res=[]
    while len(res)<n:
        s=f"{RNG.choice(PREF)} {RNG.choice(NOMI)}"
        if s in out: s=next(c for c in combinazioni if c not in out)
        out.add(s); res.append(f"{s} {RNG.choice(suffissi)}")
    return res
def persone(n):
    res=[]; seen=set()
    while len(res)<n:
        s=f"{RNG.choice(NOMI_PERS)} {RNG.choice(COGN)}"
        if s not in seen: seen.add(s); res.append(s)
    return res
def date_pesate(n, start=START, end=END, crescita=0.12):
    """Date casuali con stagionalità (picco estivo e pre-natalizio) e crescita annua."""
    giorni = pd.date_range(start, end, freq='D')
    m = giorni.month.values; anni = (giorni.year.values - start.year)
    w = 1 + 0.35*np.isin(m,[5,6,7]) + 0.25*np.isin(m,[11,12]) - 0.35*(m==8)
    w = w * (1+crescita)**anni * np.where(giorni.dayofweek.values>=5, 0.15, 1)
    w = w / w.sum()
    return pd.to_datetime(RNG.choice(giorni.values, size=n, p=w))
def save(df, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    df.to_csv(path, index=False, encoding='utf-8', float_format='%.2f', date_format='%Y-%m-%d')


# ============================================================================
R = str(Path(__file__).resolve().parent.parent)  # cartella principale del repository
DATA_RIF = END

# ---------------- P1: vendite e crediti ----------------
p1 = f'{R}/01-powerbi-vendite-crediti/data'
ag_names = persone(8)
agenti = pd.DataFrame({'Codice Agente':[f'AG{i:02d}' for i in range(1,9)], 'Agente':ag_names,
                       'Area':['Nord-Ovest','Nord-Ovest','Nord-Ovest','Nord-Est','Nord-Est','Centro','Centro','Sud e Isole']})
nC = 320
prov = [PROVINCE[i] for i in RNG.integers(0,len(PROVINCE),nC)]
canale = RNG.choice(['Horeca','Retail','Grossisti'], nC, p=[.55,.35,.10])
acq = pd.to_datetime(np.where(RNG.random(nC)<.6, np.datetime64('2022-06-01'), RNG.choice(pd.date_range('2023-01-01','2026-06-30').values, nC)))
def agente_per_zona(z):
    c = agenti[agenti.Area==z]['Codice Agente'].values
    return RNG.choice(c)
clienti = pd.DataFrame({'Codice Cliente':[f'C{i:04d}' for i in range(1,nC+1)], 'Ragione Sociale':nomi_aziende(nC),
    'Provincia':[p for p,_ in prov], 'Zona':[z for _,z in prov], 'Canale':canale,
    'Codice Agente':[agente_per_zona(z) for _,z in prov], 'Data Acquisizione':acq.normalize(),
    'Giorni Pagamento':RNG.choice([30,60,90], nC, p=[.4,.4,.2])})
fornitori = pd.DataFrame({'Codice Fornitore':[f'F{i:03d}' for i in range(1,13)],
    'Fornitore':['Torrefazione Alpina Spa','Bevande del Lago Srl','Pastificio Le Spighe Srl','Dolciaria Valverde Spa','Caseificio Prato Verde Srl','Conserve del Golfo Srl',
                 'Surgelati Polare Spa','Forno Antico Srl','Detergenti Lindo Srl','Packaging Futura Srl','Oleificio Colle Alto Srl','Distillerie Monte Rosa Spa']})
FAM = {'Caffè':('F001',['Caffè in grani 1kg','Caffè macinato 250g','Capsule compatibili x50','Decaffeinato in grani 500g','Orzo solubile 200g'],(9,28)),
       'Bevande':('F002',['Acqua naturale 6x1,5L','Acqua frizzante 6x1,5L','Aranciata 24x33cl','Tè freddo limone 24x33cl','Succo pesca 24x20cl','Bibita cola 24x33cl'],(4,16)),
       'Pasta e farine':('F003',['Spaghetti 5kg','Penne rigate 5kg','Farina tipo 00 25kg','Lasagne fresche 1kg','Gnocchi 1kg'],(6,30)),
       'Dolci e snack':('F004',['Croissant vuoti x60','Biscotti frollini 3kg','Cornetti crema x50','Muffin cioccolato x24','Crackers monoporzione x100'],(12,45)),
       'Latticini':('F005',['Mozzarella fiordilatte 1kg','Mascarpone 500g','Panna da cucina 1L','Burro 1kg','Grana grattugiato 1kg'],(5,22)),
       'Conserve':('F006',['Polpa di pomodoro 4kg','Tonno all\'olio 1,7kg','Olive verdi 3kg','Carciofini 2kg'],(5,25)),
       'Surgelati':('F007',['Patatine fritte 2,5kg','Verdure grigliate 1kg','Spinaci a cubetti 2,5kg','Minestrone 1kg','Frutti di bosco 1kg'],(6,35)),
       'Panetteria':('F008',['Pane per tramezzini 1kg','Focaccia precotta x10','Pizza base x12','Bauletto bianco 500g'],(3,18)),
       'Detergenza':('F009',['Detersivo lavastoviglie 10kg','Sgrassatore 5L','Brillantante 5L','Sapone mani 5L'],(8,40)),
       'Monouso':('F010',['Bicchieri carta x1000','Tovaglioli 33x33 x2400','Vaschette alluminio x100','Cannucce carta x500'],(5,30)),
       'Olio e condimenti':('F011',['Olio extravergine 5L','Olio di semi 10L','Aceto balsamico 1L','Sale fino 10kg'],(4,45)),
       'Liquori':('F012',['Amaro alle erbe 70cl','Limoncello 70cl','Grappa 70cl','Vermouth rosso 1L'],(8,25))}
rows=[]; k=1
for fam,(forn,descs,(lo,hi)) in FAM.items():
    for d in descs:
        for var in ['', ' – formato promo'] if RNG.random()<.5 else ['']:
            pr = round(float(RNG.uniform(lo,hi)),2)
            rows.append([f'A{k:05d}', d+var, fam, forn, pr, round(pr*RNG.uniform(.55,.75),2)]); k+=1
articoli = pd.DataFrame(rows, columns=['Codice Articolo','Descrizione','Famiglia','Codice Fornitore','Prezzo Listino','Costo Standard'])

# fatture
peso_cli = RNG.lognormal(0,1.1,nC); peso_cli/=peso_cli.sum()
churn = pd.to_datetime(np.where(RNG.random(nC)<.12, RNG.choice(pd.date_range('2024-01-01','2026-06-30').values,nC), np.datetime64('2099-01-01')))
nF = 15000
date_f = date_pesate(nF*2)
cli_f = RNG.choice(nC, nF*2, p=peso_cli)
ok = (date_f >= clienti['Data Acquisizione'].values[cli_f]) & (date_f < churn[cli_f])
date_f, cli_f = date_f[ok][:nF], cli_f[ok][:nF]
ordn = np.argsort(date_f); date_f, cli_f = date_f[ordn], cli_f[ordn]
peso_art = RNG.lognormal(0,1,len(articoli)); peso_art/=peso_art.sum()
righe=[]
cnt={}
for d,c in zip(date_f, cli_f):
    y=d.year; cnt[y]=cnt.get(y,0)+1; nf=f'FT{y}-{cnt[y]:05d}'
    for a in RNG.choice(len(articoli), RNG.integers(2,9), replace=False, p=peso_art):
        art=articoli.iloc[a]; q=int(RNG.integers(1,25)); omaggio = RNG.random()<.04
        sc = 0 if omaggio else float(RNG.choice([0,0,0,5,10,15]))
        prezzo = art['Prezzo Listino']*(1+0.04*(y-2023))
        lordo = q*prezzo
        righe.append([nf, d, clienti['Codice Cliente'].iat[c], clienti['Codice Agente'].iat[c], art['Codice Articolo'], q, round(prezzo,2), sc,
                      0.0 if omaggio else round(lordo*(1-sc/100),2), round(lordo,2) if omaggio else 0.0, round(q*art['Costo Standard'],2)])
fatture = pd.DataFrame(righe, columns=['Numero Fattura','Data Fattura','Codice Cliente','Codice Agente','Codice Articolo','Quantita','Prezzo Listino','Sconto %','Imponibile','Valore Omaggio','Costo'])
# scadenze (importi IVA inclusa)
tes = fatture.groupby(['Numero Fattura','Data Fattura','Codice Cliente'],as_index=False)['Imponibile'].sum()
tes = tes[tes.Imponibile>0]
gp = clienti.set_index('Codice Cliente')['Giorni Pagamento']
ritardo_cli = pd.Series(RNG.choice([-5,0,5,15,30,60], nC, p=[.1,.35,.25,.15,.1,.05]), index=clienti['Codice Cliente'])
tes['Data Scadenza'] = tes['Data Fattura'] + pd.to_timedelta(tes['Codice Cliente'].map(gp),'D')
rit = tes['Codice Cliente'].map(ritardo_cli).values + RNG.integers(-5,20,len(tes))
pag = tes['Data Scadenza'] + pd.to_timedelta(rit,'D')
tes['Data Pagamento'] = pag.where(pag<=DATA_RIF)
tes['Importo'] = (tes.Imponibile*1.22).round(2)
scadenze = tes[['Numero Fattura','Codice Cliente','Data Fattura','Data Scadenza','Importo','Data Pagamento']]
for n,df in [('agenti',agenti),('clienti',clienti),('fornitori',fornitori),('articoli',articoli),('fatture_righe',fatture.drop(columns=['Costo'])),('scadenze',scadenze)]:
    save(df, f'{p1}/{n}.csv')
print('P1', len(fatture), 'righe fattura', len(scadenze), 'scadenze', fatture.Imponibile.sum().round())

# ---------------- P5: Qlik vendite e margini (riusa anagrafiche P1) ----------------
p5 = f'{R}/05-qlik-vendite-margini/data'
save(agenti, f'{p5}/agenti.csv'); save(clienti.drop(columns=['Giorni Pagamento']), f'{p5}/clienti.csv'); save(articoli, f'{p5}/articoli.csv')
save(fatture, f'{p5}/fatture_righe.csv')
# ordini: ogni fattura nasce da un ordine; data ordine prima, consegna richiesta, consegna effettiva
o = fatture[['Numero Fattura','Data Fattura','Codice Cliente','Codice Agente','Codice Articolo','Quantita','Imponibile']].copy()
o['Numero Ordine'] = o['Numero Fattura'].str.replace('FT','OV')
o['Data Ordine'] = o['Data Fattura'] - pd.to_timedelta(RNG.integers(3,25,len(o)),'D')
o['Data Consegna Richiesta'] = o['Data Ordine'] + pd.to_timedelta(RNG.choice([5,7,10,14],len(o)),'D')
o['Data Consegna Effettiva'] = o['Data Consegna Richiesta'] + pd.to_timedelta(RNG.choice([-3,-1,0,0,0,1,2,5,9],len(o)),'D')
o['Stato Riga'] = 'Evasa'
# ordini aperti (portafoglio) ultime settimane
extra = o.sample(900, random_state=1).copy()
extra['Data Ordine'] = pd.to_datetime(RNG.choice(pd.date_range('2026-09-01','2026-09-30').values, len(extra)))
extra['Data Consegna Richiesta'] = extra['Data Ordine'] + pd.to_timedelta(RNG.choice([7,14,21,30],len(extra)),'D')
extra['Data Consegna Effettiva'] = pd.NaT; extra['Stato Riga']='Aperta'
extra['Numero Ordine'] = ['OV2026-9' + f'{i:04d}' for i in range(len(extra))]
ordini = pd.concat([o,extra]).rename(columns={'Imponibile':'Valore Riga'})
ordini = ordini[['Numero Ordine','Data Ordine','Codice Cliente','Codice Agente','Codice Articolo','Quantita','Valore Riga','Data Consegna Richiesta','Data Consegna Effettiva','Stato Riga']]
save(ordini, f'{p5}/ordini_righe.csv')
bud = fatture.assign(Anno=fatture['Data Fattura'].dt.year, Mese=fatture['Data Fattura'].dt.month).merge(articoli[['Codice Articolo','Famiglia']])
bud = bud.groupby(['Anno','Mese','Famiglia'],as_index=False).Imponibile.sum()
bud = bud[bud.Anno>=2024]; bud['Budget'] = (bud.Imponibile*RNG.uniform(.95,1.15,len(bud))).round(-2)
fut = bud[bud.Anno==2026].copy(); 
for m in [10,11,12]:
    t=bud[(bud.Anno==2025)&(bud.Mese==m)].copy(); t['Anno']=2026; t['Budget']=(t.Imponibile*1.1).round(-2); fut=pd.concat([fut,t])
bud = pd.concat([bud[bud.Anno<2026],fut])[['Anno','Mese','Famiglia','Budget']]
save(bud, f'{p5}/budget.csv')
print('P5 ordini', len(ordini), 'budget', len(bud))

# ---------------- P2: acquisti ----------------
p2 = f'{R}/02-powerbi-acquisti-abc/data'
save(fornitori, f'{p2}/fornitori.csv'); save(articoli.drop(columns=['Prezzo Listino']).rename(columns={'Costo Standard':'Costo Standard'}), f'{p2}/articoli.csv')
nA = 14000
d = date_pesate(nA, crescita=.08)
a = RNG.choice(len(articoli), nA, p=peso_art)
acq_rows=[]; cnt={}
for di,ai in sorted(zip(d,a)):
    art = articoli.iloc[ai]; q = int(RNG.integers(10,300)); 
    infl = 1+0.05*(di.year-2023)
    costo_u = art['Costo Standard']*infl*RNG.uniform(.9,1.12)
    listino_u = art['Costo Standard']*infl*1.05
    interno = RNG.random()<.06
    y=di.year; cnt[y]=cnt.get(y,0)+1
    acq_rows.append([di, '' if interno else f'DDT-{art["Codice Fornitore"]}-{y}-{cnt[y]:05d}', 'Carico interno' if interno else 'Carico da fornitore',
                     art['Codice Fornitore'], art['Codice Articolo'], q, round(q*costo_u,2), '' if RNG.random()<.03 else round(q*listino_u,2)])
acquisti = pd.DataFrame(acq_rows, columns=['Data Documento','Numero Documento','Tipo Movimento','Codice Fornitore','Codice Articolo','Quantita','Costo Totale','Listino Totale'])
save(acquisti, f'{p2}/acquisti.csv')
print('P2', len(acquisti))

# ---------------- P3: pipeline commerciale ----------------
p3 = f'{R}/03-powerbi-pipeline-commerciale/data'
comm = pd.DataFrame({'Codice Commerciale':[f'S{i:02d}' for i in range(1,7)], 'Commerciale':persone(6), 'Team':['Enterprise','Enterprise','Mid-market','Mid-market','PMI','PMI']})
nK=220
cli3 = pd.DataFrame({'Codice Cliente':[f'K{i:04d}' for i in range(1,nK+1)],
   'Ragione Sociale':[f"{RNG.choice(['Meccanica','Logistica','Tessile','Alimentare','Plastiche','Elettronica','Arredi','Chimica','Trasporti','Packaging'])} {RNG.choice(NOMI)} {RNG.choice(['Srl','Spa'])}" for _ in range(nK)],
   'Settore':RNG.choice(['Manifattura','Distribuzione','Servizi','Alimentare','Logistica'],nK),
   'Regione':RNG.choice(['Lombardia','Piemonte','Veneto','Emilia-Romagna','Toscana','Lazio','Campania'],nK,p=[.3,.15,.15,.15,.1,.1,.05]),
   'Dimensione':RNG.choice(['Grande','Media','Piccola'],nK,p=[.2,.4,.4])})
cli3['Codice Commerciale'] = cli3.Dimensione.map({'Grande':['S01','S02'],'Media':['S03','S04'],'Piccola':['S05','S06']}).apply(lambda l: RNG.choice(l))
LINEE = {'Gestionale ERP':('One-off',(15000,120000)),'CRM':('One-off',(5000,40000)),'BI e Analytics':('One-off',(8000,60000)),
         'Canoni Cloud':('Ricorrente',(3000,30000)),'Assistenza e manutenzione':('Ricorrente',(2000,20000)),'Formazione':('One-off',(1500,10000))}
nT=2600
dap = date_pesate(nT, start=pd.Timestamp('2023-01-01'), end=pd.Timestamp('2026-09-30'), crescita=.15)
tr=[]
for i,dd in enumerate(sorted(dap)):
    c = cli3.iloc[RNG.integers(0,nK)]; lin = RNG.choice(list(LINEE)); tipo,(lo,hi)=LINEE[lin]
    mult = {'Grande':1.8,'Media':1,'Piccola':.6}[c.Dimensione]
    val = round(float(RNG.uniform(lo,hi))*mult,-2)
    durata = int(RNG.gamma(3,25))
    chiusura = dd + pd.Timedelta(days=durata)
    if chiusura > END:
        stato = RNG.choice(['Aperta','In negoziazione'],p=[.6,.4]); chiusura=pd.NaT
    else:
        stato = RNG.choice(['Vinta','Persa'], p=[.42,.58] if c.Dimensione!='Grande' else [.35,.65])
    motivo = '' if stato!='Persa' else RNG.choice(['Prezzo','Concorrenza','Progetto rimandato','Requisiti non coperti'])
    tr.append([f'T{dd.year}-{i+1:05d}', dd, chiusura, stato, motivo, c['Codice Cliente'], c['Codice Commerciale'], lin, tipo, val])
tratt = pd.DataFrame(tr, columns=['ID Trattativa','Data Apertura','Data Chiusura','Stato','Motivo Perdita','Codice Cliente','Codice Commerciale','Linea Prodotto','Tipo Ricavo','Valore'])
vinte = tratt[tratt.Stato=='Vinta'].reset_index(drop=True)
ordi = pd.DataFrame({'Numero Ordine':[f'OC{d.year}-{i+1:05d}' for i,d in enumerate(vinte['Data Chiusura'])], 'Data Ordine':vinte['Data Chiusura'],
    'ID Trattativa':vinte['ID Trattativa'], 'Codice Cliente':vinte['Codice Cliente'], 'Codice Commerciale':vinte['Codice Commerciale'],
    'Linea Prodotto':vinte['Linea Prodotto'], 'Tipo Ricavo':vinte['Tipo Ricavo'], 'Valore Ordine':(vinte.Valore*RNG.uniform(.9,1.0,len(vinte))).round(-1)})
ordi['Data Consegna Prevista'] = ordi['Data Ordine'] + pd.to_timedelta(RNG.integers(20,180,len(ordi)),'D')
ft=[]; k=0
for _,r in ordi.iterrows():
    if r['Tipo Ricavo']=='Ricorrente':
        rate=[(r['Data Ordine']+pd.DateOffset(months=m), r['Valore Ordine']/12) for m in range(1,13)]
    else:
        n=RNG.choice([1,2,3]); rate=[(r['Data Ordine']+pd.Timedelta(days=int(30+60*j+RNG.integers(0,30))), r['Valore Ordine']/n) for j in range(n)]
    for d_,imp in rate:
        if d_<=END:
            k+=1; ft.append([f'FV{d_.year}-{k:05d}', d_.normalize(), r['Numero Ordine'], r['Codice Cliente'], r['Linea Prodotto'], r['Tipo Ricavo'], round(imp,2)])
fatt3 = pd.DataFrame(ft, columns=['Numero Fattura','Data Fattura','Numero Ordine','Codice Cliente','Linea Prodotto','Tipo Ricavo','Importo'])
b = fatt3.assign(Anno=fatt3['Data Fattura'].dt.year, Mese=fatt3['Data Fattura'].dt.month).groupby(['Anno','Mese','Linea Prodotto'],as_index=False).Importo.sum()
b = b[b.Anno>=2024]; b['Budget']=(b.Importo*RNG.uniform(.95,1.2,len(b))).round(-2)
ext=b[(b.Anno==2025)&(b.Mese>=10)].copy(); ext['Anno']=2026; ext['Budget']=(ext.Importo*1.15).round(-2)
budget3 = pd.concat([b,ext])[['Anno','Mese','Linea Prodotto','Budget']]
for n,df in [('commerciali',comm),('clienti',cli3),('trattative',tratt),('ordini',ordi),('fatture',fatt3),('budget',budget3)]:
    save(df, f'{p3}/{n}.csv')
print('P3', len(tratt), 'trattative', len(ordi), 'ordini', len(fatt3), 'fatture')

# ---------------- P4: produzione ----------------
p4 = f'{R}/04-powerbi-produzione-scarti/data'
art4 = pd.DataFrame({'Codice Articolo':[f'PF{i:04d}' for i in range(1,41)],
    'Descrizione':[f"{RNG.choice(['Film','Film stretch','Film termoretraibile','Film barriera','Tubolare'])} {RNG.choice([20,23,30,35,50,80])} micron h{RNG.choice([500,750,1000,1500])}" for _ in range(40)],
    'Famiglia':RNG.choice(['Imballaggio industriale','Alimentare','Agricoltura','Edilizia'],40),
    'Spessore Micron':RNG.choice([20,23,30,35,50,80],40)})
linee = {'Linea 1':(420,.035),'Linea 2':(380,.045),'Linea 3':(510,.03),'Linea 4':(300,.06)}
pr=[]; k=0
for d_ in pd.date_range('2024-01-01','2026-09-30'):
    if d_.dayofweek==6: continue
    for lin,(kgh,scarto) in linee.items():
        if d_.month==8 and d_.day<20: continue
        for turno in ['A','B','C']:
            if RNG.random()<.12: continue
            k+=1; art=art4.iloc[RNG.integers(0,40)]
            ore = round(float(RNG.uniform(5.5,8)),2)
            eff = 1 + 0.02*(d_.year-2024)
            cons = ore*kgh*RNG.uniform(.85,1.05)*eff
            sc = cons*max(0.005, RNG.normal(scarto*(1-0.08*(d_.year-2024)), scarto/3))
            rif = cons*RNG.uniform(.005,.02)
            prod = cons-sc-rif
            m2 = prod/ (art['Spessore Micron']*0.92/1000)
            pr.append([d_, f'ODP{d_.year}-{k:05d}', lin, turno, art['Codice Articolo'], ore, round(cons,1), round(prod,1), round(sc,1), round(rif,1), round(m2,0), int(prod//RNG.uniform(180,260))])
prod4 = pd.DataFrame(pr, columns=['Data','Ordine Produzione','Linea','Turno','Codice Articolo','Ore Lavorate','Consumo Kg','Produzione Kg','Scarto Kg','Rifili Kg','Metri Quadri','Bobine OK'])
save(art4, f'{p4}/articoli.csv'); save(prod4, f'{p4}/produzione.csv')
print('P4', len(prod4))

# ---------------- ritocchi P3: data del mese nel budget e tabella linee ----------------
p3 = f'{R}/03-powerbi-pipeline-commerciale/data'
b=pd.read_csv(f'{p3}/budget.csv'); b['Data Mese']=pd.to_datetime(dict(year=b.Anno,month=b.Mese,day=1)).dt.strftime('%Y-%m-%d')
b[['Data Mese','Anno','Mese','Linea Prodotto','Budget']].to_csv(f'{p3}/budget.csv',index=False)
t=pd.read_csv(f'{p3}/trattative.csv')
t[['Linea Prodotto','Tipo Ricavo']].drop_duplicates().sort_values('Linea Prodotto').to_csv(f'{p3}/linee_prodotto.csv',index=False)
