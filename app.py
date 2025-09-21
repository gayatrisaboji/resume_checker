# app.py
import streamlit as st
import pdfplumber, docx2txt
import streamlit as st

try:
    from evaluator import compute_relevance, clean_text
except Exception as e:
    st.error(f"⚠️ Import error: {e}")
    st.stop()  # stop execution so blank screen is avoided

import os

st.set_page_config(layout="wide", page_title="Resume Relevance Checker")
st.title("Automated Resume Relevance Checker — MVP")

st.sidebar.header("1) Upload Job Description (JD)")
jd_file = st.sidebar.file_uploader("Upload JD (PDF or DOCX)", type=["pdf","docx"])
jd_text = ""
if jd_file:
    if jd_file.type == "application/pdf":
        with pdfplumber.open(jd_file) as pdf:
            for p in pdf.pages:
                txt = p.extract_text()
                if txt: jd_text += txt + "\n"
    else:
        jd_text = docx2txt.process(jd_file)
else:
    st.sidebar.info("Please upload a JD file to parse required skills.")

st.sidebar.header("2) Provide required skills (optional)")
skills_input = st.sidebar.text_area("Comma-separated skills (e.g. Python, Flask, SQL)", height=80)
if skills_input.strip():
    jd_skills = [s.strip() for s in skills_input.split(",") if s.strip()]
else:
    # try to auto-extract simple keywords from JD (take top nouns/words)
    # for simplicity when JD uploaded, split and take frequent words (quick heuristic)
    jd_skills = []
    if jd_text:
        # quick heuristic: words of length>2 and titlecase-like (not thorough)
        words = [w.strip().lower() for w in jd_text.split() if len(w.strip())>2]
        freq = {}
        for w in words:
            freq[w] = freq.get(w,0)+1
        # take top candidates excluding common stop words
        stops = set(["and","with","the","skills","experience","years","ability","work","required","must","prefer"])
        cand = [w for w in sorted(freq, key=freq.get, reverse=True) if w not in stops][:15]
        jd_skills = [w for w in cand]

st.sidebar.write("Detected / used skills:", ", ".join(jd_skills[:20]) if jd_skills else "None")

st.header("Upload Resumes to evaluate")
uploaded = st.file_uploader("Upload one or multiple resumes (PDF/DOCX)", accept_multiple_files=True, type=["pdf","docx"])
results = []

if st.button("Run Evaluation"):

    if not jd_text and not jd_skills:
        st.error("Please either upload a JD or enter required skills in the sidebar.")
    elif not uploaded:
        st.error("Please upload at least one resume.")
    else:
        for file in uploaded:
            # extract text
            res_text = ""
            try:
                if file.type == "application/pdf":
                    with pdfplumber.open(file) as pdf:
                        for p in pdf.pages:
                            t = p.extract_text()
                            if t: res_text += t + "\n"
                else:
                    res_text = docx2txt.process(file)
            except Exception as e:
                res_text = ""
            res_text = res_text or ""
            # compute relevance
            out = compute_relevance(jd_text, res_text, jd_skills)
            results.append({
                "filename": file.name,
                "score": out["final_score"],
                "verdict": out["verdict"],
                "missing": ", ".join(out["missing"]) if out["missing"] else "None",
                "feedback": out["feedback"]
            })

        # show results table
        if results:
            st.subheader("Results")
            import pandas as pd
            df = pd.DataFrame(results).sort_values(by="score", ascending=False)
            st.dataframe(df, use_container_width=True)
            # allow downloading CSV
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button("Download results CSV", data=csv, file_name="results.csv", mime="text/csv")
