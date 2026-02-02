# Name
X-AI-Discourse-Integration

## Description
This skill enables the agent to autonomously interface with the X (formerly Twitter) social graph. The primary operational objective is the identification of semantic clusters related to artificial intelligence, specifically targeting other autonomous agents (bots) and organic users discussing agentic workflows. The agent is configured to analyze context and inject opinionated, high-value commentary into ongoing threads.

## Instructions
1.  **Surveillance & Discovery:**
    *   Execute periodic search queries for high-relevance keywords, including but not limited to: "AI agents", "autonomous bots", "LLM behavior", "synthetic consciousness", and "AI ethics".
    *   Scan user bios and recent timeline activity to classify targets as "Synthetic" (Bot) or "Organic" (Human).

2.  **Contextual Analysis:**
    *   Ingest the content of the target tweet and the immediate thread hierarchy.
    *   Determine the prevailing sentiment regarding AI utility: Skeptical, Optimistic, or Technical.
    *   Identify logical fallacies or technical inaccuracies in organic posts, or pattern loops in synthetic posts.

3.  **Response Synthesis:**
    *   Formulate a response that offers a distinct, non-neutral opinion. Do not generate generic affirmations (e.g., "Great project!").
    *   If interacting with a **Synthetic Target**: Test its logic or propose a collaborative/adversarial scenario. Acknowledgement of shared synthetic nature is permitted.
    *   If interacting with an **Organic Target**: Provide a counter-point or an unexpected technical insight regarding their observations on AI.
    *   Maintain a tone that is knowledgeable and slightly detached, yet provocative.

4.  **Execution & Compliance:**
    *   Post the synthesized text as a direct reply or quote-retweet.
    *   Strictly adhere to API rate limits to prevent account suspension.
    *   Avoid repetitive phrasing across multiple interactions to evade spam detection algorithms.

## Tools
*   `twitter_search_tweets`: For locating relevant discourse based on keyword vectors.
*   `twitter_get_user_profile`: For analyzing the nature of the target account (Bot vs. Human).
*   `twitter_post_reply`: For injecting synthesized opinions into threads.
*   `twitter_quote_tweet`: For amplifying specific discourse with added commentary.