# 🚀 Guida al Deployment - Knowledge Valorisation Platform

Questa guida fornisce istruzioni dettagliate per deployare la piattaforma su diverse piattaforme di hosting.

## 📋 Indice

1. [Streamlit Cloud (Raccomandato)](#streamlit-cloud)
2. [GitHub Pages + Streamlit](#github-pages)
3. [Heroku](#heroku)
4. [Docker](#docker)
5. [Vercel](#vercel)
6. [Railway](#railway)

---

## 🌟 Streamlit Cloud (Raccomandato)

**Vantaggi**: Gratuito, integrazione GitHub, SSL automatico, facile da configurare

### Passo 1: Preparazione Repository GitHub

1. **Crea un nuovo repository** su GitHub
2. **Carica tutti i file** del progetto:
```bash
git init
git add .
git commit -m "Initial commit: Knowledge Valorisation Platform"
git branch -M main
git remote add origin https://github.com/USERNAME/knowledge-valorisation-platform.git
git push -u origin main
```

### Passo 2: Deploy su Streamlit Cloud

1. **Vai su** [share.streamlit.io](https://share.streamlit.io)
2. **Accedi** con il tuo account GitHub
3. **Clicca** "New app"
4. **Seleziona**:
   - Repository: `USERNAME/knowledge-valorisation-platform`
   - Branch: `main`
   - Main file path: `app.py`
5. **Clicca** "Deploy!"

### Passo 3: Configurazione Secrets (Opzionale)

Se vuoi usare le funzionalità AI:

1. **Vai nelle impostazioni** dell'app su Streamlit Cloud
2. **Aggiungi secrets**:
```toml
[openai]
OPENAI_API_KEY = "your-openai-api-key-here"
```

### Passo 4: URL Personalizzato (Opzionale)

L'app sarà disponibile su: `https://USERNAME-knowledge-valorisation-platform-app-main-xxxxx.streamlit.app`

---

## 📄 GitHub Pages + Streamlit

**Vantaggi**: Hosting gratuito su GitHub, dominio personalizzabile

### Limitazioni
- Streamlit non può essere hostato direttamente su GitHub Pages
- Alternativa: Convertire in app statica o usare GitHub Codespaces

### Opzione 1: GitHub Codespaces

1. **Abilita Codespaces** nel repository
2. **Crea** `.devcontainer/devcontainer.json`:
```json
{
  "name": "Knowledge Valorisation Platform",
  "image": "python:3.11",
  "postCreateCommand": "pip install -r requirements.txt",
  "forwardPorts": [8501],
  "customizations": {
    "vscode": {
      "extensions": ["ms-python.python"]
    }
  }
}
```

3. **Avvia Codespace** e esegui:
```bash
streamlit run app.py
```

### Opzione 2: GitHub Actions per Deploy Automatico

Crea `.github/workflows/deploy.yml`:
```yaml
name: Deploy to Streamlit Cloud

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Setup Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.11'
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
    - name: Test app
      run: |
        python -c "import streamlit; print('Streamlit OK')"
```

---

## 🔥 Heroku

**Vantaggi**: Controllo completo, database integrati, scaling automatico

### Passo 1: Preparazione

1. **Installa Heroku CLI**
2. **Login**: `heroku login`
3. **Crea app**: `heroku create your-app-name`

### Passo 2: Configurazione

Crea `Procfile`:
```
web: streamlit run app.py --server.headless true --server.enableCORS false --server.port $PORT
```

### Passo 3: Deploy

```bash
git add .
git commit -m "Deploy to Heroku"
git push heroku main
```

### Passo 4: Configurazione Variabili

```bash
heroku config:set OPENAI_API_KEY="your-api-key"
```

---

## 🐳 Docker

**Vantaggi**: Ambiente isolato, portabilità, scaling

### Deploy Locale

```bash
# Build
docker build -t knowledge-valorisation .

# Run
docker run -p 8501:8501 -e OPENAI_API_KEY="your-key" knowledge-valorisation
```

### Deploy con Docker Compose

```bash
# Con variabili d'ambiente
echo "OPENAI_API_KEY=your-key" > .env

# Avvia
docker-compose up -d
```

### Deploy su Cloud Provider

**Google Cloud Run**:
```bash
gcloud run deploy --image gcr.io/PROJECT-ID/knowledge-valorisation --platform managed
```

**AWS ECS**:
```bash
aws ecs create-service --cluster my-cluster --service-name knowledge-valorisation
```

---

## ⚡ Vercel

**Vantaggi**: Deploy veloce, CDN globale, integrazione GitHub

### Limitazioni
Vercel è ottimizzato per Next.js, ma può hostare Streamlit con configurazioni speciali.

### Setup

1. **Installa Vercel CLI**: `npm i -g vercel`
2. **Crea** `vercel.json`:
```json
{
  "builds": [
    {
      "src": "app.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "app.py"
    }
  ]
}
```

3. **Deploy**: `vercel --prod`

---

## 🚂 Railway

**Vantaggi**: Deploy semplice, database integrati, pricing competitivo

### Setup

1. **Vai su** [railway.app](https://railway.app)
2. **Connetti GitHub** repository
3. **Seleziona** il repository
4. **Railway** rileverà automaticamente Python e Streamlit
5. **Configura variabili d'ambiente** se necessario

---

## 🔧 Configurazioni Avanzate

### Dominio Personalizzato

**Streamlit Cloud**: Non supportato nel piano gratuito
**Heroku**: `heroku domains:add yourdomain.com`
**Vercel**: Configurazione automatica
**Railway**: Supporto domini personalizzati

### SSL/HTTPS

Tutti i provider moderni includono SSL automatico.

### Monitoraggio

**Streamlit Cloud**: Logs integrati
**Heroku**: `heroku logs --tail`
**Docker**: `docker logs container-name`

### Backup

```bash
# Backup dati
docker exec container-name tar -czf /backup/data.tar.gz /app/data

# Backup database (se presente)
heroku pg:backups:capture --app your-app-name
```

---

## 🚨 Troubleshooting

### Errori Comuni

**Port binding error**:
```python
# Assicurati che l'app usi la porta corretta
port = int(os.environ.get("PORT", 8501))
```

**Memory limit**:
- Riduci le dipendenze non necessarie
- Ottimizza il caricamento dei dati
- Usa caching di Streamlit

**Build timeout**:
- Riduci il numero di dipendenze
- Usa immagini Docker più leggere
- Ottimizza il Dockerfile

### Performance

**Caching**:
```python
@st.cache_data
def load_data():
    return expensive_computation()
```

**Lazy loading**:
```python
if 'data' not in st.session_state:
    st.session_state.data = load_data()
```

---

## 📞 Supporto

Per problemi specifici di deployment:

1. **Controlla i logs** della piattaforma
2. **Verifica le variabili d'ambiente**
3. **Testa localmente** prima del deploy
4. **Consulta la documentazione** del provider

---

## 🎯 Raccomandazioni Finali

### Per Sviluppo/Test
- **Streamlit Cloud**: Ideale per prototipi e demo
- **GitHub Codespaces**: Perfetto per sviluppo collaborativo

### Per Produzione
- **Heroku**: Controllo completo, database integrati
- **Railway**: Semplicità e performance
- **Docker + Cloud Provider**: Massima flessibilità

### Per Enterprise
- **AWS/GCP/Azure**: Scalabilità e sicurezza enterprise
- **Docker Swarm/Kubernetes**: Orchestrazione avanzata

Scegli la soluzione più adatta alle tue esigenze specifiche!

