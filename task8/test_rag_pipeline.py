import os
import sys
import subprocess

# Ensure we can import backend packages
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

# 1. Install reportlab to generate a dummy PDF
print("Installing reportlab for test PDF generation...")
subprocess.run([sys.executable, "-m", "pip", "install", "reportlab"], stdout=subprocess.DEVNULL)

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

def create_sample_pdf(filename: str):
    print(f"Creating sample PDF: {filename}...")
    c = canvas.Canvas(filename, pagesize=letter)
    
    # Page 1
    c.drawString(100, 750, "Google DeepMind: History and Overview")
    c.drawString(100, 700, "Google DeepMind was founded in London, UK, in 2010 as DeepMind Technologies.")
    c.drawString(100, 680, "It was co-founded by Demis Hassabis, Shane Legg, and Mustafa Suleyman.")
    c.drawString(100, 660, "The company established a research lab to create general-purpose AI systems.")
    c.drawString(100, 640, "Google acquired DeepMind in 2014 for $500 million.")
    c.showPage()
    
    # Page 2
    c.drawString(100, 750, "AlphaGo and Breakthroughs")
    c.drawString(100, 700, "In 2016, DeepMind's AlphaGo program defeated Lee Sedol, a 9th-dan Go champion.")
    c.drawString(100, 680, "The match was held in Seoul, South Korea, and ended 4-1 in favor of AlphaGo.")
    c.drawString(100, 660, "AlphaGo used deep neural networks and Monte Carlo tree search.")
    c.drawString(100, 640, "Later, AlphaFold made historic breakthroughs in protein folding prediction.")
    c.showPage()
    
    c.save()
    print("PDF created successfully!")

# Generate PDF
pdf_name = "test_deepmind.pdf"
create_sample_pdf(pdf_name)

# 2. Test RAG Pipeline components
try:
    print("\n--- Testing PDF Extraction Service ---")
    from backend.services.pdf_service import extract_text
    pages_data = extract_text(pdf_name)
    for page in pages_data:
        print(f"Page {page['page']} (len={len(page['text'])}): {page['text'][:120]}...")
        
    print("\n--- Testing Chunking Service ---")
    from backend.services.chunk_service import ChunkService
    # Use smaller chunk sizes to verify splitting behavior on small texts
    chunk_service = ChunkService(chunk_size=150, chunk_overlap=30)
    chunks = chunk_service.chunk_document(pages_data, pdf_name)
    print(f"Generated {len(chunks)} chunks.")
    for idx, chunk in enumerate(chunks):
        print(f"Chunk {idx+1} [Page {chunk['metadata']['page']}]: {chunk['text']}")

    print("\n--- Testing Embedding Service ---")
    from backend.services.embedding_service import EmbeddingService
    embedding_service = EmbeddingService()
    chunk_texts = [c["text"] for c in chunks]
    embeddings = embedding_service.generate_embeddings(chunk_texts)
    print(f"Generated {len(embeddings)} embeddings, vector dimensions: {len(embeddings[0])}")

    print("\n--- Testing Vector DB Service ---")
    from backend.services.vector_service import VectorService
    vector_service = VectorService(db_path="./test_chroma_db")
    # Clean previous if any
    vector_service.delete_document(pdf_name)
    vector_service.add_documents(chunks, embeddings)
    
    docs = vector_service.list_documents()
    print("Currently indexed documents in DB:", docs)

    print("\n--- Testing Retrieval Search ---")
    query = "Who co-founded DeepMind and when?"
    query_emb = embedding_service.generate_query_embedding(query)
    results = vector_service.search_documents(query_emb, top_k=2)
    print(f"Query: '{query}'")
    for idx, res in enumerate(results):
        print(f"Result {idx+1} (Score={res['score']:.4f}, Page={res['page']}): {res['text']}")

    # Clean up test files
    print("\nCleaning up test files...")
    if os.path.exists(pdf_name):
        os.remove(pdf_name)
    
    # Release ChromaDB SQLite file lock on Windows
    del vector_service
    import gc
    gc.collect()

    import shutil
    if os.path.exists("./test_chroma_db"):
        try:
            shutil.rmtree("./test_chroma_db")
        except PermissionError:
            print("[INFO] test_chroma_db folder locked by active ChromaDB client session. Deferring delete to OS.")
    print("\nCleanup complete. All RAG components verified successfully!")

except Exception as e:
    print(f"\n[ERROR] Error verified: {e}")
    # Cleanup files on exception
    if os.path.exists(pdf_name):
        try:
            os.remove(pdf_name)
        except Exception:
            pass
    # Release file lock before exception cleanup
    try:
        del vector_service
    except NameError:
        pass
    import gc
    gc.collect()
    if os.path.exists("./test_chroma_db"):
        import shutil
        try:
            shutil.rmtree("./test_chroma_db")
        except Exception:
            pass
    sys.exit(1)
