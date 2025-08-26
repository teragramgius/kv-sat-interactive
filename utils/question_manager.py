import pandas as pd
import json
import os
from typing import List, Dict, Any

class QuestionManager:
    """Gestisce il caricamento e l'organizzazione delle domande del self-assessment"""
    
    def __init__(self):
        self.questions = []
        self.channels = {}
        self.factors = ['env', 'org', 'ind']
        
    def load_questions_from_excel(self, file_path: str) -> List[Dict[str, Any]]:
        """Carica tutte le domande reali dal file Excel"""
        try:
            if not os.path.exists(file_path):
                print(f"File Excel non trovato: {file_path}")
                return self._get_fallback_questions()
            
            # Leggi il foglio del self-assessment tool
            df = pd.read_excel(file_path, sheet_name='1) self-assessment tool')
            
            # Estrai domande con struttura gerarchica
            structured_questions = self._extract_structured_questions(df)
            
            # Organizza per canali e fattori
            self._organize_questions(structured_questions)
            
            print(f"✅ Caricate {len(structured_questions)} domande reali dal file Excel")
            return structured_questions
            
        except Exception as e:
            print(f"❌ Errore nel caricamento del file Excel: {e}")
            return self._get_fallback_questions()
    
    def _extract_structured_questions(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Estrae le domande mantenendo la struttura gerarchica"""
        structured_questions = []
        
        current_channel = None
        current_factor = None
        current_actor = None
        question_counter = 0
        
        for i, row in df.iterrows():
            # Aggiorna il contesto corrente
            if pd.notna(row['CHANNELS']) and str(row['CHANNELS']).strip():
                current_channel = str(row['CHANNELS']).strip()
            
            if pd.notna(row['FACTORS']) and str(row['FACTORS']).strip():
                current_factor = str(row['FACTORS']).strip()
            
            if pd.notna(row['ACTORS']) and str(row['ACTORS']).strip():
                current_actor = str(row['ACTORS']).strip()
            
            # Estrai domande Likert
            likert_col = '1 - Strongly disagree / Not at all true | 7 - Strongly agree / Fully true'
            if pd.notna(row[likert_col]) and str(row[likert_col]).strip() and len(str(row[likert_col]).strip()) > 10:
                question = {
                    'id': f"q_{question_counter}",
                    'question': str(row[likert_col]).strip(),
                    'type': 'likert',
                    'channel': current_channel,
                    'factor': current_factor,
                    'actor': current_actor,
                    'scale': [1, 2, 3, 4, 5, 6, 7],
                    'scale_labels': {
                        1: "Strongly disagree",
                        2: "Disagree", 
                        3: "Somewhat disagree",
                        4: "Neutral",
                        5: "Somewhat agree",
                        6: "Agree",
                        7: "Strongly agree"
                    }
                }
                structured_questions.append(question)
                question_counter += 1
            
            # Estrai domande Yes/No
            yesno_col = 'yes/no'
            if pd.notna(row[yesno_col]) and str(row[yesno_col]).strip() and len(str(row[yesno_col]).strip()) > 10:
                question = {
                    'id': f"q_{question_counter}",
                    'question': str(row[yesno_col]).strip(),
                    'type': 'yesno',
                    'channel': current_channel,
                    'factor': current_factor,
                    'actor': current_actor,
                    'options': ['Yes', 'No']
                }
                structured_questions.append(question)
                question_counter += 1
        
        return structured_questions
    
    def _organize_questions(self, questions: List[Dict[str, Any]]):
        """Organizza le domande per canali e fattori"""
        self.channels = {}
        
        for question in questions:
            channel = question['channel']
            factor = question['factor']
            
            if not channel or not factor:
                continue
                
            if channel not in self.channels:
                self.channels[channel] = {
                    'name': self._clean_channel_name(channel),
                    'factors': {}
                }
            
            if factor not in self.channels[channel]['factors']:
                self.channels[channel]['factors'][factor] = {
                    'name': self._get_factor_name(factor),
                    'questions': []
                }
            
            self.channels[channel]['factors'][factor]['questions'].append(question)
    
    def _clean_channel_name(self, channel: str) -> str:
        """Pulisce il nome del canale per la visualizzazione"""
        # Rimuovi il numero e pulisci
        if channel.startswith('n.'):
            parts = channel.split(' ', 1)
            if len(parts) > 1:
                return parts[1].strip()
        return channel.strip()
    
    def _get_factor_name(self, factor: str) -> str:
        """Converte il codice fattore in nome leggibile"""
        factor_names = {
            'env': 'Environmental',
            'org': 'Organizational', 
            'ind': 'Individual'
        }
        return factor_names.get(factor, factor)
    
    def get_questions_by_channel(self, channel: str) -> Dict[str, Any]:
        """Restituisce tutte le domande per un canale specifico"""
        return self.channels.get(channel, {})
    
    def get_all_channels(self) -> List[str]:
        """Restituisce la lista di tutti i canali"""
        return list(self.channels.keys())
    
    def get_channel_summary(self) -> Dict[str, Dict[str, int]]:
        """Restituisce un riepilogo del numero di domande per canale/fattore"""
        summary = {}
        for channel, data in self.channels.items():
            summary[channel] = {}
            for factor, factor_data in data['factors'].items():
                summary[channel][factor] = len(factor_data['questions'])
        return summary
    
    def get_all_questions(self) -> List[Dict[str, Any]]:
        """Restituisce tutte le domande in una lista piatta"""
        all_questions = []
        for channel, channel_data in self.channels.items():
            for factor, factor_data in channel_data['factors'].items():
                all_questions.extend(factor_data['questions'])
        return all_questions
    
    def get_question_by_id(self, question_id: str) -> Dict[str, Any]:
        """Restituisce una domanda specifica per ID"""
        for question in self.get_all_questions():
            if question['id'] == question_id:
                return question
        return None
    
    def _get_fallback_questions(self) -> List[Dict[str, Any]]:
        """Domande di fallback se il file Excel non è disponibile"""
        fallback_questions = [
            # Canale 1: Academia-Industry joint research & mobility
            {
                'id': 'q_0',
                'question': 'National/regional policy frameworks effectively support sustained industry–academia co-creation.',
                'type': 'likert',
                'channel': 'n.1 Academia-Industry joint research & mobility',
                'factor': 'env',
                'actor': 'ACADEMIA incl. research and technology organisations',
                'scale': [1, 2, 3, 4, 5, 6, 7],
                'scale_labels': {
                    1: "Strongly disagree", 2: "Disagree", 3: "Somewhat disagree",
                    4: "Neutral", 5: "Somewhat agree", 6: "Agree", 7: "Strongly agree"
                }
            },
            {
                'id': 'q_1',
                'question': 'Are there formal joint research agreements with industry?',
                'type': 'yesno',
                'channel': 'n.1 Academia-Industry joint research & mobility',
                'factor': 'env',
                'actor': 'ACADEMIA incl. research and technology organisations',
                'options': ['Yes', 'No']
            },
            {
                'id': 'q_2',
                'question': 'IP/data governance policies are adapted to enable equitable sharing in joint R&I.',
                'type': 'likert',
                'channel': 'n.1 Academia-Industry joint research & mobility',
                'factor': 'org',
                'actor': 'INDUSTRY incl. SMEs and start-ups',
                'scale': [1, 2, 3, 4, 5, 6, 7],
                'scale_labels': {
                    1: "Strongly disagree", 2: "Disagree", 3: "Somewhat disagree",
                    4: "Neutral", 5: "Somewhat agree", 6: "Agree", 7: "Strongly agree"
                }
            },
            {
                'id': 'q_3',
                'question': 'Are research infrastructures co-governed or co-used with industry (e.g. joint labs, testbeds)?',
                'type': 'yesno',
                'channel': 'n.1 Academia-Industry joint research & mobility',
                'factor': 'org',
                'actor': 'ACADEMIA incl. research and technology organisations',
                'options': ['Yes', 'No']
            },
            {
                'id': 'q_4',
                'question': 'Researchers receive training or mentoring for working with industrial partners.',
                'type': 'likert',
                'channel': 'n.1 Academia-Industry joint research & mobility',
                'factor': 'ind',
                'actor': 'ACADEMIA incl. research and technology organisations',
                'scale': [1, 2, 3, 4, 5, 6, 7],
                'scale_labels': {
                    1: "Strongly disagree", 2: "Disagree", 3: "Somewhat disagree",
                    4: "Neutral", 5: "Somewhat agree", 6: "Agree", 7: "Strongly agree"
                }
            },
            {
                'id': 'q_5',
                'question': 'Are researchers formally authorised to lead or co-lead joint projects with industry?',
                'type': 'yesno',
                'channel': 'n.1 Academia-Industry joint research & mobility',
                'factor': 'ind',
                'actor': 'ACADEMIA incl. research and technology organisations',
                'options': ['Yes', 'No']
            }
        ]
        
        # Organizza le domande di fallback
        self._organize_questions(fallback_questions)
        
        print(f"⚠️ Usando {len(fallback_questions)} domande di fallback")
        return fallback_questions

