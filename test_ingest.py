#!/usr/bin/env python3
import os
import sys

# Set environment variables
os.environ['DATA_DIR'] = './data'
os.environ['VECTOR_STORE'] = 'memory'

# Add backend to path
sys.path.insert(0, './backend')

from app.settings import settings
from app.ingest import load_documents
from app.rag import RAGEngine, build_chunks_from_docs

try:
    print(f"Data dir: {settings.data_dir}")
    print(f"Vector store: {settings.vector_store}")
    
    print("\nLoading documents...")
    docs = load_documents(settings.data_dir)
    print(f"Loaded {len(docs)} sections from {len(set(d['title'] for d in docs))} files")
    
    print("\nBuilding chunks...")
    chunks = build_chunks_from_docs(docs, settings.chunk_size, settings.chunk_overlap)
    print(f"Built {len(chunks)} chunks")
    
    print("\nInitializing RAG engine...")
    engine = RAGEngine()
    
    print("\nIngesting chunks...")
    new_docs, new_chunks = engine.ingest_chunks(chunks)
    print(f"Ingested {new_docs} docs, {new_chunks} chunks")
    
    print("\n✓ Ingestion successful!")
except Exception as e:
    print(f"\n✗ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
