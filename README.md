# 🎓 Knowledge Valorisation Self-Assessment Platform

Una piattaforma Streamlit per la valutazione della maturità nella valorizzazione della conoscenza e collaborazione industria-accademia, basata sulla metodologia del caso Bologna.

## 🌟 Caratteristiche Principali

- **54 domande** organizzate in 6 canali e 3 fattori
- **Interfaccia intuitiva** con scala Likert (1-7) e domande Yes/No
- **Analisi AI-powered** con semantic e sentiment analysis
- **Insights narrativi automatici** simili al caso Bologna
- **Visualizzazioni interattive** dei risultati
- **Export dei dati** in formato JSON/CSV

## 🏗️ Architettura

### Canali di Valutazione
1. **Joint Research & Co-creation** - Ricerca collaborativa
2. **Shared Infrastructure & Resources** - Infrastrutture condivise
3. **Knowledge & Technology Transfer** - Trasferimento tecnologico
4. **Entrepreneurship & Spin-offs** - Imprenditorialità
5. **Mobility & Skills Development** - Mobilità e competenze
6. **Regional Innovation Ecosystem** - Ecosistema innovativo regionale

### Fattori di Analisi
- **Environmental** (env) - Aspetti normativi e di policy
- **Organizational** (org) - Processi interni organizzativi
- **Individual** (ind) - Competenze e aspetti personali

## 🚀 Installazione e Setup

### Prerequisiti
- Python 3.11+
- pip

### Installazione Locale

1. **Clona il repository**
```bash
git clone <repository-url>
cd knowledge-valorisation-platform
```

2. **Installa le dipendenze**
```bash
pip install -r requirements.txt
```

3. **Configura OpenAI (opzionale)**
```bash
export OPENAI_API_KEY="your-api-key-here"
```

4. **Avvia l'applicazione**
```bash
streamlit run app.py
```

L'applicazione sarà disponibile su `http://localhost:8501`

## 🌐 Deployment

### Streamlit Cloud (Raccomandato)

1. **Fork questo repository** su GitHub
2. **Vai su [share.streamlit.io](https://share.streamlit.io)**
3. **Connetti il tuo account GitHub**
4. **Seleziona il repository** e il branch
5. **Configura i secrets** (se necessario):
   - `OPENAI_API_KEY` per le funzionalità AI

### Heroku

1. **Crea un'app Heroku**
```bash
heroku create your-app-name
```

2. **Configura le variabili d'ambiente**
```bash
heroku config:set OPENAI_API_KEY="your-api-key"
```

3. **Deploy**
```bash
git push heroku main
```

### Docker (Opzionale)

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.headless", "true", "--server.address", "0.0.0.0"]
```

## 📁 Struttura del Progetto

```
knowledge-valorisation-platform/
├── app.py                          # Applicazione principale Streamlit
├── requirements.txt                # Dipendenze Python
├── README.md                       # Documentazione
├── .streamlit/
│   └── config.toml                # Configurazione Streamlit
├── data/
│   └── knowledge-valorisation-*.xlsx  # Dati del questionario
├── utils/
│   ├── __init__.py
│   ├── data_manager.py            # Gestione dati e persistenza
│   ├── scoring_engine.py          # Calcolo punteggi
│   ├── insight_generator.py       # Generazione insights AI
│   ├── question_manager.py        # Gestione domande
│   └── visualization_engine.py    # Creazione grafici
└── pages/                         # Pagine aggiuntive (future)
```

## 🔧 Configurazione

### Variabili d'Ambiente

- `OPENAI_API_KEY`: Chiave API OpenAI per funzionalità AI (opzionale)

### File di Configurazione

- `.streamlit/config.toml`: Configurazione tema e server Streamlit
- `requirements.txt`: Dipendenze Python

## 📊 Utilizzo

### 1. Informazioni Preliminari
- Inserisci nome, organizzazione, ruolo e settore
- Salva le informazioni per procedere

### 2. Assessment
- Rispondi alle 54 domande organizzate per canale
- Usa la scala Likert (1-7) per le valutazioni qualitative
- Rispondi Yes/No per gli aspetti specifici
- Aggiungi commenti opzionali per contesto aggiuntivo

### 3. Risultati
- Visualizza punteggi per canale e fattore
- Leggi gli insights narrativi generati dall'AI
- Confronta con il benchmark del caso Bologna
- Scarica i risultati in formato JSON

### 4. Dashboard
- Analisi avanzate e visualizzazioni
- Metriche di maturità complessiva
- Confronti e trend

## 🤖 Funzionalità AI

### Semantic Analysis
- Estrazione di temi chiave dalle risposte aperte
- Identificazione di pattern e tendenze
- Categorizzazione automatica dei contenuti

### Sentiment Analysis
- Analisi del sentiment delle risposte testuali
- Identificazione di atteggiamenti positivi/negativi
- Valutazione della polarità emotiva

### Generazione Insights
- Narrativa automatica per ogni canale
- Raccomandazioni personalizzate
- Executive summary strategico

## 📈 Metodologia di Scoring

### Calcolo Punteggi
1. **Normalizzazione**: Yes/No → 1/7, Likert → 1-7
2. **Fattore**: Media delle risposte per fattore in un canale
3. **Canale**: Media dei punteggi dei fattori
4. **Totale**: Media di tutti i punteggi dei canali

### Benchmark
- **Caso Bologna**: 5.76/7 (riferimento)
- **Livelli di Maturità**:
  - Iniziale: < 4.0
  - Base: 4.0-5.0
  - Intermedio: 5.0-6.0
  - Avanzato: ≥ 6.0

## 🛠️ Sviluppo

### Aggiungere Nuove Domande
1. Modifica il file Excel in `data/`
2. Aggiorna il `QuestionManager` se necessario
3. Testa il caricamento delle domande

### Personalizzare Insights
1. Modifica i template in `InsightGenerator`
2. Aggiorna i prompt per l'AI
3. Testa la generazione di insights

### Nuove Visualizzazioni
1. Aggiungi metodi al `VisualizationEngine`
2. Integra nelle pagine dell'app
3. Testa la renderizzazione

## 🔒 Privacy e Sicurezza

- **Anonimizzazione**: I dati sensibili vengono automaticamente anonimizzati
- **Locale**: Tutti i dati rimangono nella sessione locale
- **GDPR**: Conformità per utenti europei
- **No tracking**: Nessun tracciamento degli utenti

## 🐛 Troubleshooting

### Problemi Comuni

**Errore ModuleNotFoundError**
```bash
pip install -r requirements.txt
```

**Problemi con OpenAI**
- Verifica la chiave API
- Controlla i limiti di utilizzo
- L'app funziona anche senza OpenAI (con template predefiniti)

**Problemi di caricamento Excel**
- Verifica che il file sia nella directory `data/`
- Controlla il formato del file Excel
- Usa le domande di esempio se il file non è disponibile

## 🤝 Contribuire

1. Fork il repository
2. Crea un branch per la feature (`git checkout -b feature/AmazingFeature`)
3. Commit le modifiche (`git commit -m 'Add some AmazingFeature'`)
4. Push al branch (`git push origin feature/AmazingFeature`)
5. Apri una Pull Request

## 📄 Licenza

Questo progetto è rilasciato sotto licenza MIT. Vedi il file `LICENSE` per i dettagli.

## 📞 Supporto

Per supporto e domande:
- Apri un issue su GitHub
- Consulta la documentazione
- Controlla la sezione Troubleshooting

## 🙏 Riconoscimenti

- Basato sulla metodologia del **Caso Bologna**
- Sviluppato con **Streamlit**
- Analisi AI powered by **OpenAI**
- Visualizzazioni con **Plotly**

---

**Versione**: 1.0.0  
**Ultimo aggiornamento**: Agosto 2025

