#!/usr/bin/env python3
"""
LangGraph-based debugging workflow for AI noun discovery issues.

This script systematically investigates why AI noun discovery returns 0 nouns
despite successful API calls and infrastructure being in place.
"""

import json
import os
import time
from typing import Any, Dict, List, TypedDict

from langgraph.graph import StateGraph
from src.infra.structured_logger import get_logger, log_json
from src.nodes.ai_noun_discovery import AINounDiscovery
from src.infra.db import get_bible_ro
from src.services.lmstudio_client import chat_completion, assert_qwen_live
from src.inference.router import pick
from src.infra.env_loader import ensure_env_loaded

LOG = get_logger("debug_noun_discovery")


class DebugState(TypedDict):
    """State for the debugging workflow."""

    book: str
    env_status: Dict[str, Any]
    db_status: Dict[str, Any]
    ai_status: Dict[str, Any]
    text_extraction: Dict[str, Any]
    prompt_analysis: Dict[str, Any]
    ai_response: Dict[str, Any]
    parsing_result: Dict[str, Any]
    validation_result: Dict[str, Any]
    final_diagnosis: str
    recommendations: List[str]


def check_environment(state: DebugState) -> DebugState:
    """Check environment variables and configuration."""
    ensure_env_loaded()  # Load environment variables from .env file
    log_json(LOG, 20, "debug_env_check_start")

    env_status = {
        "BIBLE_DB_DSN": bool(os.getenv("BIBLE_DB_DSN")),
        "GEMATRIA_DSN": bool(os.getenv("GEMATRIA_DSN")),
        "LM_STUDIO_HOST": os.getenv("LM_STUDIO_HOST", "not set"),
        "THEOLOGY_MODEL": os.getenv("THEOLOGY_MODEL", "not set"),
        "ENFORCE_QWEN_LIVE": os.getenv("ENFORCE_QWEN_LIVE", "not set"),
        "MAX_AI_CALLS_PER_RUN": os.getenv("MAX_AI_CALLS_PER_RUN", "500"),
    }

    # Test model router configuration
    try:
        cfg = pick("discovery")
        env_status["model_router"] = {"model": cfg.get("model"), "available": True}
    except Exception as e:
        env_status["model_router"] = {"error": str(e), "available": False}

    log_json(LOG, 20, "debug_env_check_complete", env_status=env_status)
    return {**state, "env_status": env_status}


def check_database(state: DebugState) -> DebugState:
    """Check database connectivity and data availability."""
    log_json(LOG, 20, "debug_db_check_start")

    db_status = {"bible_db": False, "gematria_db": False, "data_available": False}

    # Check Bible DB
    try:
        bible_conn = get_bible_ro()
        # Try a simple query
        rows = list(bible_conn.execute("SELECT COUNT(*) FROM bible.verses WHERE book_name = 'Gen'"))
        db_status["bible_db"] = True
        db_status["bible_verses_count"] = rows[0][0] if rows else 0
    except Exception as e:
        db_status["bible_db_error"] = str(e)

    # Check Gematria DB
    try:
        from src.infra.db import get_gematria_rw

        gematria_conn = get_gematria_rw()
        # Try a simple query
        rows = list(gematria_conn.execute("SELECT COUNT(*) FROM concept_network"))
        db_status["gematria_db"] = True
        db_status["existing_nodes"] = rows[0][0] if rows else 0
    except Exception as e:
        db_status["gematria_db_error"] = str(e)

    # Check if Hebrew text is available for the book
    if db_status["bible_db"]:
        try:
            book = state["book"]
            book_map = {"Genesis": "Gen", "Exodus": "Exo", "Leviticus": "Lev", "Numbers": "Num", "Deuteronomy": "Deu"}
            db_book = book_map.get(book, book[:3])

            rows = list(
                get_bible_ro().execute(
                    """
                SELECT COUNT(hw.word_text) as word_count
                FROM bible.hebrew_ot_words hw
                JOIN bible.verses v ON hw.verse_id = v.verse_id
                WHERE v.book_name = %s AND LEFT(hw.strongs_id, 1) = 'H'
                """,
                    (db_book,),
                )
            )
            db_status["hebrew_words_available"] = rows[0][0] if rows else 0
            db_status["data_available"] = db_status["hebrew_words_available"] > 0
        except Exception as e:
            db_status["data_extraction_error"] = str(e)

    log_json(LOG, 20, "debug_db_check_complete", db_status=db_status)
    return {**state, "db_status": db_status}


def check_ai_connectivity(state: DebugState) -> DebugState:
    """Check AI model connectivity and health."""
    log_json(LOG, 20, "debug_ai_check_start")

    ai_status = {"qwen_live": False, "models_available": {}}

    # Check Qwen health
    try:
        assert_qwen_live()
        ai_status["qwen_live"] = True
    except Exception as e:
        ai_status["qwen_live_error"] = str(e)

    # Test individual models
    models_to_test = ["text-embedding-bge-m3", "qwen.qwen3-reranker-0.6b", "christian-bible-expert-v2.0-12b"]

    for model in models_to_test:
        try:
            # Simple test call
            messages = [{"role": "user", "content": "Hello"}]
            chat_completion(messages, model=model, max_tokens=10, temperature=0)
            ai_status["models_available"][model] = True
        except Exception as e:
            ai_status["models_available"][model] = False
            ai_status[f"{model}_error"] = str(e)

    log_json(LOG, 20, "debug_ai_check_complete", ai_status=ai_status)
    return {**state, "ai_status": ai_status}


def analyze_text_extraction(state: DebugState) -> DebugState:
    """Analyze the Hebrew text extraction process."""
    log_json(LOG, 20, "debug_text_extraction_start")

    text_extraction = {"raw_text_length": 0, "sampling_applied": False, "sampled_length": 0}

    if not state["db_status"]["bible_db"]:
        text_extraction["error"] = "Bible DB not available"
        return {**state, "text_extraction": text_extraction}

    try:
        discoverer = AINounDiscovery()
        raw_text = discoverer._get_raw_hebrew_text(discoverer.book_map.get(state["book"], state["book"][:3]))

        text_extraction["raw_text_length"] = len(raw_text)

        if raw_text:
            # Test the sampling logic
            sampled = discoverer._sample_text(raw_text)
            text_extraction["sampled_length"] = len(sampled)
            text_extraction["sampling_applied"] = len(sampled) < len(raw_text)
            text_extraction["sample_preview"] = sampled[:200] + "..." if len(sampled) > 200 else sampled

        log_json(LOG, 20, "debug_text_extraction_complete", text_extraction=text_extraction)
    except Exception as e:
        text_extraction["error"] = str(e)
        log_json(LOG, 40, "debug_text_extraction_error", error=str(e))

    return {**state, "text_extraction": text_extraction}


def analyze_prompt_and_response(state: DebugState) -> DebugState:
    """Analyze the AI prompt construction and response handling."""
    log_json(LOG, 20, "debug_prompt_analysis_start")

    prompt_analysis = {"prompt_constructed": False, "ai_call_made": False, "response_received": False}

    if not state["text_extraction"]["raw_text_length"]:
        prompt_analysis["error"] = "No text available for analysis"
        return {**state, "prompt_analysis": prompt_analysis}

    try:
        discoverer = AINounDiscovery()
        raw_text = discoverer._get_raw_hebrew_text(discoverer.book_map.get(state["book"], state["book"][:3]))

        if not raw_text:
            prompt_analysis["error"] = "Raw text extraction failed"
            return {**state, "prompt_analysis": prompt_analysis}

        # Construct the prompt (replicate the logic from ai_noun_discovery.py)
        sampled_text = discoverer._sample_text(raw_text)
        prompt = f"""
        Analyze this Hebrew text from {state["book"]} and discover significant nouns.

        For each noun you discover:
        1. Extract the original Hebrew word
        2. Break it down into individual Hebrew letters
        3. Calculate its gematria (numerical) value
        4. Classify it as: person, place, or thing
        5. Provide a brief theological/contextual meaning
        6. Note its first occurrence in the text

        Focus on nouns that appear to be significant for biblical theology.
        Return in JSON format with array of noun objects.

        Hebrew text sample:
        {sampled_text}

        Return format:
        {{
            "nouns": [
                {{
                    "hebrew": "אברהם",
                    "letters": ["א", "ב", "ר", "ה", "ם"],
                    "gematria": 248,
                    "classification": "person",
                    "meaning": "Father of many nations",
                    "primary_verse": "Genesis 11:27",
                    "freq": 5
                }}
            ]
        }}
        """

        prompt_analysis["prompt_constructed"] = True
        prompt_analysis["prompt_length"] = len(prompt)
        prompt_analysis["sampled_text_used"] = len(sampled_text)

        # Try the AI call with detailed logging

        try:
            cfg = pick("discovery")
            model = cfg["model"]

            messages_batch = [
                [
                    {
                        "role": "system",
                        "content": "You are a Hebrew language expert specializing in biblical text analysis.",
                    },
                    {"role": "user", "content": prompt},
                ]
            ]

            start_time = time.time()
            results = chat_completion(messages_batch, model=model, temperature=0.1)
            call_time = int((time.time() - start_time) * 1000)  # Convert to ms

            prompt_analysis["ai_call_made"] = True
            prompt_analysis["call_time_ms"] = call_time
            prompt_analysis["response_received"] = bool(results)

            if results:
                content = results[0].text
                prompt_analysis["response_length"] = len(content)
                prompt_analysis["response_preview"] = content[:500] + "..." if len(content) > 500 else content

                # Store for next step
                ai_response = {"content": content, "call_time_ms": call_time, "model": model}
            else:
                ai_response = {"error": "No results from AI call"}

        except Exception as e:
            prompt_analysis["ai_call_error"] = str(e)
            ai_response = {"error": str(e)}

        log_json(LOG, 20, "debug_prompt_analysis_complete", prompt_analysis=prompt_analysis)

    except Exception as e:
        prompt_analysis["error"] = str(e)
        ai_response = {"error": str(e)}
        log_json(LOG, 40, "debug_prompt_analysis_error", error=str(e))

    return {**state, "prompt_analysis": prompt_analysis, "ai_response": ai_response}


def analyze_parsing_and_validation(state: DebugState) -> DebugState:
    """Analyze the response parsing and noun validation."""
    log_json(LOG, 20, "debug_parsing_analysis_start")

    parsing_result = {"parsing_attempted": False, "nouns_parsed": 0, "validation_attempted": False}

    if "error" in state["ai_response"]:
        parsing_result["error"] = f"AI response error: {state['ai_response']['error']}"
        return {**state, "parsing_result": parsing_result}

    try:
        discoverer = AINounDiscovery()
        content = state["ai_response"]["content"]

        # Try parsing
        parsed = discoverer._parse_ai_response(content)
        parsing_result["parsing_attempted"] = True

        if "nouns" in parsed:
            parsing_result["nouns_parsed"] = len(parsed["nouns"])
            parsing_result["parsed_data"] = parsed

            # Try validation
            raw_text = discoverer._get_raw_hebrew_text(discoverer.book_map.get(state["book"], state["book"][:3]))

            validated = discoverer._validate_and_enhance_nouns(parsed["nouns"], raw_text, state["book"])
            parsing_result["validation_attempted"] = True
            parsing_result["nouns_validated"] = len(validated)
            parsing_result["validated_nouns"] = validated

        log_json(LOG, 20, "debug_parsing_analysis_complete", parsing_result=parsing_result)

    except Exception as e:
        parsing_result["error"] = str(e)
        log_json(LOG, 40, "debug_parsing_analysis_error", error=str(e))

    return {**state, "parsing_result": parsing_result}


def generate_diagnosis_and_recommendations(state: DebugState) -> DebugState:
    """Generate final diagnosis and recommendations."""
    log_json(LOG, 20, "debug_diagnosis_start")

    diagnosis_parts = []
    recommendations = []

    # Environment issues
    if not state["env_status"]["BIBLE_DB_DSN"]:
        diagnosis_parts.append("BIBLE_DB_DSN environment variable not set - cannot access Hebrew text")
        recommendations.append("Set BIBLE_DB_DSN environment variable to connect to Bible database")

    if not state["ai_status"]["qwen_live"]:
        diagnosis_parts.append("Qwen models not live or accessible")
        recommendations.append("Ensure LM Studio is running with required models loaded")

    # Database issues
    if not state["db_status"]["bible_db"]:
        diagnosis_parts.append("Bible database not accessible")
        recommendations.append("Check BIBLE_DB_DSN and database connectivity")

    if state["db_status"].get("hebrew_words_available", 0) == 0:
        diagnosis_parts.append("No Hebrew words available for the specified book")
        recommendations.append("Verify book name mapping and database content")

    # Text extraction issues
    if state["text_extraction"]["raw_text_length"] == 0:
        diagnosis_parts.append("Hebrew text extraction failed")
        recommendations.append("Debug database queries and book name mappings")

    # AI call issues
    if not state["prompt_analysis"]["ai_call_made"]:
        diagnosis_parts.append("AI call not successfully made")
        recommendations.append("Check model availability and LM Studio connectivity")

    if state["ai_response"].get("error"):
        diagnosis_parts.append(f"AI call failed: {state['ai_response']['error']}")
        recommendations.append("Check LM Studio logs and model loading")

    # Parsing issues
    if state["parsing_result"].get("nouns_parsed", 0) == 0 and state["prompt_analysis"]["response_received"]:
        diagnosis_parts.append("AI returned response but parsing found 0 nouns")
        recommendations.append("Analyze AI prompt effectiveness and response format")
        recommendations.append("Check if AI model understands the task requirements")

    # Validation issues
    if state["parsing_result"].get("nouns_parsed", 0) > 0 and state["parsing_result"].get("nouns_validated", 0) == 0:
        diagnosis_parts.append("Nouns parsed but validation failed (words not found in text)")
        recommendations.append("Check text preprocessing and word matching logic")

    # Success case
    if state["parsing_result"].get("nouns_validated", 0) > 0:
        diagnosis_parts.append("AI noun discovery working correctly")
        recommendations.append("No action needed - system functioning as expected")

    final_diagnosis = "; ".join(diagnosis_parts) if diagnosis_parts else "Unable to determine root cause"

    log_json(LOG, 20, "debug_diagnosis_complete", diagnosis=final_diagnosis, recommendations=recommendations)

    return {**state, "final_diagnosis": final_diagnosis, "recommendations": recommendations}


def create_debug_workflow():
    """Create the LangGraph workflow for debugging noun discovery."""
    workflow = StateGraph(DebugState)

    # Add nodes
    workflow.add_node("check_environment", check_environment)
    workflow.add_node("check_database", check_database)
    workflow.add_node("check_ai_connectivity", check_ai_connectivity)
    workflow.add_node("analyze_text_extraction", analyze_text_extraction)
    workflow.add_node("analyze_prompt_and_response", analyze_prompt_and_response)
    workflow.add_node("analyze_parsing_and_validation", analyze_parsing_and_validation)
    workflow.add_node("generate_diagnosis_and_recommendations", generate_diagnosis_and_recommendations)

    # Define edges
    workflow.add_edge("check_environment", "check_database")
    workflow.add_edge("check_database", "check_ai_connectivity")
    workflow.add_edge("check_ai_connectivity", "analyze_text_extraction")
    workflow.add_edge("analyze_text_extraction", "analyze_prompt_and_response")
    workflow.add_edge("analyze_prompt_and_response", "analyze_parsing_and_validation")
    workflow.add_edge("analyze_parsing_and_validation", "generate_diagnosis_and_recommendations")

    # Set entry point
    workflow.set_entry_point("check_environment")

    return workflow


def run_debug_analysis(book: str = "Genesis") -> DebugState:
    """Run the complete debugging analysis."""
    log_json(LOG, 20, "debug_workflow_start", book=book)

    workflow = create_debug_workflow()
    app = workflow.compile()

    initial_state = DebugState(
        book=book,
        env_status={},
        db_status={},
        ai_status={},
        text_extraction={},
        prompt_analysis={},
        ai_response={},
        parsing_result={},
        validation_result={},
        final_diagnosis="",
        recommendations=[],
    )

    # Run the workflow
    final_state = app.invoke(initial_state)

    log_json(LOG, 20, "debug_workflow_complete", diagnosis=final_state["final_diagnosis"])

    return final_state


if __name__ == "__main__":
    import sys

    book = sys.argv[1] if len(sys.argv) > 1 else "Genesis"

    print(f"🔍 Debugging AI noun discovery for book: {book}")
    print("=" * 60)

    result = run_debug_analysis(book)

    print("\n📊 DEBUG RESULTS:")
    print("=" * 60)
    print(f"Book: {result['book']}")
    print(f"Final Diagnosis: {result['final_diagnosis']}")

    print("\n🔧 RECOMMENDATIONS:")
    for i, rec in enumerate(result["recommendations"], 1):
        print(f"{i}. {rec}")

    print("\n📋 DETAILED STATE:")
    print("=" * 60)

    # Print key sections
    sections = [
        ("Environment Status", "env_status"),
        ("Database Status", "db_status"),
        ("AI Status", "ai_status"),
        ("Text Extraction", "text_extraction"),
        ("Prompt Analysis", "prompt_analysis"),
        ("Parsing Result", "parsing_result"),
    ]

    for title, key in sections:
        if result.get(key):
            print(f"\n{title}:")
            print(json.dumps(result[key], indent=2, ensure_ascii=False))
