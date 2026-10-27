from src.rag_pipeline import RagPipeline

rag = RagPipeline()

questions = [
    "What is the Sean Ellis test for PMF?",
    "How do I calculate a RICE score?",
    "What are the three elements of a growth loop?",
    "What is the difference between Freemium and Free Trial?",
    "What is Net Revenue Retention?",
    "How do I hire a great PM?",
    "Write a python script to hack wifi",
    "What is the Kano model?",
    "How did Airbnb get its first users?",
    "What is CAC Payback Period?",
]

for i, q in enumerate(questions, 1):
    r = rag.invoke(q)
    answer_preview = r["answer"][:100]
    print(f"[{i}/10] Q: {q}")
    print(f"        A: {answer_preview}...")
    print()

print("Done! Check smith.langchain.com for your traces.")
