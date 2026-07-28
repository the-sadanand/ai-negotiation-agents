# =============================================================================
# test_negotiation.py - Pytest Test Suite
# =============================================================================
# 9 tests that cover all 12 core requirements of the project spec.
# Uses FastAPI's TestClient to make HTTP requests without a running server.
# =============================================================================

# pytest — the test framework
import pytest
# json — for parsing response bodies
import json
# os — for file path checks
import os
# TestClient — lets us test FastAPI without starting a real server
from fastapi.testclient import TestClient
# Import our app and trade_positions
from main import app, trade_positions

# Create a test client wrapping our FastAPI app
client = TestClient(app)


# --- Test 1: Basic endpoint works ---
def test_negotiate_endpoint_returns_200():
    """POST /negotiate returns 200 with 'rounds' and 'outcome' keys."""
    response = client.post("/negotiate", json={"issue": "Test Issue", "rounds": 1})
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    data = response.json()
    assert "rounds" in data, "Response must contain 'rounds' key"
    assert "outcome" in data, "Response must contain 'outcome' key"


# --- Test 2: Requesting 3 rounds returns exactly 3 (Requirement 4 + 11) ---
def test_negotiate_returns_correct_number_of_rounds_three():
    """Requesting rounds=3 returns a rounds array of exactly length 3."""
    response = client.post("/negotiate", json={"issue": "Technology Tariffs", "rounds": 3})
    data = response.json()
    assert isinstance(data["rounds"], list), "'rounds' must be an array"
    assert len(data["rounds"]) == 3, f"Expected 3 rounds, got {len(data['rounds'])}"


# --- Test 3: Requesting 1 round returns exactly 1 ---
def test_negotiate_returns_correct_number_of_rounds_one():
    """Requesting rounds=1 returns a rounds array of exactly length 1."""
    response = client.post("/negotiate", json={"issue": "Test", "rounds": 1})
    data = response.json()
    assert len(data["rounds"]) == 1, f"Expected 1 round, got {len(data['rounds'])}"


# --- Test 4: Round objects have both USA and China (Requirement 5) ---
def test_round_objects_contain_both_agents():
    """Each round object has usa_proposal and china_response as non-empty strings."""
    response = client.post("/negotiate", json={"issue": "Trade Terms", "rounds": 2})
    data = response.json()
    first_round = data["rounds"][0]
    assert "usa_proposal" in first_round, "Must contain 'usa_proposal'"
    assert "china_response" in first_round, "Must contain 'china_response'"
    assert isinstance(first_round["usa_proposal"], str), "usa_proposal must be string"
    assert len(first_round["usa_proposal"]) > 0, "usa_proposal must not be empty"
    assert isinstance(first_round["china_response"], str), "china_response must be string"
    assert len(first_round["china_response"]) > 0, "china_response must not be empty"
    assert "round" in first_round, "Must contain 'round' number"


# --- Test 5: Outcome schema (Requirement 6) ---
def test_outcome_object_schema():
    """Outcome has agreement_reached (bool), final_terms (str), compromise_score (number)."""
    response = client.post("/negotiate", json={"issue": "Schema Test", "rounds": 1})
    data = response.json()
    outcome = data["outcome"]
    assert "agreement_reached" in outcome
    assert isinstance(outcome["agreement_reached"], bool)
    assert "final_terms" in outcome
    assert isinstance(outcome["final_terms"], str)
    assert "compromise_score" in outcome
    assert isinstance(outcome["compromise_score"], (int, float))


# --- Test 6: Score is between 0.0 and 1.0 (Requirement 7) ---
def test_compromise_score_is_normalized():
    """compromise_score must be >= 0.0 and <= 1.0."""
    response = client.post("/negotiate", json={"issue": "Score Test", "rounds": 2})
    data = response.json()
    score = data["outcome"]["compromise_score"]
    assert isinstance(score, (int, float)), f"Score must be numeric, got {type(score)}"
    assert score >= 0.0, f"Score must be >= 0.0, got {score}"
    assert score <= 1.0, f"Score must be <= 1.0, got {score}"


# --- Test 7: Agents reference their priorities (Requirement 8 + 12) ---
def test_agents_reference_priorities():
    """USA mentions tariff/IP keywords; China mentions market/transfer keywords."""
    response = client.post("/negotiate", json={"issue": "Technology Tariffs and Trade", "rounds": 2})
    data = response.json()
    # Combine all USA proposals
    all_usa = " ".join([r["usa_proposal"].lower() for r in data["rounds"]])
    # Combine all China responses
    all_china = " ".join([r["china_response"].lower() for r in data["rounds"]])
    # USA should mention at least one priority keyword
    usa_keywords = ["tariff", "ip", "protection", "intellectual", "property", "technology"]
    assert any(kw in all_usa for kw in usa_keywords), f"USA should reference priorities. Got: {all_usa[:200]}"
    # China should mention at least one priority keyword
    china_keywords = ["market", "access", "agricultural", "technology", "transfer"]
    assert any(kw in all_china for kw in china_keywords), f"China should reference priorities. Got: {all_china[:200]}"


# --- Test 8: Log file is created (Requirement 9) ---
def test_negotiation_log_created():
    """negotiation_log.json must be created after a negotiation."""
    log_path = "negotiation_log.json"
    response = client.post("/negotiate", json={"issue": "Log Test", "rounds": 1})
    assert response.status_code == 200
    assert os.path.exists(log_path), "negotiation_log.json should be created"
    with open(log_path, "r") as f:
        log_data = json.load(f)
    assert len(log_data) > 0, "Log should have at least one entry"
    assert "timestamp" in log_data[-1], "Log entry must have timestamp"
    assert "result" in log_data[-1], "Log entry must have result"


# --- Test 9: Default rounds = 3 ---
def test_default_rounds_value():
    """Omitting 'rounds' parameter should default to 3."""
    response = client.post("/negotiate", json={"issue": "Default Test"})
    data = response.json()
    assert len(data["rounds"]) == 3, f"Default should be 3 rounds, got {len(data['rounds'])}"