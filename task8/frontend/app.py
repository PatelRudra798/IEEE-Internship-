import streamlit as st
from api_client import APIClient

# Initialize page configuration
st.set_page_config(
    page_title="Document QA System (RAG)",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize API Client
api_client = APIClient()

# Initialize session states
if "messages" not in st.session_state:
    st.session_state.messages = []
if "uploaded_filenames" not in st.session_state:
    st.session_state.uploaded_filenames = set()

# Custom CSS for modern premium design
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap');
    
    /* Global Font Overrides */
    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif;
    }
    
    /* Header background gradient title */
    .main-title {
        font-size: 2.6rem;
        font-weight: 700;
        background: linear-gradient(135deg, #60a5fa 0%, #3b82f6 50%, #1d4ed8 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
    }
    
    /* Document listing container */
    .doc-container {
        border-radius: 8px;
        padding: 10px;
        margin-bottom: 8px;
        background-color: rgba(30, 41, 59, 0.4);
        border: 1px solid rgba(255, 255, 255, 0.05);
    }
    
    /* Sleek source citation styling */
    .source-box {
        padding: 12px 16px;
        background-color: rgba(15, 23, 42, 0.6);
        border-left: 4px solid #3b82f6;
        border-radius: 0 10px 10px 0;
        margin-bottom: 12px;
        border-top: 1px solid rgba(255, 255, 255, 0.05);
        border-bottom: 1px solid rgba(255, 255, 255, 0.05);
        border-right: 1px solid rgba(255, 255, 255, 0.05);
    }
    
    .source-meta {
        font-size: 0.82rem;
        font-weight: 600;
        color: #94a3b8;
        margin-bottom: 6px;
    }
    
    .source-text {
        font-size: 0.9rem;
        font-style: italic;
        color: #e2e8f0;
        line-height: 1.4;
    }
    
    .score-badge {
        color: #34d399;
        font-weight: 700;
    }

    /* System Status Pills */
    .status-pill-online {
        padding: 5px 12px;
        border-radius: 30px;
        background-color: rgba(52, 211, 153, 0.1);
        color: #34d399;
        font-size: 0.78rem;
        font-weight: 600;
        display: inline-flex;
        align-items: center;
        gap: 6px;
        border: 1px solid rgba(52, 211, 153, 0.2);
    }
    
    .status-pill-offline {
        padding: 5px 12px;
        border-radius: 30px;
        background-color: rgba(248, 113, 113, 0.1);
        color: #f87171;
        font-size: 0.78rem;
        font-weight: 600;
        display: inline-flex;
        align-items: center;
        gap: 6px;
        border: 1px solid rgba(248, 113, 113, 0.2);
    }
    
    .dot {
        height: 7px;
        width: 7px;
        border-radius: 50%;
        display: inline-block;
    }
    .dot-online { background-color: #34d399; }
    .dot-offline { background-color: #f87171; }
</style>
""", unsafe_allow_html=True)

# Application Header
st.markdown("<h1 class='main-title'>📄 Document QA System</h1>", unsafe_allow_html=True)
st.write("Retrieval-Augmented Generation (RAG) assistant. Answered context is strictly limited to uploaded documents.")

# Fetch system connection state
is_backend_online = api_client.check_health()

# SIDEBAR: Configurations and Upload Controls
with st.sidebar:
    st.markdown("## ⚙️ System Config")
    
    # Status Pill
    if is_backend_online:
        st.markdown(
            '<div class="status-pill-online"><span class="dot dot-online"></span>Connected to Backend</div>', 
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            '<div class="status-pill-offline"><span class="dot dot-offline"></span>Connection Error</div>', 
            unsafe_allow_html=True
        )
        
    st.markdown("---")
    
    # File Upload Panel
    st.markdown("### 📥 Index Document")
    uploaded_files = st.file_uploader(
        "Upload PDF files",
        type=["pdf"],
        accept_multiple_files=True,
        disabled=not is_backend_online,
        label_visibility="collapsed"
    )
    
    if uploaded_files and is_backend_online:
        for file in uploaded_files:
            if file.name not in st.session_state.uploaded_filenames:
                with st.spinner(f"Indexing {file.name}..."):
                    try:
                        file_bytes = file.read()
                        res = api_client.upload_pdf(file_bytes, file.name)
                        st.toast(
                            f"Successfully parsed {file.name}! ({res.get('chunks_processed', 0)} chunks)",
                            icon="✅"
                        )
                        st.session_state.uploaded_filenames.add(file.name)
                        st.rerun()
                    except Exception as e:
                        st.error(f"Failed to upload {file.name}: {str(e)}")
                        
    st.markdown("---")
    
    # Documents Dashboard
    st.markdown("### 📁 Indexed Documents")
    if is_backend_online:
        try:
            indexed_docs = api_client.list_documents()
            
            # Sync session state filenames in case DB is modified externally (e.g. docker restart)
            db_filenames = {doc["filename"] for doc in indexed_docs}
            st.session_state.uploaded_filenames = db_filenames
            
            if not indexed_docs:
                st.info("No documents indexed. Upload a PDF to start.")
            else:
                st.write(f"Total documents: **{len(indexed_docs)}**")
                for doc in indexed_docs:
                    filename = doc["filename"]
                    chunks_count = doc["chunks_count"]
                    
                    # Render Document Dashboard list items
                    with st.container():
                        col_details, col_action = st.columns([5, 1])
                        with col_details:
                            st.markdown(f"📄 **{filename}**\n`{chunks_count} chunks`", help=filename)
                        with col_action:
                            if st.button("🗑️", key=f"del_{filename}"):
                                with st.spinner(f"Removing {filename}..."):
                                    try:
                                        api_client.delete_document(filename)
                                        if filename in st.session_state.uploaded_filenames:
                                            st.session_state.uploaded_filenames.remove(filename)
                                        st.toast(f"Deleted '{filename}' successfully.", icon="🗑️")
                                        st.rerun()
                                    except Exception as e:
                                        st.error(f"Failed to delete: {str(e)}")
        except Exception as e:
            st.error(f"Failed loading document registry: {e}")
    else:
        st.warning("Offline. Uploading and indexing disabled.")
        
    st.markdown("---")
    if st.button("🧹 Clear Chat History", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# MAIN WORKSPACE: Chat Logs and Query Input
if not is_backend_online:
    st.error(
        "🚨 Connection Error: Unable to communicate with the FastAPI backend. "
        "Please check that the server is active on port 8000 and CORS configurations are set."
    )
else:
    # Render chat logs
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            
            # Render source citations if they exist
            if message["role"] == "assistant" and message.get("sources"):
                with st.expander("🔍 View Retrieved Sources"):
                    for src in message["sources"]:
                        doc_name = src["document"]
                        page_num = src["page"]
                        text_snippet = src["text"]
                        score = src["score"]
                        
                        st.markdown(f"""
                        <div class="source-box">
                            <div class="source-meta">
                                📄 {doc_name} &bull; Page {page_num} &bull; Similarity: <span class="score-badge">{score:.2%}</span>
                            </div>
                            <div class="source-text">
                                "{text_snippet}"
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

    # Chat Input Box
    if user_query := st.chat_input("Ask a question about the uploaded documents..."):
        # Immediately display user input
        with st.chat_message("user"):
            st.markdown(user_query)
            
        st.session_state.messages.append({"role": "user", "content": user_query})
        
        # Call backend for response
        with st.chat_message("assistant"):
            with st.spinner("Searching document context and generating answer..."):
                try:
                    response = api_client.ask_question(user_query)
                    answer = response["answer"]
                    sources = response["sources"]
                    
                    st.markdown(answer)
                    
                    # Display retrieved sources
                    if sources:
                        with st.expander("🔍 View Retrieved Sources"):
                            for src in sources:
                                doc_name = src["document"]
                                page_num = src["page"]
                                text_snippet = src["text"]
                                score = src["score"]
                                
                                st.markdown(f"""
                                <div class="source-box">
                                    <div class="source-meta">
                                        📄 {doc_name} &bull; Page {page_num} &bull; Similarity: <span class="score-badge">{score:.2%}</span>
                                    </div>
                                    <div class="source-text">
                                        "{text_snippet}"
                                    </div>
                                </div>
                                """, unsafe_allow_html=True)
                    
                    # Store assistant message in history
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": answer,
                        "sources": sources
                    })
                    
                except Exception as e:
                    error_message = f"Error: {str(e)}"
                    st.error(error_message)
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": f"I encountered an error while retrieving or processing context: {str(e)}",
                        "sources": []
                    })
