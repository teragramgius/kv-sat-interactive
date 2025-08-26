import json
import os
import pandas as pd
from datetime import datetime
from typing import Dict, Any, Optional

class DataManager:
    """
    Gestisce il salvataggio e caricamento dei dati dell'assessment
    """
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self.ensure_data_directory()
    
    def ensure_data_directory(self):
        """Assicura che la directory dei dati esista"""
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
    
    def save_session_data(self, data: Dict[str, Any], session_id: str) -> bool:
        """
        Salva i dati della sessione corrente
        
        Args:
            data: Dizionario con i dati da salvare
            session_id: ID univoco della sessione
            
        Returns:
            bool: True se il salvataggio è riuscito
        """
        try:
            file_path = os.path.join(self.data_dir, f"session_{session_id}.json")
            
            # Aggiungi timestamp
            data['last_updated'] = datetime.now().isoformat()
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            return True
        except Exception as e:
            print(f"Errore nel salvataggio: {e}")
            return False
    
    def load_session_data(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Carica i dati di una sessione precedente
        
        Args:
            session_id: ID della sessione da caricare
            
        Returns:
            Dict con i dati della sessione o None se non trovata
        """
        try:
            file_path = os.path.join(self.data_dir, f"session_{session_id}.json")
            
            if not os.path.exists(file_path):
                return None
            
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Errore nel caricamento: {e}")
            return None
    
    def export_to_json(self, data: Dict[str, Any], filename: str = None) -> str:
        """
        Esporta i dati in formato JSON
        
        Args:
            data: Dati da esportare
            filename: Nome del file (opzionale)
            
        Returns:
            str: Contenuto JSON come stringa
        """
        if filename:
            file_path = os.path.join(self.data_dir, filename)
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        
        return json.dumps(data, indent=2, ensure_ascii=False)
    
    def export_to_csv(self, responses: Dict[str, Any], filename: str = None) -> pd.DataFrame:
        """
        Esporta le risposte in formato CSV
        
        Args:
            responses: Dizionario delle risposte
            filename: Nome del file CSV (opzionale)
            
        Returns:
            DataFrame con le risposte
        """
        # Converte le risposte in DataFrame
        data_rows = []
        
        for key, value in responses.items():
            if key.startswith('q_'):
                question_id = key.replace('q_', '')
                comment_key = f"comment_{question_id}"
                comment = responses.get(comment_key, '')
                
                data_rows.append({
                    'question_id': question_id,
                    'response': value,
                    'comment': comment,
                    'timestamp': datetime.now().isoformat()
                })
        
        df = pd.DataFrame(data_rows)
        
        if filename:
            file_path = os.path.join(self.data_dir, filename)
            df.to_csv(file_path, index=False, encoding='utf-8')
        
        return df
    
    def get_all_sessions(self) -> list:
        """
        Restituisce una lista di tutte le sessioni salvate
        
        Returns:
            Lista degli ID delle sessioni
        """
        sessions = []
        
        if not os.path.exists(self.data_dir):
            return sessions
        
        for filename in os.listdir(self.data_dir):
            if filename.startswith('session_') and filename.endswith('.json'):
                session_id = filename.replace('session_', '').replace('.json', '')
                sessions.append(session_id)
        
        return sessions
    
    def delete_session(self, session_id: str) -> bool:
        """
        Elimina una sessione salvata
        
        Args:
            session_id: ID della sessione da eliminare
            
        Returns:
            bool: True se l'eliminazione è riuscita
        """
        try:
            file_path = os.path.join(self.data_dir, f"session_{session_id}.json")
            
            if os.path.exists(file_path):
                os.remove(file_path)
                return True
            
            return False
        except Exception as e:
            print(f"Errore nell'eliminazione: {e}")
            return False
    
    def backup_data(self, backup_dir: str = "backups") -> bool:
        """
        Crea un backup di tutti i dati
        
        Args:
            backup_dir: Directory per il backup
            
        Returns:
            bool: True se il backup è riuscito
        """
        try:
            if not os.path.exists(backup_dir):
                os.makedirs(backup_dir)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = os.path.join(backup_dir, f"backup_{timestamp}.json")
            
            all_data = {}
            for session_id in self.get_all_sessions():
                session_data = self.load_session_data(session_id)
                if session_data:
                    all_data[session_id] = session_data
            
            with open(backup_file, 'w', encoding='utf-8') as f:
                json.dump(all_data, f, indent=2, ensure_ascii=False)
            
            return True
        except Exception as e:
            print(f"Errore nel backup: {e}")
            return False

