import os
import re
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

DATA_DIR = "data"

def clean_text(text):
    lines = [line.strip() for line in text.split("\n") if line.strip()]
    cleaned_lines = []

    for line in lines:
        if re.match(r'^(page\s*\d+(\s*of\s*\d+)?)$', line, re.I):
            continue
        if re.match(r'^\d+\s*/\s*\d+$', line):
            continue
        if len(line) < 5:
            continue

        cleaned_lines.append(line)

    return "\n".join(cleaned_lines)

def load_and_chunk_documents():
    documents = []

    # Load PDFs
    for filename in os.listdir(DATA_DIR):
        if filename.lower().endswith(".pdf"):
            path = os.path.join(DATA_DIR, filename)
            loader = PyPDFLoader(path)
            pages = loader.load()

            for p in pages:
                p.page_content = clean_text(p.page_content)
                p.metadata["source"] = filename

            documents.extend(pages)

    #chunks
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=100
    )
    chunks = splitter.split_documents(documents)
    return chunks

if __name__ == "__main__":
    chunks = load_and_chunk_documents()
    print(f"Total chunks: {len(chunks)}")
