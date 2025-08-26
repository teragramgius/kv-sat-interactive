import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
import os
from datetime import datetime
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    openai = None
from wordcloud import WordCloud
import matplotlib.pyplot as plt
# Import dei moduli utility (caricamento dinamico per evitare errori)
import sys
import os

# Aggiungi la directory utils al path
sys.path.append(os.path.join(os.path.dirname(__file__), 'utils'))

# Configurazione pagina
st.set_page_config(
    page_title="Knowledge Valorisation Self-Assessment",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Configurazione OpenAI
if OPENAI_AVAILABLE and 'OPENAI_API_KEY' in os.environ:
    openai.api_key = os.environ['OPENAI_API_KEY']

# Inizializzazione componenti
@st.cache_resource
def initialize_components():
    """Inizializza i componenti dell'applicazione"""
    try:
        from data_manager import DataManager
        from scoring_engine import ScoringEngine
        from insight_generator import InsightGenerator
        from question_manager import QuestionManager
        from visualization_engine import VisualizationEngine
        
        return DataManager(), ScoringEngine(), InsightGenerator(), QuestionManager(), VisualizationEngine()
    except ImportError as e:
        st.error(f"Errore nell'importazione dei moduli: {e}")
        return None, None, None, None, None

# Caricamento dati
@st.cache_data
def load_questions():
    """Carica le domande dal file Excel"""
    try:
        from question_manager import QuestionManager
        question_manager = QuestionManager()
        questions = question_manager.load_questions_from_excel('data/knowledge-valorisation-self-assessment-tool-with-the-case-of-bologna.xlsx')
        return questions
    except Exception as e:
        st.error(f"Errore nel caricamento delle domande: {e}")
        return []

def initialize_session_state():
    """Inizializza lo stato della sessione"""
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 'Home'
    
    if 'user_info' not in st.session_state:
        st.session_state.user_info = {}
    
    if 'responses' not in st.session_state:
        st.session_state.responses = {}
    
    if 'current_question_index' not in st.session_state:
        st.session_state.current_question_index = 0
    
    if 'assessment_completed' not in st.session_state:
        st.session_state.assessment_completed = False

def render_sidebar():
    """Renderizza la sidebar di navigazione"""
    with st.sidebar:
        st.markdown("# 🎓 Knowledge Valorisation")
        
        # Menu di navigazione
        pages = ['Home', 'Assessment', 'Results', 'Dashboard']
        
        for page in pages:
            if st.button(page, use_container_width=True, 
                        type="primary" if st.session_state.current_page == page else "secondary"):
                st.session_state.current_page = page
                st.rerun()

def render_home_page():
    """Renderizza la pagina home"""
    st.title("🎓 Knowledge Valorisation Self-Assessment Platform")
    
    st.markdown("""
    ## Benvenuto nella Piattaforma di Auto-Valutazione per la Valorizzazione della Conoscenza
    
    Questa piattaforma ti permette di valutare il livello di maturità della tua organizzazione nella valorizzazione della conoscenza e nella collaborazione industria-accademia.
    """)
    
    # Informazioni sull'assessment
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### 📋 Cosa include l'assessment:
        
        - **102 domande** organizzate in 6 canali principali
        - **Scala Likert (1-7)** per valutazioni qualitative  
        - **Domande Yes/No** per aspetti specifici
        - **Campi aperti** per commenti e contesto
        """)
        
        st.markdown("""
        ### 🎯 I 6 Canali di Valutazione:
        
        1. **Academia-Industry joint research & mobility** - Ricerca collaborativa
        2. **Promoting research-driven spin-offs and start-ups** - Imprenditorialità
        3. **Intermediaries and knowledge transfer professionals** - Trasferimento tecnologico
        4. **Engagement of citizens, public bodies and societal actors** - Coinvolgimento sociale
        5. **Intellectual Property management & Standardisation** - Gestione IP
        6. **Knowledge circulation & informing policy** - Circolazione conoscenza
        """)
    
    with col2:
        st.markdown("""
        ### 🤖 Analisi AI-Powered:
        
        - **Semantic Analysis** delle risposte aperte
        - **Sentiment Analysis** per identificare atteggiamenti
        - **Generazione automatica** di insights narrativi
        - **Raccomandazioni personalizzate** basate sui risultati
        """)
        
        st.markdown("""
        ### 📊 Output Finale:
        
        - **Punteggi dettagliati** per canale e fattore
        - **Schema narrativo** simile al caso Bologna
        - **Visualizzazioni interattive** dei risultati
        - **Report scaricabile** in formato PDF/JSON
        """)
    
    st.markdown("---")
    
    # Sezione informazioni utente
    st.subheader("👤 Informazioni Preliminari")
    
    col1, col2 = st.columns(2)
    
    with col1:
        name = st.text_input("Nome e Cognome", value=st.session_state.user_info.get('name', ''))
        organization = st.text_input("Organizzazione", value=st.session_state.user_info.get('organization', ''))
    
    with col2:
        role = st.text_input("Ruolo", value=st.session_state.user_info.get('role', ''))
        sector = st.selectbox("Settore", 
                             ['Università', 'Centro di Ricerca', 'Azienda Privata', 'Ente Pubblico', 'Altro'],
                             index=0 if not st.session_state.user_info.get('sector') else 
                             ['Università', 'Centro di Ricerca', 'Azienda Privata', 'Ente Pubblico', 'Altro'].index(st.session_state.user_info.get('sector')))
    
    if st.button("💾 Salva Informazioni e Inizia Assessment", type="primary", use_container_width=True):
        st.session_state.user_info = {
            'name': name,
            'organization': organization,
            'role': role,
            'sector': sector,
            'timestamp': datetime.now().isoformat()
        }
        st.session_state.current_page = 'Assessment'
        st.success("Informazioni salvate! Reindirizzamento all'assessment...")
        st.rerun()

def render_assessment_page():
    """Renderizza la pagina dell'assessment"""
    st.title("📝 Knowledge Valorisation Assessment")
    
    # Verifica informazioni preliminari
    if not all([
        st.session_state.user_info.get('name'),
        st.session_state.user_info.get('organization'),
        st.session_state.user_info.get('role'),
        st.session_state.user_info.get('sector')
    ]):
        st.warning("⚠️ Per favore completa le informazioni preliminari nella pagina Home.")
        if st.button("🏠 Torna alla Home"):
            st.session_state.current_page = 'Home'
            st.rerun()
        return
    
    # Carica le domande reali
    questions = load_questions()
    if not questions:
        st.error("❌ Impossibile caricare le domande. Contatta il supporto.")
        return
    
    # Inizializza l'indice della domanda corrente
    if 'current_question_index' not in st.session_state:
        st.session_state.current_question_index = 0
    
    # Progress bar
    progress = (st.session_state.current_question_index + 1) / len(questions)
    st.progress(progress)
    st.caption(f"Domanda {st.session_state.current_question_index + 1} di {len(questions)}")
    
    # Domanda corrente
    current_question = questions[st.session_state.current_question_index]
    
    # Mostra informazioni sulla domanda
    st.markdown("---")
    
    # Informazioni di contesto
    col1, col2 = st.columns(2)
    with col1:
        channel_name = current_question.get('channel', 'N/A')
        if channel_name and channel_name.startswith('n.'):
            channel_name = channel_name.split(' ', 1)[1] if ' ' in channel_name else channel_name
        st.markdown(f"**🎯 Canale:** {channel_name}")
    with col2:
        factor_name = current_question.get('factor', 'N/A')
        factor_display = {
            'env': 'Environmental',
            'org': 'Organizational', 
            'ind': 'Individual'
        }.get(factor_name, factor_name)
        st.markdown(f"**📊 Fattore:** {factor_display}")
    
    # Testo della domanda
    st.markdown("### 📋 Domanda")
    st.markdown(f"*{current_question['question']}*")
    
    # Input per la risposta
    response_key = f"q_{st.session_state.current_question_index}"
    
    st.markdown("### 💭 La tua risposta")
    
    if current_question['type'] == 'likert':
        # Scala Likert
        scale_labels = current_question.get('scale_labels', {
            1: "Strongly disagree", 2: "Disagree", 3: "Somewhat disagree",
            4: "Neutral", 5: "Somewhat agree", 6: "Agree", 7: "Strongly agree"
        })
        
        response = st.radio(
            "Seleziona il tuo livello di accordo:",
            options=[1, 2, 3, 4, 5, 6, 7],
            format_func=lambda x: f"{x} - {scale_labels.get(x, '')}",
            key=response_key,
            index=st.session_state.responses.get(response_key, 4) - 1 if st.session_state.responses.get(response_key) else 3,
            horizontal=True
        )
        
    else:  # yes/no
        response = st.radio(
            "Seleziona la tua risposta:",
            options=['Yes', 'No'],
            key=response_key,
            index=0 if st.session_state.responses.get(response_key) == 'Yes' else 1 if st.session_state.responses.get(response_key) == 'No' else 0,
            horizontal=True
        )
    
    # Campo aperto per commenti
    comment_key = f"comment_{st.session_state.current_question_index}"
    comment = st.text_area(
        "💬 Commenti aggiuntivi (opzionale):",
        value=st.session_state.responses.get(comment_key, ''),
        key=comment_key,
        height=100,
        placeholder="Aggiungi qui eventuali commenti, contesto o spiegazioni aggiuntive..."
    )
    
    # Salva le risposte
    st.session_state.responses[response_key] = response
    if comment:
        st.session_state.responses[comment_key] = comment
    
    st.markdown("---")
    
    # Navigazione
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col1:
        if st.session_state.current_question_index > 0:
            if st.button("⬅️ Precedente", use_container_width=True):
                st.session_state.current_question_index -= 1
                st.rerun()
    
    with col2:
        # Mostra canale/fattore corrente
        st.markdown(f"<div style='text-align: center; color: #666;'><small>{channel_name} | {factor_display}</small></div>", unsafe_allow_html=True)
    
    with col3:
        if st.session_state.current_question_index < len(questions) - 1:
            if st.button("Successiva ➡️", use_container_width=True):
                st.session_state.current_question_index += 1
                st.rerun()
        else:
            if st.button("✅ Completa Assessment", type="primary", use_container_width=True):
                st.session_state.assessment_completed = True
                st.session_state.current_page = 'Results'
                st.success("🎉 Assessment completato! Generazione risultati...")
                st.rerun()
    
    # Sidebar con riepilogo progresso
    with st.sidebar:
        st.markdown("### 📈 Progresso Assessment")
        st.progress(progress)
        st.caption(f"{st.session_state.current_question_index + 1}/{len(questions)} domande completate")
        
        # Mostra risposte date
        answered = len([k for k in st.session_state.responses.keys() if k.startswith('q_')])
        st.metric("Risposte date", answered, f"{answered}/{len(questions)}")
        
        # Quick navigation (opzionale)
        if st.checkbox("🔍 Navigazione rapida"):
            question_jump = st.selectbox(
                "Vai alla domanda:",
                range(len(questions)),
                index=st.session_state.current_question_index,
                format_func=lambda x: f"Domanda {x+1}"
            )
            if question_jump != st.session_state.current_question_index:
                st.session_state.current_question_index = question_jump
                st.rerun()

def render_results_page():
    """Renderizza la pagina dei risultati"""
    st.title("📊 Risultati Assessment")
    
    if not st.session_state.assessment_completed:
        st.warning("⚠️ Completa prima l'assessment per vedere i risultati.")
        if st.button("📝 Vai all'Assessment"):
            st.session_state.current_page = 'Assessment'
            st.rerun()
        return
    
    # Calcola i punteggi
    scores = calculate_scores()
    
    # Mostra punteggi principali
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Punteggio Totale", f"{scores['total']:.2f}/7", f"vs Bologna: {scores['total'] - 5.76:.2f}")
    
    with col2:
        st.metric("Domande Completate", scores['completed'], f"{scores['completed']}/{scores['total_questions']}")
    
    with col3:
        st.metric("Livello Maturità", get_maturity_level(scores['total']))
    
    # Visualizzazioni
    st.subheader("📈 Punteggi per Canale")
    
    # Grafico radar
    fig = create_radar_chart(scores['by_channel'])
    st.plotly_chart(fig, use_container_width=True)
    
    # Tabella dettagliata
    st.subheader("📋 Dettaglio Punteggi")
    df_scores = pd.DataFrame([
        {
            'Canale': channel,
            'Punteggio': score,
            'Livello': get_maturity_level(score)
        }
        for channel, score in scores['by_channel'].items()
    ])
    st.dataframe(df_scores, use_container_width=True)
    
    # Insights AI
    st.subheader("🤖 Insights AI-Generated")
    insights = generate_insights(scores, st.session_state.responses)
    st.markdown(insights)
    
    # Download risultati
    st.subheader("💾 Download Risultati")
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📄 Download JSON", use_container_width=True):
            results_json = json.dumps({
                'user_info': st.session_state.user_info,
                'scores': scores,
                'responses': st.session_state.responses,
                'timestamp': datetime.now().isoformat()
            }, indent=2)
            st.download_button(
                label="💾 Scarica JSON",
                data=results_json,
                file_name=f"assessment_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )
    
    with col2:
        if st.button("📊 Download CSV", use_container_width=True):
            csv_data = df_scores.to_csv(index=False)
            st.download_button(
                label="💾 Scarica CSV",
                data=csv_data,
                file_name=f"assessment_scores_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )

def render_dashboard_page():
    """Renderizza la dashboard avanzata"""
    st.title("📊 Dashboard Avanzata")
    
    if not st.session_state.assessment_completed:
        st.warning("⚠️ Completa prima l'assessment per vedere la dashboard.")
        return
    
    # Metriche avanzate
    scores = calculate_scores()
    
    # Confronto con benchmark
    st.subheader("🎯 Confronto con Benchmark Bologna")
    
    bologna_scores = {
        'Academia-Industry joint research & mobility': 5.8,
        'Promoting research-driven spin-offs and start-ups': 5.5,
        'Intermediaries and knowledge transfer professionals': 5.9,
        'Engagement of citizens, public bodies and societal actors': 5.7,
        'Intellectual Property management & Standardisation': 5.8,
        'Knowledge circulation & informing policy': 5.9
    }
    
    # Grafico comparativo
    fig = create_comparison_chart(scores['by_channel'], bologna_scores)
    st.plotly_chart(fig, use_container_width=True)
    
    # Analisi per fattore
    st.subheader("🔍 Analisi per Fattore")
    factor_scores = calculate_factor_scores()
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Environmental", f"{factor_scores['env']:.2f}/7")
    with col2:
        st.metric("Organizational", f"{factor_scores['org']:.2f}/7")
    with col3:
        st.metric("Individual", f"{factor_scores['ind']:.2f}/7")

def calculate_scores():
    """Calcola i punteggi dell'assessment"""
    questions = load_questions()
    responses = st.session_state.responses
    
    # Conta risposte completate
    completed = len([k for k in responses.keys() if k.startswith('q_')])
    
    # Calcola punteggi per canale
    channel_scores = {}
    
    for question in questions:
        channel = question.get('channel', 'Unknown')
        if channel.startswith('n.'):
            channel = channel.split(' ', 1)[1] if ' ' in channel else channel
        
        response_key = f"q_{questions.index(question)}"
        if response_key in responses:
            response = responses[response_key]
            
            # Normalizza la risposta su scala 1-7
            if question['type'] == 'likert':
                score = response
            else:  # yes/no
                score = 7 if response == 'Yes' else 1
            
            if channel not in channel_scores:
                channel_scores[channel] = []
            channel_scores[channel].append(score)
    
    # Calcola medie per canale
    channel_averages = {
        channel: sum(scores) / len(scores) if scores else 0
        for channel, scores in channel_scores.items()
    }
    
    # Punteggio totale
    total_score = sum(channel_averages.values()) / len(channel_averages) if channel_averages else 0
    
    return {
        'total': total_score,
        'by_channel': channel_averages,
        'completed': completed,
        'total_questions': len(questions)
    }

def calculate_factor_scores():
    """Calcola i punteggi per fattore"""
    questions = load_questions()
    responses = st.session_state.responses
    
    factor_scores = {'env': [], 'org': [], 'ind': []}
    
    for question in questions:
        factor = question.get('factor')
        response_key = f"q_{questions.index(question)}"
        
        if factor in factor_scores and response_key in responses:
            response = responses[response_key]
            
            # Normalizza la risposta
            if question['type'] == 'likert':
                score = response
            else:  # yes/no
                score = 7 if response == 'Yes' else 1
            
            factor_scores[factor].append(score)
    
    # Calcola medie
    return {
        factor: sum(scores) / len(scores) if scores else 0
        for factor, scores in factor_scores.items()
    }

def get_maturity_level(score):
    """Determina il livello di maturità basato sul punteggio"""
    if score < 4.0:
        return "Iniziale"
    elif score < 5.0:
        return "Base"
    elif score < 6.0:
        return "Intermedio"
    else:
        return "Avanzato"

def create_radar_chart(channel_scores):
    """Crea un grafico radar per i punteggi dei canali"""
    categories = list(channel_scores.keys())
    values = list(channel_scores.values())
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        name='Punteggi'
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 7]
            )),
        showlegend=True,
        title="Punteggi per Canale"
    )
    
    return fig

def create_comparison_chart(user_scores, bologna_scores):
    """Crea un grafico di confronto con Bologna"""
    channels = list(user_scores.keys())
    user_values = list(user_scores.values())
    bologna_values = [bologna_scores.get(channel, 0) for channel in channels]
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        name='I tuoi punteggi',
        x=channels,
        y=user_values,
        marker_color='lightblue'
    ))
    
    fig.add_trace(go.Bar(
        name='Bologna (benchmark)',
        x=channels,
        y=bologna_values,
        marker_color='orange'
    ))
    
    fig.update_layout(
        barmode='group',
        title='Confronto con il Caso Bologna',
        xaxis_title='Canali',
        yaxis_title='Punteggio (1-7)',
        yaxis=dict(range=[0, 7])
    )
    
    return fig

def generate_insights(scores, responses):
    """Genera insights basati sui risultati"""
    total_score = scores['total']
    
    insights = f"""
    ## 🎯 Executive Summary
    
    Il tuo punteggio complessivo è **{total_score:.2f}/7**, che corrisponde a un livello di maturità **{get_maturity_level(total_score)}**.
    
    ### 🔍 Analisi Principale
    
    """
    
    if total_score >= 6.0:
        insights += """
        **Eccellente!** La tua organizzazione dimostra un alto livello di maturità nella valorizzazione della conoscenza. 
        Continua a mantenere questi standard elevati e considera di diventare un punto di riferimento per altre organizzazioni.
        """
    elif total_score >= 5.0:
        insights += """
        **Buono!** La tua organizzazione ha una solida base nella valorizzazione della conoscenza. 
        Ci sono opportunità di miglioramento in alcune aree specifiche che potrebbero portare a risultati ancora migliori.
        """
    elif total_score >= 4.0:
        insights += """
        **In sviluppo.** La tua organizzazione sta costruendo le capacità di valorizzazione della conoscenza. 
        È importante concentrarsi su miglioramenti strutturati e sistematici.
        """
    else:
        insights += """
        **Fase iniziale.** C'è molto potenziale di crescita nella valorizzazione della conoscenza. 
        Considera di sviluppare una strategia strutturata per migliorare le capacità organizzative.
        """
    
    # Analisi per canale
    insights += "\n### 📊 Punti di Forza e Aree di Miglioramento\n\n"
    
    sorted_channels = sorted(scores['by_channel'].items(), key=lambda x: x[1], reverse=True)
    
    best_channel = sorted_channels[0]
    worst_channel = sorted_channels[-1]
    
    insights += f"""
    **Punto di forza principale:** {best_channel[0]} (punteggio: {best_channel[1]:.2f})
    
    **Area di miglioramento prioritaria:** {worst_channel[0]} (punteggio: {worst_channel[1]:.2f})
    """
    
    return insights

def main():
    """Funzione principale dell'applicazione"""
    # Inizializza lo stato della sessione
    initialize_session_state()
    
    # Renderizza la sidebar
    render_sidebar()
    
    # Renderizza la pagina corrente
    if st.session_state.current_page == 'Home':
        render_home_page()
    elif st.session_state.current_page == 'Assessment':
        render_assessment_page()
    elif st.session_state.current_page == 'Results':
        render_results_page()
    elif st.session_state.current_page == 'Dashboard':
        render_dashboard_page()

if __name__ == "__main__":
    main()

