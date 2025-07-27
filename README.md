# fusion_agents

<body>
  <h1>Indian Hospital Query Bot </h1>

  <h2>Overview</h2>
  <p>This project fine-tunes and deploys a medical query assistant for hospital-style responses using LLMs. It uses a two-stage architecture for factual response generation and stylistic adaptation. The system also intelligently routes queries based on medical relevance.</p>

  <h2>1. Data Preparation for Fine-Tuning</h2>
  <ul>
    <li>Collected ~30,000 real-world patient-hospital email responses.</li>
    <li>Converted them to <code>{input, response}</code> format for supervised fine-tuning.</li>
    <li>Preprocessed for casing, punctuation normalization, and removal of PII.</li>
    <li>Tokenized using <code>tiktoken</code> compatible tokenizer.</li>
  </ul>

  <h3>Training Details</h3>
  <ul>
    <li>Trained on 3 epochs using LoRA on top of base LLM (e.g., Mistral / GPT-J).</li>
    <li>Used batch size of 32, AdamW optimizer, learning rate warmup.</li>
    <li>Trained using HuggingFace Trainer API with gradient checkpointing enabled.</li>
  </ul>

  <h2>2. Evaluation and Limitation Discovery</h2>
  <ul>
    <li>Post-training inference showed stylistic accuracy, but factual hallucinations.</li>
    <li>Hard-coded diagnoses and lack of medical reasoning found in some cases.</li>
    <li>Decided to separate medical generation logic from style generation logic.</li>
  </ul>

  <h2>3. Agent Architecture Integration</h2>
  <h3>LLM Reasoning Agent (LangGraph)</h3>
  <ul>
    <li>Built a LangGraph stateful agent with following state schema:
      <pre><code>AgentState = {
  query: str,
  topic: str,
  question: str,
  medical_answer: str,
  query_type: str,
  final_response: str,
  messages: List[BaseMessage]
}</code></pre></li>
    <li>Query is routed through a <code>query_router</code> to determine if it's medical.</li>
    <li>If medical, it's passed to <code>medical_llm_node</code> for factual answer generation.</li>
    <li>Final output is wrapped via <code>style_fusion_node</code> using the fine-tuned model.</li>
  </ul>

  <h3>Routing Logic</h3>
  <p>Node transitions:</p>
  <pre><code>"checkquery" → "query_router" → "medical" (if medical) → "stylefusion" → END
                        ↘ "notmedical" (if not medical) → "stylefusion" → END</code></pre>

  <h2>4. Output Style & Safety</h2>
  <ul>
    <li>Style of final responses is strictly matched to hospital tone via fused model.</li>
    <li>Fact accuracy is ensured by separating medical logic from style generator.</li>
    <li>Final output includes fail-safes for empty or irrelevant responses.</li>
  </ul>

  <h2>5. Example Flow</h2>
  <pre><code>Input: "I have a headache. What do I do?"
→ Query routed to medical
→ Base LLM generates a factual answer (e.g., migraine symptoms)
→ Style-fusion LLM wraps response in polite medical tone
→ Output delivered
  </code></pre>

  <h2>6. Future Enhancements</h2>
  <ul>
    <li>RAG fallback for rare medical terms or conditions.</li>
    <li>Self-verification to detect hallucinated diagnoses.</li>
    <li>Long context threading for patient history awareness.</li>
  </ul>

  <h2>7. Running the Bot</h2>
  <pre><code>Hospital_Chat = HospitalAgent()
response = Hospital_Chat.run("My father has high BP, what should we do?")</code></pre>

  <p>Make sure <code>graph1.py</code> and all routes are compiled without invalid nodes.</p>
</body>
