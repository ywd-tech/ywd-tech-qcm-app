
import streamlit as st
import fitz  # PyMuPDF
import openai
import os

# Clé API (à configurer comme variable d'environnement)
openai.api_key = os.getenv("OPENAI_API_KEY")

st.set_page_config(page_title="Générateur de QCM intelligent", layout="wide")
st.title("📘 Générateur intelligent de QCM à partir d’un PDF médical")

uploaded_file = st.file_uploader("📥 Importer un fichier PDF", type="pdf")

max_questions = st.slider("🔢 Nombre maximum de QCM à générer", 1, 100, 5)

if uploaded_file:
    st.info("📄 Lecture du contenu du PDF en cours...")
    with fitz.open(stream=uploaded_file.read(), filetype="pdf") as doc:
        texte = "\n".join([page.get_text() for page in doc])

    st.success("✅ Texte extrait avec succès !")
    st.text_area("📝 Aperçu du texte extrait", texte[:2000], height=200)

    if st.button("🧠 Générer les QCM automatiquement"):
        with st.spinner("Génération en cours via OpenAI GPT..."):
            prompt = f"""
Tu es un expert en pédagogie médicale. Génére {max_questions} QCM (questions à choix multiples) à partir du texte suivant :

---
{texte}
---

Pour chaque QCM, donne le résultat au format JSON structuré suivant :
[ {{
  "question": "...",
  "options": ["...", "...", "...", "..."],
  "correct_answers": [0, 2]  # indices des bonnes réponses
}} ]

Génère uniquement la structure JSON.
"""

            try:
                response = openai.ChatCompletion.create(
                    model="gpt-4",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.7,
                    max_tokens=3000
                )
                import json
                import re
                raw_text = response.choices[0].message.content.strip()
                json_text = re.search(r'\[.*\]', raw_text, re.DOTALL)
                qcm_list = json.loads(json_text.group()) if json_text else []

                st.success(f"🎯 {len(qcm_list)} QCM générés !")
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
                st.error(f"Une erreur est survenue : {e}")
else:
    st.warning("📂 Veuillez importer un PDF pour commencer.")
