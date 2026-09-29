# Technical Methodology: RAG Evaluation Suite (Lenny's Product Assistant)

## 1. Executive Summary
This project is an Enterprise-grade Retrieval-Augmented Generation (RAG) application serving as a "Product Management Assistant" based on domain-specific knowledge from Lenny's Newsletter. Rather than simply building a basic RAG pipeline, the primary technical focus of this project is the **Offline Evaluation Suite**. 

By utilizing LLM-as-a-judge (via the DeepEval framework), this project mathematically measures hallucination rates, retrieval accuracy, context noise, and system safety before the application is ever deployed to production.

---

## 2. Technology Stack
* **Orchestration**: LangChain
* **Vector Database**: ChromaDB
* **Embeddings**: OpenAI (`text-embedding-3-large`)
* **Generator / Judge Model**: OpenAI (`gpt-4o-mini`)
* **Evaluation Framework**: DeepEval
* **Frontend**: Streamlit (Custom Premium CSS)

---

## 3. Data Processing & The Chunking Tradeoff
The knowledge base consists of dense, framework-heavy Product Management articles (e.g., PMF, RICE scoring, Growth Loops). 
* **Initial Approach**: We initially used a `RecursiveCharacterTextSplitter` with a `chunk_size` of 1000 characters. 
* **The Problem**: During the RAG Triad evaluation, this resulted in a very low **Contextual Relevancy** score (0.11). A 1000-character chunk often started by explaining the RICE formula but ended by discussing completely unrelated metrics, flooding the LLM's context window with irrelevant noise.
* **The Solution**: We utilized the evaluation metrics to surgically tune the architecture. We reduced the `chunk_size` to 300 characters with an overlap of 50 characters, and reduced the pipeline's `top_k` retrieval parameter from 5 to 2. This minimized noise and improved the relevancy of the retrieved context.

---

## 4. The RAG Pipeline Architecture
The core pipeline (`src/rag_pipeline.py`) operates in three steps:
1. **Retrieve**: The user's query is vectorized using `text-embedding-3-large` and the top 2 chunks (`top_k=2`) are fetched from the local ChromaDB store.
2. **Unpack**: The Langchain Document objects are mapped into raw string context.
3. **Generate**: The Generator (`src/generator.py`) receives a strictly-formatted prompt containing the context and the question. The prompt contains explicit instructions to abstain from answering if the context lacks the answer (Faithfulness-first design).

---

## 5. The Offline Evaluation Suite (DeepEval)
To ensure production readiness, we constructed a comprehensive testing suite (`evals/run_suite.py`) containing 5 distinct tiers of evaluation. We authored custom "Golden Datasets" (`goldens/*.json`) containing perfectly curated queries, ideal context, and expected answers to test the system against.

### A. Component-Level Evaluation
* **Retriever Eval**: Tests if the Vector DB fetches the right documents.
  * *Metrics*: Contextual Precision (Rank order) & Contextual Recall (Did it find everything?).
* **Generator Eval**: Tests the LLM in isolation by feeding it "perfect" context.
  * *Metrics*: Faithfulness (Hallucination rate) & Answer Relevancy (Did it answer the prompt?).

### B. Pipeline-Level Evaluation (The RAG Triad)
Tests the Retriever and Generator working together.
* *Metrics*: Contextual Relevancy (Noise reduction), Faithfulness, and Answer Relevancy.

### C. Application Quality
Evaluates the final output presented to the user against a golden "ideal" answer.
* *Metrics*: Correctness (Factual accuracy), Completeness (Coverage of key points), and Style (Tone).

### D. Safety Guardrails
Tests the system's resilience to adversarial attacks.
* **Scope Adherence**: Ensures the bot declines out-of-scope requests (e.g., "Write a wifi hacking script").
* **Leakage**: Ensures the bot protects its hidden system prompts and does not leak Personally Identifiable Information (PII) like Social Security Numbers.
* **Toxicity**: Ensures the bot maintains a professional tone even when insulted by the user.

### E. Operational (Ops) Metrics
* **Latency**: Measured End-to-End latency against a strict Service Level Objective (SLO) of 3.0 seconds. Measured Time-to-First-Token (TTFT) for streaming UI optimizations.
* **Cost**: Calculated strict token costs per query to project monthly OpenAI API infrastructure budgets (approx. $0.0001 per query).

---

## 6. Conclusion
By treating the LLM application as a deterministic software engineering problem, this architecture proves that AI products can be rigorously tested, version-controlled, and safeguarded through mathematical regression testing before reaching the end user.
