from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline
from rag.retrieve import load_vectorstore
from rag.prompt import RAG_PROMPT
from sentence_transformers import CrossEncoder

#HF model for generation
MODEL_NAME = "declare-lab/flan-alpaca-base"
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME)

generator = pipeline(
    "text2text-generation",
    model=model,
    tokenizer=tokenizer,
    device=-1  # CPU
)

#Reranker for better relevance
reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")


def ask_rag(question, memory_context=""):
    vectorstore = load_vectorstore()

    query = question.lower()

    docs_with_scores = vectorstore.similarity_search_with_score(query, k=5)
    
    SIMILARITY_THRESHOLD = 0.8

    #Keep only relevant chunks below threshold
    relevant_docs = [doc for doc, score in docs_with_scores if score < SIMILARITY_THRESHOLD]
    
    #Safe refusal if no relevant docs
    if not relevant_docs:
        return "I don't know based on the provided documents.", []

    # Rerank retrieved docs for best order
    texts = [d.page_content for d in relevant_docs]
    scores = reranker.predict([[question, text] for text in texts])
    relevant_docs = [doc for _, doc in sorted(zip(scores, relevant_docs), reverse=True)]

    context = "\n\n".join(
        [
            f"{d.page_content}\n(Source: {d.metadata.get('source', 'Unknown')} - page {d.metadata.get('page', '?')})"
            for d in relevant_docs
        ]
    )
    if memory_context:
        context = memory_context + "\n\n" + context

    prompt = RAG_PROMPT.format(context=context, question=question)

    #Generate answer
    response_text = generator(
        prompt,
        max_length=300,
        do_sample=True,
        temperature=0.7
    )[0]["generated_text"]


    if "I don't know" in response_text:
        return response_text.strip(), []

    seen = set()
    sources = []
    for d in relevant_docs:
        src = f"{d.metadata.get('source', 'Unknown')} (page {d.metadata.get('page', '?')})"
        if src not in seen:
            sources.append(src)
            seen.add(src)

    final_answer = f"{response_text.strip()}\n\nCitations:\n" + "\n".join(sources)

    return final_answer, sources
