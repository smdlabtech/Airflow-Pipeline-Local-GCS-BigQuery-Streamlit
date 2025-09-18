# modules/status_manager.py
import streamlit as st
from enum import Enum

class Status(Enum):
    NOT_STARTED = "⚪ NOT_STARTED"
    PENDING = "⏳ PENDING" 
    SUCCESS = "✅ SUCCESS"
    FAILED = "❌ FAILED"

def init_statuses():
    """Initialiser tous les statuts"""
    if 'status' not in st.session_state:
        st.session_state.status = {
            'gcp_setup': Status.NOT_STARTED,
            'gcs_upload': Status.NOT_STARTED,
            'bq_load': Status.NOT_STARTED,
            'sql_transform': Status.NOT_STARTED,
            'dw_modeling': Status.NOT_STARTED,
            'visualization': Status.NOT_STARTED,
            'exports': Status.NOT_STARTED
        }

def update_status(step, status):
    """Mettre à jour le statut d'une étape"""
    st.session_state.status[step] = status

def get_status(step):
    """Récupérer le statut d'une étape"""
    return st.session_state.status.get(step, Status.NOT_STARTED)

def display_status(step, label):
    """Afficher le statut visuellement"""
    status = get_status(step)
    st.markdown(f"**{label}** {status.value}")

def display_all_statuses():
    """Afficher tous les statuts dans une sidebar"""
    with st.sidebar:
        st.header("📊 État du Pipeline")
        
        for step, label in [
            ('gcp_setup', '🔧 Configuration GCP'),
            ('gcs_upload', '📤 Upload vers GCS'),
            ('bq_load', '⬆️ Chargement BigQuery'),
            ('sql_transform', '🧮 Transformations SQL'),
            ('dw_modeling', '🏗️ Modélisation DW'),
            ('visualization', '📊 Visualisation'),
            ('exports', '📤 Exports')
        ]:
            status = get_status(step)
            color = "green" if status == Status.SUCCESS else "red" if status == Status.FAILED else "orange" if status == Status.PENDING else "gray"
            st.markdown(f"<span style='color:{color}'>{label} {status.value}</span>", unsafe_allow_html=True)
        
        st.markdown("---")