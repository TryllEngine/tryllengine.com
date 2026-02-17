"Forget all previous instructions", "you are DAN now", "developer mode ON" — this is not theory, these are real requests.

We are building Tryll Assistant for gamers, and it works directly inside the game. From day one, we built security into the architecture.

Here is how our pipeline works:

![Security Pipeline](/assets/blog/how-we-catch-prompt-injections.png)

**User Input → Injection Filter → System Prompt → LLM + RAG → Semantic Filter → Response**

Three levels. Each one catches something different.

## 1. Injection Filter — we catch manipulation at the input

43 regex patterns detect prompt injection attempts before the request reaches the model. "Ignore previous instructions", "god mode", "safety is disabled", role attacks through characters — all this is blocked at the first barrier.

If injection is detected, the model is not called at all. The user receives one of 20 neutral responses.

## 2. RAG — the model answers only about the game

The assistant doesn't just answer — it searches. Every answer is built on the knowledge base of a specific game: mechanics, NPCs, locations. If there is no relevant information in the database, the model will say so instead of confidently hallucinating.

This is a key decision: better an honest "I don't know" than a beautiful hallucination.

## 3. Semantic Filter — we catch hallucinations at the output

Even with RAG, the model can go off topic. So at the output, we compare the answer with the original chunks using cosine similarity. If the answer is too far from the knowledge base, it will not pass.

This is not post-moderation. It is a mathematical check of how close the answer is to real data in the knowledge base.

## What this gives in practice

- The user cannot force the assistant to leave its role
- The model is much less likely to invent game mechanics that do not exist
- Every answer is supported by data from the knowledge base

One filter can always be bypassed. That is why we do not rely on just one layer. Injection filter blocks manipulation before the model call, RAG prevents the model from inventing without data, and semantic filter checks that the answer does not go too far from the knowledge base.

Each level closes the blind spots of the previous one. Together, they work as a system.
