from lightrag import LightRAG, QueryParam
import os

# Define your working directory for LightRAG
WORKING_DIR = "./lightrag_working_dir"

# Create the working directory if it doesn't exist
if not os.path.exists(WORKING_DIR):
    os.makedirs(WORKING_DIR)

# Initialize LightRAG instance
rag = LightRAG(
    working_dir=WORKING_DIR,
    llm_model_func=None  # Replace with your LLM model function if needed
)

# Insert a sample text document
sample_text = "A quick brown fox jumps over the lazy dog."
rag.insert(sample_text)

# Query the indexed data
query_result = rag.query(
    "What does the fox do?", 
    param=QueryParam(mode="naive")
)
print(query_result)

