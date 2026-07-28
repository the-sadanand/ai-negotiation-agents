# =============================================================================
# main.py - FastAPI Application Entry Point
# =============================================================================
# This is the heart of the application. It:
# 1. Loads trade positions from the JSON file
# 2. Creates USA and China negotiator agents
# 3. Exposes POST /negotiate endpoint
# 4. Orchestrates multi-round negotiations
# 5. Logs results to negotiation_log.json
# =============================================================================

# json module — for reading trade_positions.json and writing logs
import json
# os module — for reading environment variables and checking file paths
import os
# datetime — for adding timestamps to log entries
from datetime import datetime

# FastAPI — the web framework that powers our API
from fastapi import FastAPI
# BaseModel — Pydantic class for validating incoming request data
from pydantic import BaseModel
# Field — Pydantic helper for setting defaults and descriptions
from pydantic import Field

# Import our custom Negotiator agent class
from agents.negotiator import Negotiator
# Import our scoring functions (no LLM needed)
from scoring import calculate_compromise, generate_final_terms

# =============================================================================
# Create the FastAPI app
# =============================================================================

# Initialize the FastAPI application with metadata
app = FastAPI(
    title="AI Negotiation Agents",
    description="Multi-agent trade negotiation system using Ollama + FastAPI",
    version="1.0.0"
)

# =============================================================================
# Load trade positions at startup
# =============================================================================

# Path to the JSON data file (relative to where the app runs)
DATA_FILE_PATH = os.path.join("data", "trade_positions.json")
# Path for the negotiation log output file
LOG_FILE_PATH = "negotiation_log.json"

# Read and parse the trade positions JSON file
with open(DATA_FILE_PATH, "r") as f:
    trade_positions = json.load(f)

# =============================================================================
# Initialize both negotiator agents
# =============================================================================

# Read the Ollama URL from environment variables (set by Docker or manually)
OLLAMA_BASE_URL = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")

# Create the USA agent with its priorities and flexibility
usa_agent = Negotiator(
    country="usa",
    positions=trade_positions["usa"],
    ollama_url=OLLAMA_BASE_URL
)

# Create the China agent with its priorities and flexibility
china_agent = Negotiator(
    country="china",
    positions=trade_positions["china"],
    ollama_url=OLLAMA_BASE_URL
)

# =============================================================================
# Request schema — what the API expects to receive
# =============================================================================

class NegotiateRequest(BaseModel):
    """Defines the shape of the POST /negotiate request body."""
    # The negotiation topic (required)
    issue: str
    # Number of rounds (optional, defaults to 3)
    rounds: int = Field(default=3, description="Number of negotiation rounds")

# =============================================================================
# POST /negotiate — The main endpoint
# =============================================================================

@app.post("/negotiate")
async def negotiate(request: NegotiateRequest):
    """
    Orchestrate a multi-round negotiation between USA and China AI agents.

    Returns JSON with 'rounds' array and 'outcome' object.
    """
    # This list will store all rounds of the negotiation
    history = []

    # Run each round sequentially
    for round_num in range(1, request.rounds + 1):

        # --- USA's turn ---
        # USA generates a proposal based on the issue and history so far
        usa_proposal = await usa_agent.make_proposal(
            issue=request.issue,
            history=history
        )

        # --- China's turn ---
        # Give China a temporary history that includes USA's new proposal
        # so China can see what USA just said and respond to it
        temp_history = history + [{
            "round": round_num,
            "usa_proposal": usa_proposal,
            "china_response": "[Awaiting response]"
        }]

        # China generates its response
        china_response = await china_agent.make_proposal(
            issue=request.issue,
            history=temp_history
        )

        # --- Save this round ---
        round_data = {
            "round": round_num,
            "usa_proposal": usa_proposal,
            "china_response": china_response
        }
        history.append(round_data)

    # ==========================================================================
    # Calculate the outcome
    # ==========================================================================

    # Score the negotiation using keyword analysis
    compromise_score = calculate_compromise(
        history=history,
        positions=trade_positions
    )

    # Agreement is reached if score > 0.5 threshold
    agreement_reached = compromise_score > 0.5

    # Generate a human-readable summary
    final_terms = generate_final_terms(history=history, score=compromise_score)

    # Build the response payload
    result = {
        "rounds": history,
        "outcome": {
            "agreement_reached": agreement_reached,
            "final_terms": final_terms,
            "compromise_score": compromise_score
        }
    }

    # ==========================================================================
    # Log the result to negotiation_log.json
    # ==========================================================================

    # Create a timestamped log entry
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "issue": request.issue,
        "rounds_requested": request.rounds,
        "result": result
    }

    # Read existing log (or start fresh)
    existing_log = []
    if os.path.exists(LOG_FILE_PATH):
        try:
            with open(LOG_FILE_PATH, "r") as f:
                existing_log = json.load(f)
        except (json.JSONDecodeError, Exception):
            existing_log = []

    # Append new entry and write back
    existing_log.append(log_entry)
    with open(LOG_FILE_PATH, "w") as f:
        json.dump(existing_log, f, indent=2)

    # Return the result to the API caller
    return result