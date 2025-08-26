import openai
import os
from typing import Dict, List, Any, Optional
import json
import re
from textblob import TextBlob

class InsightGenerator:
    """
    Genera insights narrativi usando AI per l'analisi semantica e del sentiment
    """
    
    def __init__(self, api_key: Optional[str] = None):
        self.client = None
        if api_key or os.getenv('OPENAI_API_KEY'):
            try:
                self.client = openai.OpenAI(api_key=api_key or os.getenv('OPENAI_API_KEY'))
            except Exception as e:
                print(f"Errore nell'inizializzazione OpenAI: {e}")
        
        self.channels = {
            1: "Joint Research & Co-creation",
            2: "Shared Infrastructure & Resources", 
            3: "Knowledge & Technology Transfer",
            4: "Entrepreneurship & Spin-offs",
            5: "Mobility & Skills Development",
            6: "Regional Innovation Ecosystem"
        }
        
        self.factors = {
            'env': 'Environmental (policy, regulatory)',
            'org': 'Organizational (internal processes)', 
            'ind': 'Individual (personal, skills)'
        }
    
    def extract_open_responses(self, responses: Dict[str, Any]) -> Dict[str, str]:
        """
        Estrae le risposte aperte dai commenti
        
        Args:
            responses: Dizionario delle risposte
            
        Returns:
            Dict con le risposte aperte organizzate
        """
        open_responses = {}
        
        for key, value in responses.items():
            if key.startswith('comment_') and value and value.strip():
                question_id = key.replace('comment_', '')
                open_responses[question_id] = value.strip()
        
        return open_responses
    
    def perform_sentiment_analysis(self, text_responses: List[str]) -> Dict[str, Any]:
        """
        Analizza il sentiment delle risposte testuali
        
        Args:
            text_responses: Lista di risposte testuali
            
        Returns:
            Dict con analisi del sentiment
        """
        if not text_responses:
            return {
                'overall_sentiment': 'neutral',
                'polarity': 0.0,
                'subjectivity': 0.0,
                'positive_count': 0,
                'negative_count': 0,
                'neutral_count': 0
            }
        
        sentiments = []
        polarities = []
        subjectivities = []
        
        positive_count = 0
        negative_count = 0
        neutral_count = 0
        
        for text in text_responses:
            try:
                blob = TextBlob(text)
                polarity = blob.sentiment.polarity
                subjectivity = blob.sentiment.subjectivity
                
                polarities.append(polarity)
                subjectivities.append(subjectivity)
                
                if polarity > 0.1:
                    sentiments.append('positive')
                    positive_count += 1
                elif polarity < -0.1:
                    sentiments.append('negative')
                    negative_count += 1
                else:
                    sentiments.append('neutral')
                    neutral_count += 1
                    
            except Exception as e:
                print(f"Errore nell'analisi sentiment: {e}")
                sentiments.append('neutral')
                neutral_count += 1
        
        avg_polarity = sum(polarities) / len(polarities) if polarities else 0.0
        avg_subjectivity = sum(subjectivities) / len(subjectivities) if subjectivities else 0.0
        
        # Determina sentiment generale
        if avg_polarity > 0.1:
            overall_sentiment = 'positive'
        elif avg_polarity < -0.1:
            overall_sentiment = 'negative'
        else:
            overall_sentiment = 'neutral'
        
        return {
            'overall_sentiment': overall_sentiment,
            'polarity': avg_polarity,
            'subjectivity': avg_subjectivity,
            'positive_count': positive_count,
            'negative_count': negative_count,
            'neutral_count': neutral_count,
            'total_responses': len(text_responses)
        }
    
    def extract_key_themes(self, text_responses: List[str]) -> List[str]:
        """
        Estrae temi chiave dalle risposte testuali
        
        Args:
            text_responses: Lista di risposte testuali
            
        Returns:
            Lista di temi identificati
        """
        if not text_responses:
            return []
        
        # Combina tutti i testi
        combined_text = ' '.join(text_responses).lower()
        
        # Parole chiave comuni nel dominio knowledge valorisation
        domain_keywords = [
            'collaboration', 'partnership', 'innovation', 'research', 'technology',
            'transfer', 'industry', 'academia', 'university', 'spin-off', 'startup',
            'intellectual property', 'ip', 'licensing', 'commercialization',
            'entrepreneurship', 'incubator', 'accelerator', 'funding', 'investment',
            'skills', 'training', 'mobility', 'exchange', 'network', 'ecosystem',
            'policy', 'regulation', 'governance', 'framework', 'strategy'
        ]
        
        # Trova temi presenti
        found_themes = []
        for keyword in domain_keywords:
            if keyword in combined_text:
                found_themes.append(keyword.title())
        
        return found_themes[:10]  # Limita a 10 temi principali
    
    def generate_channel_narrative(self, channel_num: int, channel_data: Dict[str, Any], 
                                 open_responses: Dict[str, str], 
                                 sentiment_analysis: Dict[str, Any]) -> str:
        """
        Genera narrativa per un canale specifico
        
        Args:
            channel_num: Numero del canale
            channel_data: Dati del canale (punteggi, fattori)
            open_responses: Risposte aperte relative al canale
            sentiment_analysis: Analisi del sentiment
            
        Returns:
            str: Narrativa generata
        """
        channel_name = self.channels[channel_num]
        score = channel_data['score']
        factors = channel_data['factors']
        
        # Template base per la narrativa
        if self.client:
            return self._generate_ai_narrative(channel_name, score, factors, open_responses, sentiment_analysis)
        else:
            return self._generate_template_narrative(channel_name, score, factors, sentiment_analysis)
    
    def _generate_ai_narrative(self, channel_name: str, score: float, factors: Dict[str, float],
                              open_responses: Dict[str, str], sentiment_analysis: Dict[str, Any]) -> str:
        """
        Genera narrativa usando OpenAI API
        """
        try:
            # Prepara il contesto per l'AI
            context = f"""
            Canale: {channel_name}
            Punteggio complessivo: {score:.2f}/7
            
            Punteggi per fattore:
            - Environmental: {factors.get('env', 0):.2f}/7
            - Organizational: {factors.get('org', 0):.2f}/7
            - Individual: {factors.get('ind', 0):.2f}/7
            
            Sentiment generale: {sentiment_analysis.get('overall_sentiment', 'neutral')}
            Polarità: {sentiment_analysis.get('polarity', 0):.2f}
            
            Risposte aperte: {'; '.join(open_responses.values()) if open_responses else 'Nessuna risposta aperta'}
            """
            
            prompt = f"""
            Basandoti sui seguenti dati del self-assessment per il canale "{channel_name}":
            
            {context}
            
            Genera un insight narrativo professionale che includa:
            1. Analisi della situazione attuale
            2. Identificazione di punti di forza specifici
            3. Sfide e barriere identificate
            4. Opportunità di miglioramento concrete
            5. Raccomandazioni specifiche e attuabili
            
            Stile: Professionale, analitico, simile al caso Bologna.
            Lunghezza: 150-200 parole.
            Lingua: Italiano.
            """
            
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "Sei un esperto in knowledge valorisation e collaborazione industria-accademia. Genera insights professionali basati sui dati di assessment."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"Errore nella generazione AI: {e}")
            return self._generate_template_narrative(channel_name, score, factors, sentiment_analysis)
    
    def _generate_template_narrative(self, channel_name: str, score: float, 
                                   factors: Dict[str, float], sentiment_analysis: Dict[str, Any]) -> str:
        """
        Genera narrativa usando template predefiniti
        """
        # Determina il livello di performance
        if score >= 6.0:
            performance_level = "eccellente"
            performance_desc = "mostra una performance eccellente"
        elif score >= 5.0:
            performance_level = "buona"
            performance_desc = "presenta una buona performance"
        elif score >= 4.0:
            performance_level = "media"
            performance_desc = "mostra una performance nella media"
        else:
            performance_level = "da migliorare"
            performance_desc = "presenta aree significative di miglioramento"
        
        # Identifica il fattore più forte e più debole
        env_score = factors.get('env', 4.0)
        org_score = factors.get('org', 4.0)
        ind_score = factors.get('ind', 4.0)
        
        factor_scores = {'Environmental': env_score, 'Organizational': org_score, 'Individual': ind_score}
        strongest_factor = max(factor_scores, key=factor_scores.get)
        weakest_factor = min(factor_scores, key=factor_scores.get)
        
        # Sentiment
        sentiment = sentiment_analysis.get('overall_sentiment', 'neutral')
        sentiment_desc = {
            'positive': 'un atteggiamento positivo',
            'negative': 'alcune preoccupazioni',
            'neutral': 'un approccio equilibrato'
        }.get(sentiment, 'un approccio equilibrato')
        
        narrative = f"""
        **Situazione Attuale:** Il canale {channel_name} {performance_desc} con un punteggio di {score:.2f}/7. 
        L'analisi rivela {sentiment_desc} verso questo ambito della valorizzazione della conoscenza.
        
        **Punti di Forza:** Il fattore {strongest_factor.lower()} emerge come area di eccellenza 
        ({factor_scores[strongest_factor]:.2f}/7), indicando una solida base in questo aspetto.
        
        **Aree di Miglioramento:** Il fattore {weakest_factor.lower()} presenta opportunità di sviluppo 
        ({factor_scores[weakest_factor]:.2f}/7) e potrebbe beneficiare di interventi mirati.
        
        **Raccomandazioni:** Concentrarsi sul rafforzamento degli aspetti {weakest_factor.lower()} 
        mantenendo l'eccellenza negli aspetti {strongest_factor.lower()}. Implementare strategie 
        specifiche per questo canale basate sulle best practice del settore.
        """
        
        return narrative.strip()
    
    def create_executive_summary(self, all_scores: Dict[str, Any], 
                               all_responses: Dict[str, Any]) -> str:
        """
        Crea un executive summary generale dell'assessment
        
        Args:
            all_scores: Tutti i punteggi calcolati
            all_responses: Tutte le risposte dell'utente
            
        Returns:
            str: Executive summary
        """
        total_score = all_scores['total_score']
        channels = all_scores['channels']
        
        # Identifica canali migliori e peggiori
        channel_scores = {data['name']: data['score'] for data in channels.values()}
        best_channel = max(channel_scores, key=channel_scores.get)
        worst_channel = min(channel_scores, key=channel_scores.get)
        
        # Analisi sentiment generale
        open_responses = self.extract_open_responses(all_responses)
        sentiment = self.perform_sentiment_analysis(list(open_responses.values()))
        
        # Confronto con Bologna
        bologna_score = 5.76
        comparison = "superiore" if total_score > bologna_score else "inferiore" if total_score < bologna_score else "equivalente"
        
        if self.client:
            return self._generate_ai_executive_summary(total_score, best_channel, worst_channel, sentiment, comparison)
        else:
            return self._generate_template_executive_summary(total_score, best_channel, worst_channel, sentiment, comparison)
    
    def _generate_template_executive_summary(self, total_score: float, best_channel: str, 
                                           worst_channel: str, sentiment: Dict[str, Any], 
                                           comparison: str) -> str:
        """
        Genera executive summary con template
        """
        maturity_level = "avanzato" if total_score >= 6.0 else "intermedio" if total_score >= 5.0 else "base" if total_score >= 4.0 else "iniziale"
        
        summary = f"""
        **Valutazione Complessiva:** L'organizzazione presenta un livello di maturità {maturity_level} 
        nella valorizzazione della conoscenza, con un punteggio totale di {total_score:.2f}/7.
        
        **Punti di Forza Principali:**
        • {best_channel} emerge come area di eccellenza
        • Atteggiamento generale {sentiment.get('overall_sentiment', 'equilibrato')} verso la collaborazione
        • Performance {comparison} rispetto al benchmark del caso Bologna
        
        **Aree di Miglioramento:**
        • {worst_channel} richiede attenzione prioritaria
        • Necessità di strategie integrate per il miglioramento continuo
        • Opportunità di apprendimento dalle best practice internazionali
        
        **Raccomandazioni Strategiche:**
        • Sviluppare un piano d'azione focalizzato su {worst_channel}
        • Capitalizzare sui successi in {best_channel} per guidare il miglioramento
        • Implementare meccanismi di monitoraggio e valutazione continua
        """
        
        return summary.strip()
    
    def _generate_ai_executive_summary(self, total_score: float, best_channel: str, 
                                     worst_channel: str, sentiment: Dict[str, Any], 
                                     comparison: str) -> str:
        """
        Genera executive summary usando AI
        """
        try:
            prompt = f"""
            Genera un executive summary per un assessment di knowledge valorisation con i seguenti risultati:
            
            - Punteggio totale: {total_score:.2f}/7
            - Canale migliore: {best_channel}
            - Canale da migliorare: {worst_channel}
            - Sentiment generale: {sentiment.get('overall_sentiment', 'neutral')}
            - Performance vs Bologna: {comparison}
            
            Include:
            1. Valutazione complessiva del livello di maturità
            2. Top 3 punti di forza
            3. Top 3 aree di miglioramento
            4. Raccomandazioni strategiche concrete
            
            Stile: Executive-level, strategico, actionable.
            Lunghezza: 200-250 parole.
            Lingua: Italiano.
            """
            
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "Sei un consulente senior specializzato in knowledge valorisation. Genera executive summary strategici e actionable."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=600,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"Errore nella generazione AI executive summary: {e}")
            return self._generate_template_executive_summary(total_score, best_channel, worst_channel, sentiment, comparison)

