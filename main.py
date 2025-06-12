import streamlit as st
import subprocess
import psutil
import time
import os

GAME_FILE = "asteroides_jogo.py"

def find_game_process():
    """Procura por um processo que esteja rodando jogo.py"""
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if GAME_FILE in ' '.join(proc.info['cmdline']):
                return proc
        except Exception:
            continue
    return None

st.title("Painel de Controle do Jogo 🎮")

proc = find_game_process()

if proc:
    st.success("O jogo já está rodando! ✅")
    if st.button("Fechar o jogo ❌"):
        proc.terminate()
        st.warning("Jogo encerrado.")
else:
    st.warning("O jogo não está rodando.")
    if st.button("Abrir o jogo 🚀"):
        subprocess.Popen(["python", GAME_FILE])
        time.sleep(1)  # espera 1s pro processo aparecer
        st.success("Jogo iniciado!")

# Mostrar status do processo
proc = find_game_process()
if proc:
    st.markdown(f"**PID:** {proc.pid}")
