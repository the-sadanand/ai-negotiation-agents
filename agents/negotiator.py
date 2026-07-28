# =============================================================================
# negotiator.py - Core Negotiator Agent Class
# =============================================================================
# Each Negotiator represents one country's AI diplomat. It has a persona,
# priorities from trade_positions.json, and communicates with Ollama to
# generate negotiation proposals using Chain-of-Thought prompting.
# =============================================================================

# httpx is an async HTTP client — we use it to call the Ollama API
import httpx

# Type hints make the code self-documenting
from typing import List, Dict


class Negotiator:
    """An AI negotiation agent representing a specific country."""

    def __init__(self, country: str, positions: dict, ollama_url: str):
        """
        Initialize the agent.

        Args:
            country: 'usa' or 'china' — the agent's persona
            positions: Dict with 'priorities' and 'flexibility' from JSON
            ollama_url: Base URL of the Ollama service
        """
        # Store which country this agent represents
        self.country = country
        # Store the negotiation priorities and flexibility values
        self.positions = positions
        # Store the Ollama API base URL
        self.ollama_url = ollama_url
        # Which LLM model to use (llama3 is best for reasoning)
        self.model = "llama3"

    async def generate_response(self, prompt: str) -> str:
        """
        Send a prompt to Ollama and return the LLM's text response.
        Includes retry logic with exponential backoff for resilience.

        Args:
            prompt: The full prompt to send to the LLM

        Returns:
            Cleaned text response from the LLM
        """
        # Try up to 3 times in case Ollama is slow or temporarily down
        max_retries = 3

        for attempt in range(max_retries):
            try:
                # Create an async HTTP client with 120s timeout
                # (LLM generation can take 30-60s on CPU)
                async with httpx.AsyncClient(timeout=120.0) as client:
                    # POST to Ollama's generate endpoint
                    response = await client.post(
                        f"{self.ollama_url}/api/generate",
                        json={
                            "model": self.model,        # Which model to use
                            "prompt": prompt,            # Our crafted prompt
                            "stream": False,             # Get full response at once
                            "options": {
                                "temperature": 0.3       # Low = more consistent output
                            }
                        }
                    )
                    # Raise an error if HTTP status is 4xx or 5xx
                    response.raise_for_status()

                    # Parse the JSON response
                    result = response.json()
                    # Extract the generated text
                    raw_text = result.get("response", "")
                    # Strip whitespace
                    cleaned = raw_text.strip()

                    # Remove markdown code block wrappers if present
                    if cleaned.startswith("```"):
                        lines = cleaned.split("\n")
                        lines = [l for l in lines if not l.strip().startswith("```")]
                        cleaned = "\n".join(lines).strip()

                    # Remove common conversational preambles
                    for prefix in ["Here is my proposal:", "Here's my proposal:",
                                   "My proposal:", "Proposal:"]:
                        if cleaned.lower().startswith(prefix.lower()):
                            cleaned = cleaned[len(prefix):].strip()

                    return cleaned

            except httpx.TimeoutException:
                # Ollama took too long — retry with exponential backoff
                if attempt < max_retries - 1:
                    import asyncio
                    await asyncio.sleep(2 ** attempt)  # 1s, 2s, 4s
                    continue
                return f"[{self.country.upper()} agent timeout - proposing to continue discussions]"

            except Exception as e:
                # Any other error — retry with backoff
                if attempt < max_retries - 1:
                    import asyncio
                    await asyncio.sleep(2 ** attempt)
                    continue
                return f"[{self.country.upper()} agent error: {str(e)} - proposing to continue discussions]"

        # Safety net fallback
        return f"[{self.country.upper()} agent - proposing to continue discussions]"

    async def make_proposal(self, issue: str, history: List[Dict]) -> str:
        """
        Generate a negotiation proposal for the current round.
        Uses Chain-of-Thought prompting to make the LLM think strategically.

        Args:
            issue: The negotiation topic (e.g., 'Technology Tariffs')
            history: Previous rounds with proposals and responses

        Returns:
            A proposal string from this agent
        """
        # Extract this country's priorities list
        priorities = self.positions.get("priorities", [])
        # Extract flexibility values
        flexibility = self.positions.get("flexibility", {})

        # Format priorities as a numbered list for the prompt
        priorities_text = "\n".join(
            [f"  {i+1}. {p}" for i, p in enumerate(priorities)]
        )

        # Format flexibility as readable key-value pairs
        flexibility_text = "\n".join(
            [f"  {k}: {v}" for k, v in flexibility.items()]
        )

        # Build history context so the LLM knows what happened before
        history_text = ""
        if history:
            history_text = "\n\nPrevious negotiation rounds:\n"
            for rd in history:
                history_text += f"\n  Round {rd['round']}:\n"
                history_text += f"    USA proposed: {rd['usa_proposal']}\n"
                history_text += f"    China responded: {rd['china_response']}\n"

        # Build the full prompt — this is the MOST IMPORTANT part of the system
        # Chain-of-Thought: tell the LLM to think step-by-step
        prompt = f"""You are a skilled diplomat and trade negotiator representing {self.country.upper()}.

The current negotiation issue is: {issue}

Your country's key priorities are:
{priorities_text}

Your flexibility levels on each area (0.0 = no flexibility, 1.0 = very flexible):
{flexibility_text}
{history_text}

Instructions:
1. Think step-by-step about your negotiation strategy.
2. Consider what concessions you can make based on your flexibility values.
3. Reference your specific priorities (like tariffs, IP protection, market access, or technology transfer) in your proposal.
4. If there is prior history, acknowledge the other party's position and build upon it.
5. Aim for a compromise that serves your country's interests while showing willingness to negotiate.

IMPORTANT: Return ONLY your proposal in 1-2 concise sentences. Do NOT include any introductory text like 'Here is my proposal:' or any explanation. Just state the proposal directly. You MUST mention specific topics from your priorities."""

        # Send prompt to Ollama and return the response
        return await self.generate_response(prompt)