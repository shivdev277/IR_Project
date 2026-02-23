import streamlit as st
from src.search import search_query
from src.answer_extractor import extract_answer

st.title("College PDF & PPT Semantic Search")

course = st.selectbox("Select Course", ["AI", "NETSEC"])
query = st.text_input("Ask your question")

if st.button("Search") and query:
    embedding_file = f"embeddings/{course}.pkl"
    
    result = search_query(query, embedding_file)
    answer = extract_answer(result["text"], query)

    st.subheader("Answer")
    st.write(answer)

    st.subheader("Source")
    st.write(f"File: {result['pdf']}")
    st.write(f"Page: {result['page']}")
