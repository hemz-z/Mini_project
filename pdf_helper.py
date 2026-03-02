# ─────────────────────────────────────────────
#  PDF Helper — Extract, Index, and Answer
# ─────────────────────────────────────────────

from PyPDF2 import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from ai_helper import call_groq
from config import CHUNK_SIZE, CHUNK_OVERLAP, EMBEDDING_MODEL


def extract_text_from_pdf(pdf_file):
    """Read all pages of a PDF and return combined text."""
    reader = PdfReader(pdf_file)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text


def build_vector_store(text):
    """Split text into chunks and store as vectors in FAISS."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP
    )
    chunks = splitter.split_text(text)
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
    return FAISS.from_texts(chunks, embedding=embeddings)


def answer_question(vector_store, question):
    """Find relevant chunks and generate an answer using Groq."""
    docs = vector_store.similarity_search(question, k=4)
    context = "\n\n".join([doc.page_content for doc in docs])
    prompt = f"""You are a helpful assistant. Answer the question based only on the context below.
If the answer is not in the context, say "I couldn't find that in the document."

Context:
{context}

Question: {question}

Answer:"""
    result = call_groq(prompt)
    if result:
        return result
    return "📄 **Relevant passages from your PDF:**\n\n" + context
