import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import io
import base64
from typing import Dict, List, Any, Optional

class VisualizationEngine:
    """
    Crea visualizzazioni e grafici per i risultati dell'assessment
    """
    
    def __init__(self):
        self.color_palette = {
            'primary': '#1f77b4',
            'secondary': '#ff7f0e', 
            'success': '#2ca02c',
            'warning': '#d62728',
            'info': '#9467bd',
            'light': '#17becf'
        }
        
        self.channels = {
            1: "Joint Research",
            2: "Infrastructure", 
            3: "Tech Transfer",
            4: "Entrepreneurship",
            5: "Mobility",
            6: "Ecosystem"
        }
    
    def create_radar_chart(self, channel_scores: Dict[str, float], 
                          title: str = "Punteggi per Canale") -> go.Figure:
        """
        Crea un radar chart per i punteggi dei canali
        
        Args:
            channel_scores: Dizionario con punteggi per canale
            title: Titolo del grafico
            
        Returns:
            Figura Plotly del radar chart
        """
        # Prepara i dati
        if isinstance(list(channel_scores.keys())[0], int):
            # Se le chiavi sono numeri, usa i nomi abbreviati
            categories = [self.channels.get(k, f"Channel {k}") for k in sorted(channel_scores.keys())]
            values = [channel_scores[k] for k in sorted(channel_scores.keys())]
        else:
            # Se le chiavi sono già nomi
            categories = list(channel_scores.keys())
            values = list(channel_scores.values())
        
        # Crea il radar chart
        fig = go.Figure()
        
        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=categories,
            fill='toself',
            name='Punteggi',
            line_color=self.color_palette['primary'],
            fillcolor=f"rgba(31, 119, 180, 0.3)"
        ))
        
        # Aggiungi linea di riferimento per il benchmark Bologna (5.76)
        bologna_values = [5.76] * len(categories)
        fig.add_trace(go.Scatterpolar(
            r=bologna_values,
            theta=categories,
            mode='lines',
            name='Benchmark Bologna',
            line=dict(color=self.color_palette['warning'], dash='dash', width=2)
        ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 7],
                    tickmode='linear',
                    tick0=0,
                    dtick=1,
                    gridcolor='lightgray'
                ),
                angularaxis=dict(
                    gridcolor='lightgray'
                )
            ),
            showlegend=True,
            title={
                'text': title,
                'x': 0.5,
                'xanchor': 'center'
            },
            font=dict(size=12),
            width=600,
            height=500
        )
        
        return fig
    
    def create_factor_comparison(self, factor_scores: Dict[str, float],
                               title: str = "Confronto Fattori") -> go.Figure:
        """
        Crea un bar chart per confrontare i fattori
        
        Args:
            factor_scores: Dizionario con punteggi per fattore
            title: Titolo del grafico
            
        Returns:
            Figura Plotly del bar chart
        """
        factor_names = {
            'env': 'Environmental',
            'org': 'Organizational',
            'ind': 'Individual'
        }
        
        categories = [factor_names.get(k, k) for k in factor_scores.keys()]
        values = list(factor_scores.values())
        colors = [self.color_palette['primary'], self.color_palette['secondary'], self.color_palette['success']]
        
        fig = go.Figure(data=[
            go.Bar(
                x=categories,
                y=values,
                marker_color=colors[:len(categories)],
                text=[f"{v:.2f}" for v in values],
                textposition='auto',
            )
        ])
        
        # Aggiungi linea di riferimento
        fig.add_hline(y=5.76, line_dash="dash", line_color=self.color_palette['warning'],
                     annotation_text="Benchmark Bologna")
        
        fig.update_layout(
            title={
                'text': title,
                'x': 0.5,
                'xanchor': 'center'
            },
            xaxis_title="Fattori",
            yaxis_title="Punteggio",
            yaxis=dict(range=[0, 7]),
            showlegend=False,
            width=500,
            height=400
        )
        
        return fig
    
    def create_channel_factor_heatmap(self, scores_data: Dict[str, Any],
                                    title: str = "Matrice Canali x Fattori") -> go.Figure:
        """
        Crea una heatmap della matrice canali x fattori
        
        Args:
            scores_data: Dati dei punteggi completi
            title: Titolo del grafico
            
        Returns:
            Figura Plotly della heatmap
        """
        # Prepara la matrice
        channels = sorted(scores_data['channels'].keys())
        factors = ['env', 'org', 'ind']
        factor_names = ['Environmental', 'Organizational', 'Individual']
        
        matrix = []
        for factor in factors:
            row = []
            for channel in channels:
                score = scores_data['channels'][channel]['factors'].get(factor, 0)
                row.append(score)
            matrix.append(row)
        
        channel_names = [self.channels.get(c, f"Channel {c}") for c in channels]
        
        fig = go.Figure(data=go.Heatmap(
            z=matrix,
            x=channel_names,
            y=factor_names,
            colorscale='RdYlBu_r',
            zmin=0,
            zmax=7,
            text=[[f"{val:.2f}" for val in row] for row in matrix],
            texttemplate="%{text}",
            textfont={"size": 12},
            colorbar=dict(title="Punteggio")
        ))
        
        fig.update_layout(
            title={
                'text': title,
                'x': 0.5,
                'xanchor': 'center'
            },
            xaxis_title="Canali",
            yaxis_title="Fattori",
            width=700,
            height=400
        )
        
        return fig
    
    def create_progress_chart(self, completion_rate: float, 
                            title: str = "Progresso Assessment") -> go.Figure:
        """
        Crea un grafico di progresso circolare
        
        Args:
            completion_rate: Tasso di completamento (0-1)
            title: Titolo del grafico
            
        Returns:
            Figura Plotly del progress chart
        """
        fig = go.Figure(go.Indicator(
            mode = "gauge+number+delta",
            value = completion_rate * 100,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': title},
            delta = {'reference': 100},
            gauge = {
                'axis': {'range': [None, 100]},
                'bar': {'color': self.color_palette['primary']},
                'steps': [
                    {'range': [0, 50], 'color': "lightgray"},
                    {'range': [50, 80], 'color': "gray"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 90
                }
            }
        ))
        
        fig.update_layout(
            width=400,
            height=300,
            font={'color': "darkblue", 'family': "Arial"}
        )
        
        return fig
    
    def create_benchmark_comparison(self, user_score: float, benchmark_score: float = 5.76,
                                  title: str = "Confronto con Benchmark") -> go.Figure:
        """
        Crea un grafico di confronto con il benchmark
        
        Args:
            user_score: Punteggio dell'utente
            benchmark_score: Punteggio di benchmark (default Bologna)
            title: Titolo del grafico
            
        Returns:
            Figura Plotly del confronto
        """
        categories = ['Il tuo punteggio', 'Benchmark Bologna']
        values = [user_score, benchmark_score]
        colors = [self.color_palette['primary'], self.color_palette['warning']]
        
        fig = go.Figure(data=[
            go.Bar(
                x=categories,
                y=values,
                marker_color=colors,
                text=[f"{v:.2f}" for v in values],
                textposition='auto',
            )
        ])
        
        fig.update_layout(
            title={
                'text': title,
                'x': 0.5,
                'xanchor': 'center'
            },
            yaxis=dict(range=[0, 7]),
            showlegend=False,
            width=400,
            height=400
        )
        
        return fig
    
    def create_wordcloud(self, text_responses: List[str], 
                        title: str = "Temi Principali") -> str:
        """
        Crea una word cloud dalle risposte testuali
        
        Args:
            text_responses: Lista di risposte testuali
            title: Titolo della word cloud
            
        Returns:
            String base64 dell'immagine della word cloud
        """
        if not text_responses:
            return None
        
        # Combina tutti i testi
        combined_text = ' '.join(text_responses)
        
        # Crea la word cloud
        wordcloud = WordCloud(
            width=800, 
            height=400, 
            background_color='white',
            colormap='viridis',
            max_words=50,
            relative_scaling=0.5,
            random_state=42
        ).generate(combined_text)
        
        # Converti in immagine base64
        img_buffer = io.BytesIO()
        plt.figure(figsize=(10, 5))
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis('off')
        plt.title(title, fontsize=16, pad=20)
        plt.tight_layout()
        plt.savefig(img_buffer, format='png', bbox_inches='tight', dpi=150)
        plt.close()
        
        img_buffer.seek(0)
        img_str = base64.b64encode(img_buffer.read()).decode()
        
        return img_str
    
    def create_maturity_gauge(self, total_score: float,
                            title: str = "Livello di Maturità") -> go.Figure:
        """
        Crea un gauge per il livello di maturità
        
        Args:
            total_score: Punteggio totale (0-7)
            title: Titolo del gauge
            
        Returns:
            Figura Plotly del gauge
        """
        # Determina il livello di maturità
        if total_score >= 6.0:
            level = "Avanzato"
            color = self.color_palette['success']
        elif total_score >= 5.0:
            level = "Intermedio"
            color = self.color_palette['primary']
        elif total_score >= 4.0:
            level = "Base"
            color = self.color_palette['secondary']
        else:
            level = "Iniziale"
            color = self.color_palette['warning']
        
        fig = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = total_score,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': f"{title}<br><span style='font-size:0.8em;color:gray'>Livello: {level}</span>"},
            gauge = {
                'axis': {'range': [None, 7]},
                'bar': {'color': color},
                'steps': [
                    {'range': [0, 4], 'color': "lightgray"},
                    {'range': [4, 5], 'color': "yellow"},
                    {'range': [5, 6], 'color': "lightgreen"},
                    {'range': [6, 7], 'color': "green"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 5.76  # Benchmark Bologna
                }
            }
        ))
        
        fig.update_layout(
            width=400,
            height=300,
            font={'color': "darkblue", 'family': "Arial"}
        )
        
        return fig
    
    def create_summary_dashboard(self, scores_data: Dict[str, Any]) -> go.Figure:
        """
        Crea una dashboard riassuntiva con multiple visualizzazioni
        
        Args:
            scores_data: Dati completi dei punteggi
            
        Returns:
            Figura Plotly con subplot multipli
        """
        # Crea subplot
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Punteggi per Canale', 'Confronto Fattori', 
                          'Livello Maturità', 'Benchmark Comparison'),
            specs=[[{"type": "bar"}, {"type": "bar"}],
                   [{"type": "indicator"}, {"type": "bar"}]]
        )
        
        # 1. Bar chart canali
        channels = sorted(scores_data['channels'].keys())
        channel_names = [self.channels.get(c, f"Ch{c}") for c in channels]
        channel_scores = [scores_data['channels'][c]['score'] for c in channels]
        
        fig.add_trace(
            go.Bar(x=channel_names, y=channel_scores, name="Canali",
                  marker_color=self.color_palette['primary']),
            row=1, col=1
        )
        
        # 2. Bar chart fattori
        factor_names = ['Environmental', 'Organizational', 'Individual']
        factor_scores = [scores_data['factors_summary'][f] for f in ['env', 'org', 'ind']]
        
        fig.add_trace(
            go.Bar(x=factor_names, y=factor_scores, name="Fattori",
                  marker_color=self.color_palette['secondary']),
            row=1, col=2
        )
        
        # 3. Gauge maturità
        total_score = scores_data['total_score']
        fig.add_trace(
            go.Indicator(
                mode="gauge+number",
                value=total_score,
                gauge={'axis': {'range': [0, 7]},
                      'bar': {'color': self.color_palette['success']},
                      'steps': [{'range': [0, 4], 'color': "lightgray"},
                               {'range': [4, 7], 'color': "lightgreen"}]},
                title={'text': "Maturità"}
            ),
            row=2, col=1
        )
        
        # 4. Confronto benchmark
        fig.add_trace(
            go.Bar(x=['Tuo Score', 'Bologna'], y=[total_score, 5.76],
                  marker_color=[self.color_palette['primary'], self.color_palette['warning']],
                  name="Benchmark"),
            row=2, col=2
        )
        
        fig.update_layout(
            height=600,
            showlegend=False,
            title_text="Dashboard Riassuntiva Assessment"
        )
        
        return fig

