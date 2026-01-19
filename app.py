import streamlit as st
from rag.generate import ask_rag
import os

st.set_page_config(page_title="Finance Help")
st.title("📄 Ask Finance")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "last_question" not in st.session_state:
    st.session_state.last_question = ""

if st.session_state.chat_history:
    st.subheader("Chat History")
    for item in st.session_state.chat_history:
        st.markdown(f"**Q:** {item['question']}")
        st.markdown(f"**A:** {item['answer']}")
        st.markdown("---")

input_placeholder = st.empty()
question = input_placeholder.text_input("Ask a question about Finance")


if question and question != st.session_state.last_question:
    memory_context = ""
    for item in st.session_state.chat_history[-2:]:
        memory_context += f"Previous Q: {item['question']}\nPrevious A: {item['answer']}\n\n"

    # Get answer from RAG
    answer, sources = ask_rag(question, memory_context=memory_context)

    # Display current Q&A
    st.subheader("Question")
    st.write(question)

    st.subheader("Answer")
    st.write(answer)

    # Display sources
    if sources:
        st.subheader("Sources")
        seen_pdfs = set()
        for s in sources:
            pdf_name = s.split(" (page")[0]
            if pdf_name in seen_pdfs:
                continue
            seen_pdfs.add(pdf_name)

            pdf_path = f"data/{pdf_name}"
            if os.path.exists(pdf_path):
                with open(pdf_path, "rb") as f:
                    st.download_button(
                        label=f"📄 Download {pdf_name}",
                        data=f,
                        file_name=pdf_name,
                        mime="application/pdf",
                        key=f"download_{pdf_name}"
                    )

    # Save to chat history
    st.session_state.chat_history.append({"question": question, "answer": answer})
    st.session_state.last_question = question
