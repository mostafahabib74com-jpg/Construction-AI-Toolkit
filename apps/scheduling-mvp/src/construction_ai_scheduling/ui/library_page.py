"""Inspect the integrated repository's actual workflows and original prompts."""

import streamlit as st


def render_library_page(repo_root):
    st.header("Engineering workflows / مكتبة المهارات")
    st.caption("Browse the actual repository instructions. These workflows guide an AI assistant; this local viewer does not call a language model.")
    skills = sorted((repo_root / ".agents/skills").glob("*/SKILL.md"))
    prompts = sorted((repo_root / "AI-Prompts").glob("*/*.md"))
    first, second = st.columns(2)
    first.metric("Repository skills", len(skills))
    second.metric("Engineering prompt documents", len(prompts))
    kind = st.radio("Library", ["Skills", "Original prompts"], horizontal=True)
    query = st.text_input("Search workflow names").strip().lower()
    paths = [path for path in (skills if kind == "Skills" else prompts) if query in str(path.relative_to(repo_root)).lower()]
    if not paths:
        st.info("No matching workflows.")
        return
    selected = st.selectbox("Workflow", paths, format_func=lambda path: str(path.relative_to(repo_root)).replace("\\", "/"))
    text = selected.read_text(encoding="utf-8")
    st.markdown(text)
    st.download_button("Download workflow instructions", text, file_name=selected.parent.name + "-" + selected.name, mime="text/markdown")
    if kind == "Skills":
        for reference in sorted((selected.parent / "references").glob("*.md")):
            with st.expander(reference.stem):
                st.markdown(reference.read_text(encoding="utf-8"))
