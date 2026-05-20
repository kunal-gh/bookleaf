<div align="center">

# 🏛️ BookLeaf AI Support Automation: Technical Architecture & System Design

**A Comprehensive Guide for Technical Evaluators and Non-Technical Stakeholders**

</div>

---

## 📖 1. The Big Picture (Plain English Overview)

Imagine BookLeaf Publishing has a super-smart receptionist working 24/7. Authors are constantly messaging this receptionist on WhatsApp, Email, and Instagram asking things like, *"Is my book live yet?"* or *"When will I get my royalties?"*. 

Normally, a human would have to:
1. Figure out who the author is (since they might email from a different address than their WhatsApp number).
2. Understand what the author is asking.
3. Look up the answer in a database or a rulebook.
4. Reply politely.

This project **automates that entire process**. 

It catches messages from any platform, uses Artificial Intelligence to instantly understand the question, merges the author's different profiles together into one identity, retrieves the correct data, and replies. **However, it has a strict safety rule:** if the AI is ever less than 80% confident about the answer, it stops immediately and hands the conversation over to a real human. This ensures BookLeaf never gives authors wrong information about their money or book timelines.

---

## 🛠️ 2. The Technology Stack

We chose a "Hybrid Architecture." This means we use visual, drag-and-drop tools for the easy routing parts, and custom-written code for the heavy, intelligent tasks. 

* **n8n (No-Code Automator):** Think of this as the traffic cop. It catches incoming messages from WhatsApp/Instagram and forwards them to our custom API.
* **FastAPI (Python):** The "Brain" of the operation. This is custom code that runs the logic pipeline. It is blazingly fast and highly customizable.
* **Supabase (PostgreSQL):** The filing cabinet. A modern database where we store author profiles, book statuses, and a log of every conversation.
* **OpenAI (GPT-4o-mini & text-embedding-3-small):** The artificial intelligence. Used to read the intent behind messages and draft polite replies.
* **Vercel / Ngrok:** For public deployment. The API is plug-and-play ready to be hosted on Vercel so anyone on the internet can test it.

---

## 🧩 3. Module-by-Module Breakdown

### Module A: The Channel Gateway (n8n)
* **What it does:** It listens to different communication channels. When a message arrives, it standardizes it into a single format (JSON) and sends it to our API Brain. 
* **Key Function:** It also listens for the response. If the API Brain says "Escalate to Human," n8n can route that ticket to a human dashboard (like Zendesk or Slack).

### Module B: The API Brain (FastAPI)
* **What it does:** This is where the magic happens. It exposes several "endpoints" (URLs that other computers can talk to):
  * `/chat`: The main pipeline that answers questions.
  * `/identity/resolve`: A specific tool just for merging author identities.
  * `/admin/identity-review`: A dashboard feed for human managers to review borderline identity matches.
  * `/health`: A quick pulse check to ensure the database is online.
* **Plug-and-Play AI:** The API is designed so that adding a real OpenAI API Key instantly upgrades the system from "Mock/Test Mode" to live AI reasoning without rewriting a single line of code.

### Module C: The Database (Supabase)
* **What it does:** Stores four main tables:
  1. `authors`: Names, emails, phones, and Instagram handles.
  2. `books`: Titles, ISBNs, final submission dates, live dates, and royalty statuses.
  3. `identity_mappings`: The administrative queue where borderline identity matches wait for human approval.
  4. `query_logs`: An un-deletable audit trail of every single question asked and answer given.

---

## 🛤️ 4. The 8-Stage Query Pipeline (Operation by Operation)

When an author sends a message, it travels through an exact 8-step assembly line inside `backend/main.py`:

#### Stage 1: Intent Classification (`intent_classifier.py`)
* **Operation:** Reads the message and categorizes it. 
* **Functions:** Uses OpenAI in "JSON Mode" to extract variables. For example, if the message is *"When is Echoes of Srinagar live?"*, it extracts: `Intent: publishing_timeline`, `Entities: {Book: "Echoes of Srinagar"}`.

#### Stage 2: Identity Resolution (`identity_unifier.py`)
* **Operation:** Figures out exactly who is messaging. It compares the incoming email or phone number against the database. If they don't match perfectly, it uses fuzzy logic (like autocorrect) to see if it's a close match.

#### Stage 3: Data Retrieval (`data_retriever.py`)
* **Operation:** Reaches into Supabase and grabs the author's record and their book data.
* **Edge Case Handling:** If an author has multiple books but didn't specify which one, the system pauses and asks the author to clarify instead of guessing.

#### Stage 4: Knowledge Base Search (`knowledge_base.py`)
* **Operation:** If the author asks a general policy question (e.g., *"How long does publishing take?"*), the system searches a Markdown rulebook (`bookleaf_kb.md`) using "Vector Math" (cosine similarity) to find the exact paragraph that answers the question.

#### Stage 5: Confidence Scoring (`confidence_scorer.py`)
* **Operation:** Grades the system's own homework. It runs a mathematical formula: `(Intent * 0.50) + (Identity * 0.30) + (KB Relevance * 0.20)`.

#### Stage 6: The Circuit Breaker (Escalation Check)
* **Operation:** Looks at the final grade from Stage 5. If the score is less than `0.80` (80%), the system pulls the emergency brake. It stops generating a response and triggers a human escalation workflow.

#### Stage 7: Response Generation (`response_generator.py`)
* **Operation:** If the score is safe (>80%), it feeds the database facts to OpenAI and asks it to write a friendly, 2-sentence reply. 

#### Stage 8: Audit Logging
* **Operation:** Saves everything (the user's original message, the bot's reply, the confidence score, and any errors) into the `query_logs` database table.

---

## 🔍 5. The Identity Unification Engine

Authors are messy—they use different emails, nicknames, and phone numbers. We built a 3-Tier engine to unify them safely:

1. **Tier 1 (Auto-Match):** If identifiers match exactly, or if the name is an extremely close typo (checked via the `rapidfuzz` library), the system gives a 100% confidence score and links the profile.
2. **Tier 2 (Borderline Arbitration):** If the match is iffy (e.g., Name is "Sara J." but database says "Sara Johnson", and they used a new Instagram handle), the system uses the LLM to guess the probability. If it's between 60% and 84%, the system creates a "Pending Review" ticket in the database. A human manager can review this in the Web UI Admin Tab.
3. **Tier 3 (Create New):** If the score is below 40%, the system safely assumes this is a brand new author and creates a new profile.

---

## 🚀 6. Future Possibilities & Scalability

This project is built as a highly scalable foundation. Moving forward, it can be expanded in several ways:

1. **Public Vercel Deployment:** Because the frontend is decoupled and the FastAPI backend is stateless, this entire architecture can be deployed to Vercel or Render with zero code changes. Stakeholders can test it live via a public URL.
2. **Multi-Agent Systems (LangGraph):** Currently, the pipeline is linear (Step 1 to Step 8). In the future, we can upgrade this to a Multi-Agent system where specialized AI agents (e.g., an "Audit Agent", an "Identity Agent", and a "Support Agent") talk to each other to solve even more complex problems dynamically.
3. **Enterprise Vector Databases (`pgvector`):** The current Knowledge Base is held in computer memory for speed. If BookLeaf's policy manual grows to thousands of pages, the system is perfectly structured to swap the memory cache for Supabase's `pgvector` database extension for massive scale.
4. **Direct Channel Webhooks:** While n8n handles routing beautifully, the FastAPI endpoints are fully compliant to receive direct incoming webhooks from Twilio (for WhatsApp) or Meta (for Instagram), bypassing middleware entirely for lower latency.
