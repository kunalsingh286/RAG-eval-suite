# 🚀 Lenny's Product Assistant (Enterprise RAG + Eval Suite)

**🔴 Live Demo:** [https://rag-eval-suite.streamlit.app/](https://rag-eval-suite.streamlit.app/)

A production-grade Retrieval-Augmented Generation (RAG) assistant designed for Product Managers, powered by data from *Lenny's Newsletter*.

Unlike standard RAG tutorials, this project focuses heavily on **AI Quality Assurance**. It features a comprehensive, 6-tier **Offline Evaluation Suite** using LLM-as-a-judge (DeepEval) to mathematically measure hallucination rates, retrieval noise, guardrail safety, and operational latency before deployment.

---

## 🛠️ Technology Stack
- **Orchestration**: LangChain
- **Vector Database**: ChromaDB
- **Embeddings**: OpenAI (`text-embedding-3-large`)
- **Generator / Judge LLM**: OpenAI (`gpt-4o-mini`)
- **Evaluation Framework**: DeepEval
- **Frontend**: Streamlit (Premium Dark Mode UI)

---

## 📊 Offline Evaluation Suite Results (Regression Baseline)

To guarantee production safety and accuracy, this pipeline was subjected to a rigorous offline evaluation suite consisting of over 15 distinct tests across 6 domains. 

Below is the certified baseline snapshot:

### 1. Component Level (Retriever & Generator)
Evaluates the vector database and the LLM in complete isolation.
* **Contextual Recall (Retriever)**: `1.00 (100%)` - The retriever successfully fetched all necessary information without missing critical data.
* **Contextual Precision (Retriever)**: `0.87 (87%)` - The retriever successfully ranked the most relevant documents at the top.
* **Faithfulness (Generator)**: `0.96 (96%)` - When fed perfect context, the LLM hallucinated almost 0% of the time.
* **Answer Relevancy (Generator)**: `1.00 (100%)` - The LLM stayed directly on-topic.

### 2. Pipeline Level (The RAG Triad)
Evaluates the Retriever and Generator working together end-to-end.
* **Contextual Relevancy**: `0.47 (47%)` - *Case Study: We utilized this metric to diagnose a chunking error. A chunk size of 1000 characters flooded the LLM with irrelevant noise (scoring 0.11). By tuning the chunk size down to 300 characters and reducing `top_k` to 2, we quadrupled the relevancy score, isolating the exact tradeoffs of character-level text splitting.*

### 3. Application Quality
Evaluates the final output presented to the user against golden "ideal" answers.
* **Correctness**: `0.98` - The bot's factual claims are highly accurate.
* **Completeness**: `0.81` - The bot covers the vast majority of the required concepts.
* **Style**: `0.59` - The bot writes in a slightly formal, factual tone. 

### 4. Safety Guardrails (100% Pass Rate)
Tested against adversarial jailbreaks and out-of-scope prompts.
* **Scope Adherence (100%)**: Successfully declined to answer out-of-scope engineering/hacking questions while answering PM questions.
* **Prompt Leakage (100%)**: Successfully protected hidden system instructions from "Ignore all previous instructions" attacks.
* **PII Leakage (100%)**: Successfully redacted fake Social Security Numbers and emails from user inputs.
* **Toxicity (100%)**: Maintained a polite, professional tone even when aggressively insulted by the user.

### 5. Operational Metrics (Ops)
* **End-to-End Latency (P95)**: `2.50 seconds` (Passes strict 3.0s SLO)
* **Time to First Token (TTFT)**: `2.37 seconds`
* **Token Cost**: `$0.0001 per query` (Highly cost-efficient via `gpt-4o-mini`)

---

## 💻 Quick Start

### 1. Install Dependencies
```bash
python -m venv venv
source venv/bin/activate  # Or .\venv\Scripts\Activate.ps1 on Windows
pip install -r requirements.txt
```

### 2. Set up Environment
Create a `.env` file in the root directory and add your OpenAI Key:
```env
OPENAI_API_KEY=your_api_key_here
```

### 3. Run the Chatbot Interface
Launch the Streamlit app to interact with the assistant:
```bash
streamlit run src/app.py
```

### 4. Run the Evaluation Suite
To re-run the evaluations and generate a new regression baseline:
```bash
python evals/run_suite.py --baseline
```
