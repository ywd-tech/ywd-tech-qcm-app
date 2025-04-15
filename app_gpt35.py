
import streamlit as st
import fitz  # PyMuPDF
import openai
import json
import re
from openai import OpenAI

st.set_page_config(page_title="QCM Médical IA", layout="wide")
st.title("🧠 Générateur intelligent de QCM à partir d’un PDF médical")

# Clé API à saisir via interface
openai_api_key = st.text_input("🔐 Entrez votre clé OpenAI API :", type="password")

uploaded_file = st.file_uploader("📥 Importer un fichier PDF", type="pdf")
max_questions = st.slider("🔢 Nombre maximum de QCM à générer", 1, 100, 5)

if uploaded_file and openai_api_key:
    st.info("📄 Lecture du contenu du PDF en cours...")
    with fitz.open(stream=uploaded_file.read(), filetype="pdf") as doc:
        texte = "\n".join([page.get_text() for page in doc])

    st.success("✅ Texte extrait avec succès !")
    st.text_area("📝 Aperçu du texte extrait", texte[:2000], height=200)

    if st.button("🧠 Générer les QCM automatiquement"):
        with st.spinner("Génération en cours via GPT-3.5..."):

            prompt = f"""
Tu es un expert en pédagogie médicale. Génère {max_questions} QCM (questions à choix multiples) à partir du texte suivant :

---
{texte}
---

Pour chaque QCM, donne le résultat au format JSON structuré suivant :
[ {{
  "question": "...",
  "options": ["...", "...", "...", "..."],
  "correct_answers": [0, 2]
}} ]

Génère uniquement la structure JSON.
"""

            try:
                client = OpenAI(api_key=openai_api_key)
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.7,
                    max_tokens=3000
                )
                raw_text = response.choices[0].message.content.strip()
                json_text = re.search(r'\[.*\]', raw_text, re.DOTALL)
                qcm_list = json.loads(json_text.group()) if json_text else []

                st.success(f"🎯 {len(qcm_list)} QCM générés automatiquement")

                for i, q in enumerate(qcm_list):
                    st.markdown(f"**{i+1}. {q['question']}**")
                    user_choices = []
                    for j, opt in enumerate(q['options']):
                        checked = st.checkbox(opt, key=f"q{i}_opt{j}")
                        if checked:
                            user_choices.append(j)
                    if set(user_choices) == set(q['correct_answers']):
                        st.success("✅ Bonne réponse")
                    else:
                        bonnes = ", ".join([q['options'][k] for k in q['correct_answers']])
                        st.error(f"❌ Mauvaise réponse. Bonne(s) réponse(s) : {bonnes}")

            except Exception as e:
                st.error(f"❌ Erreur lors de la génération : {e}")
elif uploaded_file and not openai_api_key:
    st.warning("🔐 Veuillez entrer votre clé API OpenAI pour générer les QCM.")
