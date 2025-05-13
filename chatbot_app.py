import streamlit as st
import requests
from bs4 import BeautifulSoup
import PyPDF2
import google.generativeai as genai

# ✅ Configure Gemini API
genai.configure(api_key="AIzaSyBsRzXyhijV4k0cFuUyv2OYzoUCghy9eZ0")  # Replace with your actual key
model = genai.GenerativeModel("gemini-1.5-flash")

# ✅ Extract text from PDF
def extract_pdf_text(uploaded_file):
    try:
        reader = PyPDF2.PdfReader(uploaded_file)
        text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text
        return text
    except Exception as e:
        return f"Error reading PDF: {e}"

# ✅ Extract text from Website
def extract_website_text(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")
        paragraphs = soup.find_all("p")
        return "\n".join([p.get_text() for p in paragraphs])
    except Exception as e:
        return f"Error fetching website: {e}"

# ✅ Ask Gemini using PDF + website content
def ask_gemini(pdf_text, website_text, question):
    prompt = f"""
You are a helpful assistant. Answer ONLY using the content provided from the PDF and the website. Do not use any external knowledge.

PDF Content:
{pdf_text}

Website Content:
{website_text}

User's Question:
{question}
"""
    response = model.generate_content(prompt)
    return response.text

# ✅ Streamlit UI Setup
st.set_page_config(page_title="📘🌐 PDF + Website Chatbot", layout="centered")
st.title("📘🌐 Ask Questions Using Your PDF & Website Content")
st.markdown("This chatbot answers *only using the content* you provide (PDF + Website).")

# --- Upload area ---
uploaded_pdf = st.file_uploader("📄 Upload your PDF file", type=["pdf"])
website_url = st.text_input("🌍 Enter a website URL")

# --- Process PDF & Website ---
if uploaded_pdf and website_url:
    # Cache and store in session_state
    if "pdf_text" not in st.session_state:
        with st.spinner("Reading PDF..."):
            st.session_state["pdf_text"] = extract_pdf_text(uploaded_pdf)

    if "website_text" not in st.session_state:
        with st.spinner("Reading website..."):
            st.session_state["website_text"] = extract_website_text(website_url)

    # Chat history setup
    if "chat_history" not in st.session_state:
        st.session_state["chat_history"] = []

    # User question input
    with st.form("chat_form", clear_on_submit=True):
        user_question = st.text_input("💬 Ask a question based on the PDF + Website:")
        submitted = st.form_submit_button("Send")
    
    # Handle user question
    if submitted and user_question:
        with st.spinner("Thinking..."):
            response = ask_gemini(st.session_state["pdf_text"], st.session_state["website_text"], user_question)
            st.session_state["chat_history"].append(("You", user_question))
            st.session_state["chat_history"].append(("Bot", response))

    # Show chat history
    st.markdown("---")
    st.subheader("📜 Chat History")
    for sender, message in st.session_state["chat_history"]:
        if sender == "You":
            st.markdown(f"🧑 You:** {message}")
        else:
            st.markdown(f"🤖 Bot:** {message}")

else:
    st.info("Please upload a PDF and enter a website URL to start the chatbot.")