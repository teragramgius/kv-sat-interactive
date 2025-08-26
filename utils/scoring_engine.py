import numpy as np
import pandas as pd
from typing import Dict, List, Any, Tuple

class ScoringEngine:
    """
    Calcola i punteggi dell'assessment basandosi sulla metodologia Bologna
    """
    
    def __init__(self):
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
        
        # Mapping domande a canali e fattori (semplificato per demo)
        self.question_mapping = self._create_question_mapping()
    
    def _create_question_mapping(self) -> Dict[str, Dict[str, Any]]:
        """
        Crea il mapping delle domande ai canali e fattori
        Questo dovrebbe essere caricato dal file Excel in una versione completa
        """
        mapping = {}
        
        # Esempio di mapping per le prime domande
        questions_per_channel = 9  # 54 domande / 6 canali
        
        for i in range(54):
            channel = (i // questions_per_channel) + 1
            factor_index = i % 3
            factor = ['env', 'org', 'ind'][factor_index]
            
            mapping[f"q_{i}"] = {
                'channel': channel,
                'factor': factor,
                'type': 'likert' if i < 48 else 'yesno'
            }
        
        return mapping
    
    def normalize_response(self, response: Any, question_type: str) -> float:
        """
        Normalizza le risposte su scala 1-7
        
        Args:
            response: Risposta dell'utente
            question_type: Tipo di domanda ('likert' o 'yesno')
            
        Returns:
            float: Valore normalizzato 1-7
        """
        if question_type == 'likert':
            return float(response) if response is not None else 4.0  # Default neutro
        elif question_type == 'yesno':
            if response == 'Yes':
                return 7.0
            elif response == 'No':
                return 1.0
            else:
                return 4.0  # Default neutro per risposte mancanti
        else:
            return 4.0
    
    def calculate_factor_score(self, responses: Dict[str, Any], factor: str, channel: int) -> float:
        """
        Calcola il punteggio per un fattore specifico in un canale
        
        Args:
            responses: Dizionario delle risposte
            factor: Fattore ('env', 'org', 'ind')
            channel: Numero del canale (1-6)
            
        Returns:
            float: Punteggio medio per il fattore
        """
        relevant_scores = []
        
        for question_id, mapping in self.question_mapping.items():
            if mapping['channel'] == channel and mapping['factor'] == factor:
                if question_id in responses:
                    normalized_score = self.normalize_response(
                        responses[question_id], 
                        mapping['type']
                    )
                    relevant_scores.append(normalized_score)
        
        return np.mean(relevant_scores) if relevant_scores else 4.0
    
    def calculate_channel_score(self, responses: Dict[str, Any], channel: int) -> Dict[str, float]:
        """
        Calcola i punteggi per tutti i fattori di un canale
        
        Args:
            responses: Dizionario delle risposte
            channel: Numero del canale (1-6)
            
        Returns:
            Dict con punteggi per fattore e punteggio medio del canale
        """
        factor_scores = {}
        
        for factor in self.factors.keys():
            factor_scores[factor] = self.calculate_factor_score(responses, factor, channel)
        
        # Calcola il punteggio medio del canale
        channel_score = np.mean(list(factor_scores.values()))
        
        return {
            'factors': factor_scores,
            'channel_average': channel_score
        }
    
    def calculate_all_scores(self, responses: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calcola tutti i punteggi dell'assessment
        
        Args:
            responses: Dizionario completo delle risposte
            
        Returns:
            Dict con tutti i punteggi calcolati
        """
        results = {
            'channels': {},
            'factors_summary': {factor: [] for factor in self.factors.keys()},
            'total_score': 0.0,
            'response_count': 0,
            'completion_rate': 0.0
        }
        
        channel_scores = []
        
        # Calcola punteggi per ogni canale
        for channel_num in self.channels.keys():
            channel_result = self.calculate_channel_score(responses, channel_num)
            
            results['channels'][channel_num] = {
                'name': self.channels[channel_num],
                'score': channel_result['channel_average'],
                'factors': channel_result['factors']
            }
            
            channel_scores.append(channel_result['channel_average'])
            
            # Aggrega i fattori per il summary
            for factor, score in channel_result['factors'].items():
                results['factors_summary'][factor].append(score)
        
        # Calcola punteggio totale
        results['total_score'] = np.mean(channel_scores)
        
        # Calcola statistiche di completamento
        total_questions = len(self.question_mapping)
        answered_questions = len([r for r in responses.values() if r is not None])
        results['response_count'] = answered_questions
        results['completion_rate'] = answered_questions / total_questions if total_questions > 0 else 0
        
        # Calcola medie per fattore
        for factor in self.factors.keys():
            if results['factors_summary'][factor]:
                results['factors_summary'][factor] = np.mean(results['factors_summary'][factor])
            else:
                results['factors_summary'][factor] = 4.0
        
        return results
    
    def get_performance_insights(self, scores: Dict[str, Any]) -> Dict[str, Any]:
        """
        Genera insights sulla performance basati sui punteggi
        
        Args:
            scores: Risultati del calcolo dei punteggi
            
        Returns:
            Dict con insights e raccomandazioni
        """
        insights = {
            'strengths': [],
            'weaknesses': [],
            'recommendations': [],
            'benchmark_comparison': {},
            'maturity_level': ''
        }
        
        # Identifica punti di forza (punteggi > 6.0)
        for channel_num, channel_data in scores['channels'].items():
            if channel_data['score'] > 6.0:
                insights['strengths'].append({
                    'channel': channel_data['name'],
                    'score': channel_data['score'],
                    'description': f"Eccellente performance in {channel_data['name']}"
                })
        
        # Identifica aree di miglioramento (punteggi < 5.0)
        for channel_num, channel_data in scores['channels'].items():
            if channel_data['score'] < 5.0:
                insights['weaknesses'].append({
                    'channel': channel_data['name'],
                    'score': channel_data['score'],
                    'description': f"Area di miglioramento in {channel_data['name']}"
                })
        
        # Determina livello di maturità
        total_score = scores['total_score']
        if total_score >= 6.0:
            insights['maturity_level'] = 'Avanzato'
        elif total_score >= 5.0:
            insights['maturity_level'] = 'Intermedio'
        elif total_score >= 4.0:
            insights['maturity_level'] = 'Base'
        else:
            insights['maturity_level'] = 'Iniziale'
        
        # Confronto con benchmark Bologna (5.76)
        bologna_benchmark = 5.76
        insights['benchmark_comparison'] = {
            'bologna_score': bologna_benchmark,
            'difference': total_score - bologna_benchmark,
            'performance': 'Sopra' if total_score > bologna_benchmark else 'Sotto' if total_score < bologna_benchmark else 'Pari'
        }
        
        return insights
    
    def export_detailed_scores(self, scores: Dict[str, Any]) -> pd.DataFrame:
        """
        Esporta i punteggi dettagliati in formato DataFrame
        
        Args:
            scores: Risultati del calcolo dei punteggi
            
        Returns:
            DataFrame con i punteggi dettagliati
        """
        rows = []
        
        for channel_num, channel_data in scores['channels'].items():
            for factor, factor_score in channel_data['factors'].items():
                rows.append({
                    'channel_number': channel_num,
                    'channel_name': channel_data['name'],
                    'factor': factor,
                    'factor_name': self.factors[factor],
                    'factor_score': factor_score,
                    'channel_score': channel_data['score']
                })
        
        df = pd.DataFrame(rows)
        df['total_score'] = scores['total_score']
        
        return df

