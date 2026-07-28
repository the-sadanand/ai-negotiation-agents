# =============================================================================
# scoring.py - Compromise Scoring Heuristic
# =============================================================================
# This module evaluates the negotiation outcome using keyword-based analysis.
# It does NOT call the LLM. It counts "concession" vs "combative" keywords
# in the negotiation text and produces a score between 0.0 and 1.0.
# =============================================================================

# Import type hints so function signatures are clear and self-documenting
from typing import List, Dict


# Main scoring function — analyzes all rounds of negotiation history
def calculate_compromise(history: List[Dict], positions: dict) -> float:
    """
    Analyze negotiation history and return a compromise score (0.0 to 1.0).

    Args:
        history: List of round dicts, each with 'usa_proposal' and 'china_response'
        positions: Initial trade positions from trade_positions.json

    Returns:
        Float between 0.0 (no compromise) and 1.0 (full compromise)
    """
    # Words that suggest the agent is willing to make concessions
    concession_keywords = [
        "agree",         # Direct agreement
        "accept",        # Accepting the other's terms
        "concede",       # Making a concession
        "willing",       # Showing willingness to negotiate
        "compromise",    # Directly mentioning compromise
        "lower",         # Lowering demands (e.g., tariff rates)
        "reduce",        # Reducing restrictions or barriers
        "flexible",      # Showing flexibility on positions
        "cooperate",     # Willingness to work together
        "collaborate",   # Working collaboratively toward a deal
        "mutual",        # Mutual benefit language
        "together",      # Working together
        "open to",       # Open to the other side's suggestions
        "consider",      # Willing to consider the other's position
        "accommodate",   # Accommodating the other party's needs
        "meet halfway",  # Classic compromise language
        "both sides",    # Acknowledging both parties
        "shared",        # Shared interests or goals
        "balanced",      # Balanced approach to the deal
        "fair",          # Fairness language
        "propose",       # Making a constructive proposal
        "offer",         # Offering something to the other side
        "support",       # Supporting a position or idea
        "acknowledge",   # Acknowledging the other side's concerns
        "understand",    # Understanding the other's needs
        "gradual",       # Gradual changes (patience)
        "phased",        # Phased approach (incremental steps)
        "reciprocal",    # Reciprocal terms (give and take)
    ]

    # Words that suggest the agent is being combative or uncompromising
    combative_keywords = [
        "reject",          # Rejecting a proposal outright
        "refuse",          # Refusing to negotiate
        "demand",          # Making hard, inflexible demands
        "insist",          # Insisting without any flexibility
        "non-negotiable",  # Marking items as cannot-change
        "unacceptable",    # Declaring terms unacceptable
        "oppose",          # Actively opposing the other side
        "never",           # Absolute refusal
        "impossible",      # Saying something is impossible
        "withdraw",        # Withdrawing from negotiations
        "retaliate",       # Threatening retaliation
        "punish",          # Punitive language
        "sanction",        # Threatening economic sanctions
        "block",           # Blocking proposals
        "veto",            # Vetoing proposals
    ]

    # Initialize counters — these track what kind of language was used
    concession_count = 0   # How many concession keywords were found
    combative_count = 0    # How many combative keywords were found
    priority_ref_count = 0 # How many priority topics were referenced

    # Build a list of all priority strings (lowercased) from both countries
    all_priorities = []
    # Get USA's priorities from the positions dict
    for p in positions.get("usa", {}).get("priorities", []):
        all_priorities.append(p.lower())  # Lowercase for case-insensitive matching
    # Get China's priorities from the positions dict
    for p in positions.get("china", {}).get("priorities", []):
        all_priorities.append(p.lower())  # Lowercase for case-insensitive matching

    # Loop through each round in the negotiation history
    for round_data in history:
        # Get USA's proposal text, default to empty string if missing
        usa_text = round_data.get("usa_proposal", "").lower()
        # Get China's response text, default to empty string if missing
        china_text = round_data.get("china_response", "").lower()
        # Combine both texts for easier scanning
        combined = usa_text + " " + china_text

        # Count concession keywords in this round's text
        for kw in concession_keywords:
            if kw in combined:       # Check if keyword appears anywhere in the text
                concession_count += 1  # Tally it

        # Count combative keywords in this round's text
        for kw in combative_keywords:
            if kw in combined:       # Check if keyword appears anywhere in the text
                combative_count += 1   # Tally it

        # Check if agents are discussing their actual priorities (on-topic check)
        for priority in all_priorities:
            words = priority.split()  # Split priority into individual words
            for word in words:
                # Only check words longer than 3 chars (skip "a", "the", "on", etc.)
                if len(word) > 3 and word in combined:
                    priority_ref_count += 1  # Found a priority reference
                    break  # One match per priority per round is enough

    # Calculate the total keyword matches
    total = concession_count + combative_count

    # If no keywords matched at all, return a neutral 0.5
    if total == 0:
        base_score = 0.5
    else:
        # Score = ratio of concession keywords to total keywords
        # More concession language = higher score
        base_score = concession_count / total

    # Small bonus (max 0.1) if agents referenced their actual priorities
    bonus = min(0.1, priority_ref_count * 0.005)

    # Final score = base + bonus, clamped between 0.0 and 1.0
    final = max(0.0, min(1.0, base_score + bonus))

    # Round to 2 decimal places for clean output
    return round(final, 2)


# Helper function to generate a human-readable summary of the final terms
def generate_final_terms(history: List[Dict], score: float) -> str:
    """
    Create a text summary of the negotiation outcome.

    Args:
        history: Full negotiation history
        score: The calculated compromise score

    Returns:
        A string summarizing the final terms
    """
    # If no rounds happened, say so
    if not history:
        return "No negotiation rounds were conducted."

    # Get the last round (most recent proposals)
    last = history[-1]
    # Extract final positions from both sides
    usa_final = last.get("usa_proposal", "No proposal")
    china_final = last.get("china_response", "No response")

    # Choose a status message based on the score
    if score > 0.6:
        status = "Both parties showed significant willingness to compromise."
    elif score > 0.4:
        status = "Partial progress was made, but significant gaps remain."
    else:
        status = "Limited compromise was achieved during negotiations."

    # Build and return the final terms string
    return (
        f"{status} "
        f"USA's final position: {usa_final} "
        f"China's final position: {china_final}"
    )