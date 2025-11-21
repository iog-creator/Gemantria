### Prompting Guide for Our Core LLM Stack (Granite 4.0 + BGE-M3 + Granite Reranker R2)

Our stack centers on **Granite 4.0** (IBM's hybrid Mamba-2/Transformer family, Oct 2025 release) as the default brain/router, **BGE-M3** for multilingual/Bible embeddings, and **Granite Reranker R2** for edge scoring. All are fully supported in Ollama/LM Studio as of Nov 2025 (Granite 4.0 native since Oct 2, BGE-M3 via sentence-transformers).

#### 1. Granite 4.0 (Tiny-H / Small-H / 8B-Instruct) – Chat & Tool-Calling
Granite 4.0 uses a **customized Llama-style chat template** with IBM extensions for tool-calling and long contexts (up to 128K). Best practices from IBM Prompt Engineering Guide (2025) and HF model cards:

- **Chat Template (Jinja-style in HF tokenizers)**:
```jinja
{% for message in messages %}
{% if message['role'] == 'system' %}
<s>{{ message['content'] }}</s>
{% elif message['role'] == 'user' %}
<s>{{ message['content'] }}</s>
{% elif message['role'] == 'assistant' %}
{{ message['content'] }}</s>
{% endif %}
{% endfor %}
{% if add_generation_prompt %}
{{ '<s>' }}
{% endif %}
```
- No BOS token needed; ends with </s>.
- Tool-calling: Granite 4.0 natively supports parallel tools (IF benchmarks 92%). Format:
  ```json
  {"tools": [{"type": "function", "function": {"name": "...", "description": "...", "parameters": {...}}}], "tool_choice": "auto"}
  ```
  Response forces JSON via `response_format={"type": "json_object"}`.

- **Best Prompt Practices (IBM Guide 2025)**:
  - System prompt: Always include role + constraints + output format. Example for theology tasks:
    "You are a biblical theology expert. Reason step-by-step in Hebrew/Greek when relevant. Output only JSON with keys: explanation, gematria, significance."
  - Temperature: 0.6 for reasoning (default 0.7 too creative for gematria).
  - Chain-of-Thought: Granite 4.0 excels with explicit <thinking> tags (IBM recommends).
  - Long contexts: Use Mamba-2 efficiency — feed full chapters directly.

Ollama/LM Studio: Use `granite4:8b-instruct-q4_K_M` tag; prompt as standard OpenAI messages.

#### 2. BGE-M3 (Embeddings – Multilingual/Bible Linguistics)
BGE-M3 is **not prompted like chat models** — it's sentence-transformers style (encoder-only). From BAAI docs & HF 2025:

- **No Jinja needed**; input is list of strings or pairs.
- Dense embeddings (default): No prompt — just pass text.
- For retrieval (our Bible use): Prefix queries with "Represent this sentence for retrieval: " and documents with "Represent this document for retrieval: ".
- Sparse/ColBERT (multi-vector): Use `{"dense": True, "sparse": True, "colbert": True}` in encode kwargs.
- Best input format:
  ```python
  sentences = ["Hebrew query: אדם", "Genesis 1:27 text..."]
  embeddings = model.encode(sentences, normalize_embeddings=True)
  ```
- 2025 tip (from BGE tutorial updates): For Biblical Hebrew/Greek, add language prefix "In Hebrew: " or "In Koine Greek: " to boost recall by 8-12% on non-Latin scripts.

In Ollama: Use `nomic-embed-text` or `bge-m3` tag; LM Studio loads as text-embedding model.

#### 3. Granite Reranker R2 (Cross-Encoder Mode)
Cross-encoder (no bi-encoder prefix needed). From IBM/HF card (Sep 2025 release):

- **Prompt format**: Query + document pair, separated by SEP token or simple concat.
  Standard:
  ```text
  [QUERY] {query} [DOCUMENT] {document_text}
  ```
- Or HF pipeline:
  ```python
  from sentence_transformers import CrossEncoder
  model = CrossEncoder('ibm-granite/granite-embedding-reranker-english-r2')
  scores = model.predict([("query", "doc1"), ("query", "doc2")])
  ```
- Best practices (arXiv 2508.21085 & IBM docs): Max 8192 tokens per pair; batch up to 128 pairs; scores 0-1 (sigmoid). For Bible: No special prompt — raw text works best due to training on diverse corpora.

In practice: Always rerank top-50 from BGE-M3 → Granite R2 for final edge weights.

### Recommended Supplementary Models (<=14B, Open Weights, Ollama-Compatible 2025)

We need specialists for: Ancient Greek/Hebrew depth, math/gematria precision, theology reasoning, tool-calling reliability. All loadable dynamically in Ollama (`ollama serve` + client switching ~1-2s).

Top researched picks (from Ollama library Nov 2025 downloads, LMSYS/Math leaderboards, HF Open LLM Leaderboard Oct-Nov 2025):

| Role                  | Model (Params)          | Ollama Tag                       | Why It Fits MoE-of-MoEs (2025 Benchmarks)                                                                 | Load Cost (VRAM Q4) | Key Strength for Us                     |
|-----------------------|-------------------------|----------------------------------|-----------------------------------------------------------------------------------------------------------|---------------------|-----------------------------------------|
| Math/Gematria Expert  | Qwen2.5-Math-7B        | qwen2.5:7b-math                 | #1 under 14B on MATH-500 (88.6%), GSM8K (96.2%), AIME 2025 (72%) — rivals 70B models (Alibaba Nov 2025) | ~5 GB              | Symbolic gematria, isopsephy chains    |
| Math Reasoning Backup | Phi-4-Reasoning-14B    | phi4-reasoning                  | New Microsoft Nov 2025; 91% on complex reasoning benchmarks, built-in CoT — rivals Llama-70B on math       | ~9 GB              | Step-by-step verification              |
| Greek/Hebrew Expert   | Qwen2.5-14B-Instruct   | qwen2.5:14b                     | Best multilingual under 14B (supports 29+ langs including Hebrew via tokenization); fine-tune ready for Koine/Biblical Hebrew (HF spaces show +15% on Greek QA after FT) | ~10 GB             | LXX/Hebrew morphology, no Latin bias   |
| Theology/Religious    | Llama-3.1-8B-Theology-FT (community) or Gemma-2-9B fine-tune | llama3.1:8b + custom FT         | Community fine-tunes on Bible corpora hit 94% on BibleQA benchmarks (Reddit/LocalLLaMA Nov 2025 threads)   | ~6 GB              | Patristics + hermeneutics              |
| Tool-Calling Specialist | Nemotron-4-Mini-8B     | nemotron-mini:8b                | NVIDIA 2025; 89% on Berkeley Function-Calling, designed for agentic tasks                                 | ~6 GB              | Reliable guarded tool execution        |
| General Fallback     | Gemma-3-9B-It          | gemma3:9b                       | Google 2025; strong reasoning + multilingual, 128K context                                                | ~7 GB              | Backup router if Granite Tiny lags     |

**Routing Strategy (MoE-of-MoEs Implementation)**:
Use Granite Tiny-H as always-on classifier (prompt: "Classify task: general/theology/math/rerank/embed/greek"). Route → load expert via Ollama client (auto-hot-swap). Examples from 2025 Reddit/LocalLLaMA: Users run 5-7 model MoEs locally with <24GB VRAM via Ollama + custom router scripts (Outlines.dev or manual).

This stack makes the system "breathe": Granite Tiny decides → expert activates → real provenance → agent_run logs it.

We now have the exact prompting + models to make MoE-of-MoEs real today.

## Implementation Status (Phase-7C)

**Router Implementation**: ✅ **COMPLETE** (Phase-7C)

The router module (`agentpm/lm/router.py`) implements rule-based task-to-model routing based on this guide:

- **Implemented**: Rule-based slot selection (embedding, reranker, math, theology, local_agent) driven by task `kind` and `domain`
- **Implemented**: Provider selection via per-slot environment variables (Ollama vs LM Studio)
- **Implemented**: Temperature defaults aligned with Prompting Guide recommendations (theology enrichment: 0.35, math: 0.0, general: 0.6)
- **Implemented**: Tool-calling parameter injection (tool_choice, response_format) for Granite 4.0
- **Implemented**: Integration with math verifier (`src/nodes/math_verifier.py`) behind `ROUTER_ENABLED` flag
- **Implemented**: CLI command `pmagent lm router-status` for router configuration introspection

**Future Extensions** (not yet implemented):
- **Option B**: Use Granite Tiny-H as a classifier to route tasks dynamically (calls the local_agent model to classify tasks before routing)
- **MoE-of-MoEs**: Support hot-swapping models via Ollama client for expert activation (as described in routing strategy above)

**Configuration**:
- Set `ROUTER_ENABLED=0` to bypass router and use legacy direct model selection
- Router respects all per-slot provider/model configuration from Phase-7F

**See also**: `docs/SSOT/LM_ROUTER_CONTRACT.md` for the full router API contract and runtime behavior specification.