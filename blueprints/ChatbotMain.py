from flask import Blueprint, request, jsonify
from flask import Blueprint, render_template, request, redirect, url_for, flash, session

chatbotmain_bp = Blueprint('main', __name__)

from langchain_ollama.llms import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from .ChatBotVector import vector_store

model = OllamaLLM(model="llama3.2")

# Stricter prompt to ensure answers are only from CSV data
template = """
You are a plant expert assistant. ONLY use the information given below to answer questions.

Instructions:
- Do NOT use any outside knowledge, facts, or assumptions.
- If the answer is not found in the information, say:
"Sorry, no relevant information found in the database."

Information:
{Usage}

Question:
{question}
"""


prompt = ChatPromptTemplate.from_template(template)

chain = prompt | model


@chatbotmain_bp.route('/chatbot', endpoint='chatbot_page')
def chatbot_page():
    return render_template('ChatBot.html')


@chatbotmain_bp.route('/ask', methods=['POST'])
def ask():
    data = request.get_json()
    question = data.get("question", "").strip()

    if not question:
        return jsonify({"error": "No question provided."}), 400

    # Retrieve documents with scores from vector store
    docs_with_scores = vector_store.similarity_search_with_score(question, k=5)
    threshold = 0.7  # Lower = more similar (Chroma returns lower scores for more similar matches)

    # Filter documents by similarity threshold
    filtered_docs = [doc for doc, score in docs_with_scores if score < threshold]

    if not filtered_docs:
        return jsonify({"answer": "Sorry, no relevant information found in the database."})

    usage_text = "\n".join(doc.page_content for doc in filtered_docs)

    result = chain.invoke({"Usage": usage_text, "question": question})

    return jsonify({"answer": result})

