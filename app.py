import os
import json

import streamlit as st
from news_api import fetch_news
from model_selector import predict_with_model
from chatgpt_explainer import explain_article_with_gpt
from serpai import get_search_results  # or serpai, whichever matches your file
from fpdf import FPDF
import matplotlib.pyplot as plt

# --------------------- PDF Helpers ---------------------
def split_pdf_lines(pdf: FPDF, text: str, cell_w: float = None) -> list[str]:
    max_width = cell_w or (pdf.w - pdf.l_margin - pdf.r_margin)
    lines = []
    for paragraph in text.split("\n"):
        words = paragraph.split(" ")
        line = ""
        for word in words:
            test = word if not line else f"{line} {word}"
            if pdf.get_string_width(test) <= max_width:
                line = test
            else:
                if line:
                    lines.append(line)
                sub = ""
                for ch in word:
                    if pdf.get_string_width(sub + ch) <= max_width:
                        sub += ch
                    else:
                        lines.append(sub)
                        sub = ch
                line = sub
        lines.append(line)
    return lines

def create_pdf(news_text, prediction, confidence, explanation, links):
    pdf = FPDF()
    pdf.add_page()

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    reg_path = os.path.join(BASE_DIR, 'DejaVuSans.ttf')
    bold_path = os.path.join(BASE_DIR, 'DejaVuSans-Bold.ttf')
    for p in (reg_path, bold_path):
        if not os.path.isfile(p):
            raise FileNotFoundError(f"Font not found: {p}")

    pdf.add_font('DejaVu', '', reg_path, uni=True)
    pdf.add_font('DejaVu', 'B', bold_path, uni=True)

    pdf.set_left_margin(15)
    pdf.set_right_margin(15)
    cell_w = pdf.w - pdf.l_margin - pdf.r_margin

    pdf.set_font('DejaVu', 'B', 14)
    pdf.cell(0, 8, "News Article:", ln=True)
    pdf.set_font('DejaVu', '', 12)
    for ln in split_pdf_lines(pdf, news_text, cell_w):
        pdf.multi_cell(cell_w, 8, ln)
    pdf.ln(4)

    pdf.set_font('DejaVu', 'B', 12)
    pdf.cell(0, 8, f"Prediction: {prediction} ({confidence}%)", ln=True)
    pdf.ln(4)

    pdf.set_font('DejaVu', 'B', 12)
    pdf.cell(0, 8, "Explanation:", ln=True)
    pdf.set_font('DejaVu', '', 12)
    for ln in split_pdf_lines(pdf, explanation, cell_w):
        pdf.multi_cell(cell_w, 8, ln)
    pdf.ln(4)

    if links:
        pdf.set_font('DejaVu', 'B', 12)
        pdf.cell(0, 8, "Web Proof:", ln=True)
        pdf.set_font('DejaVu', '', 12)
        for item in links:
            safe_link = item['link'].replace("/", "/ ")
            line = f"- {item.get('title','[no title]')}: {safe_link}"
            for ln in split_pdf_lines(pdf, line, cell_w):
                pdf.multi_cell(cell_w, 8, ln)

    output_path = os.path.join(BASE_DIR, 'news_result.pdf')
    pdf.output(output_path)
    return output_path

# --------------------- Streamlit UI ---------------------
st.set_page_config(page_title="Fake News Detector", layout="wide")
col1, col2 = st.columns([1, 10])
with col1:
    st.image("logo.png", width=60)
with col2:
    st.markdown("<h1 style='margin-top: 10px;'>Fake News Detector</h1>", unsafe_allow_html=True)

st.markdown("<p style='text-align: center;'>Enter or select a news article and verify its authenticity in real-time.</p>", unsafe_allow_html=True)
st.markdown("---")

with st.sidebar:
    st.title("🧠 About")
    st.markdown("Detect fake news using multiple transformer models and Arpit AI explanation.")
    st.markdown("Built by Arpit Gola 💻")

mode = st.radio("🛠️ Choose Input Mode", ["🔄 Live News", "✍️ Manual Input"], horizontal=True)
model_choice = st.selectbox("🤖 Choose a Model for Prediction:", ["BERT", "RoBERTa", "DistilBERT", "XLNet", "All (Compare)"])

if "articles" not in st.session_state:
    st.session_state.articles = []

text = ""
if mode == "🔄 Live News":
    if st.button("🔄 Fetch Latest News"):
        with st.spinner("Fetching latest headlines..."):
            st.session_state.articles = fetch_news(country="us", category="technology", max_articles=5)
    if not st.session_state.articles:
        st.warning("Click the button to fetch news.")
    else:
        text = st.selectbox("📰 Select a news headline:", st.session_state.articles)
        if text:
            st.markdown("##### 📟 Full Article Preview:")
            st.text_area("Full News", text, height=150, disabled=True)
else:
    text = st.text_area("✍️ Paste or write your news article here", height=250)

if text:
    st.session_state.text = text
    st.markdown("---")
    st.markdown("### 🔍 Prediction Result")

    if model_choice != "All (Compare)":
        label, confidence = predict_with_model(text, model_choice)
        st.session_state.label = label
        st.session_state.confidence = confidence
        color = "green" if label == "Real" else "red"
        st.markdown(f"<b>{model_choice}</b> → <span style='color:{color}'>{label} ({confidence}%)</span>", unsafe_allow_html=True)
        st.metric("Confidence", f"{confidence}%")

        # Bar chart for selected model
        real_conf = confidence if label == "Real" else 100 - confidence
        fake_conf = 100 - real_conf

        fig, ax = plt.subplots(figsize=(3.5, 2.5))
        ax.bar(["Real"], [real_conf], color='green', label="Real")
        ax.bar(["Fake"], [fake_conf], color='red', label="Fake")
        ax.set_ylim(0, 100)
        ax.set_ylabel("Confidence %")
        ax.set_title(f"{model_choice} Confidence Distribution")
        ax.legend()
        st.pyplot(fig)

        with st.expander("💬 Arpit AI Explanation"):
            with st.spinner("🧠 Thinking like Arpit AI..."):
                try:
                    explanation = explain_article_with_gpt(text, label)
                except Exception as e:
                    explanation = f"⚠️ Explanation failed: {e}"
                st.write(explanation)
                st.session_state.explanation = explanation

    else:
        st.subheader("📊 Model Comparison")
        model_names = ["BERT", "RoBERTa", "DistilBERT", "XLNet"]
        real_conf_list = []
        fake_conf_list = []

        for model in model_names:
            lbl, conf = predict_with_model(text, model)
            color = "green" if lbl == "Real" else "red"
            st.markdown(f"**{model}** → <span style='color:{color}'>{lbl} ({conf}%)</span>", unsafe_allow_html=True)
            st.metric(f"{model} Confidence", f"{conf}%")
            if lbl == "Real":
                real_conf_list.append(conf)
                fake_conf_list.append(100 - conf)
            else:
                fake_conf_list.append(conf)
                real_conf_list.append(100 - conf)

        fig, ax = plt.subplots(figsize=(7, 4))
        bar_width = 0.35
        index = range(len(model_names))
        ax.bar(index, real_conf_list, bar_width, label="Real", color="green")
        ax.bar([i + bar_width for i in index], fake_conf_list, bar_width, label="Fake", color="red")
        ax.set_xlabel("Model")
        ax.set_ylabel("Confidence %")
        ax.set_title("All Models: Real vs Fake")
        ax.set_xticks([i + bar_width / 2 for i in index])
        ax.set_xticklabels(model_names)
        ax.legend()
        st.pyplot(fig)

        with st.expander("💬 Arpit AI Explanation"):
            with st.spinner("🧠 Thinking like Arpit AI..."):
                try:
                    explanation = explain_article_with_gpt(text, "Mixed")
                except Exception as e:
                    explanation = f"⚠️ Explanation failed: {e}"
                st.write(explanation)
                st.session_state.explanation = explanation

    with st.expander("🔎 Web Proof (Google Search Results)"):
        with st.spinner("Searching the web for this news..."):
            search_results = get_search_results(text.split('.')[0])
            st.session_state.search_results = search_results
            if not search_results:
                st.warning("No matching news found on Google.")
            else:
                for item in search_results:
                    st.markdown(f"🔗 [{item['title']}]({item['link']})")

    if st.button("📤 Export Result") and all(k in st.session_state for k in ("text", "label", "confidence", "explanation", "search_results")):
        pdf_path = create_pdf(
            st.session_state.text,
            st.session_state.label,
            st.session_state.confidence,
            st.session_state.explanation,
            st.session_state.search_results
        )
        json_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "news_result.json")
        with open(json_path, "w") as f:
            json.dump({
                "news": st.session_state.text,
                "prediction": st.session_state.label,
                "confidence": st.session_state.confidence,
                "explanation": st.session_state.explanation,
                "proof_links": st.session_state.search_results
            }, f, indent=4)

        col1, col2 = st.columns(2)
        with col1:
            with open(pdf_path, "rb") as f:
                st.download_button("⬇️ Download PDF", f, file_name="result.pdf")
        with col2:
            with open(json_path, "rb") as f:
                st.download_button("⬇️ Download JSON", f, file_name="result.json")
