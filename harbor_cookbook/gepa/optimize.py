"""Discover medical agent architectures with GEPA on MedAgentBench.

GEPA evolves a ``solve()`` function that performs multi-turn FHIR API
interactions to answer clinical EHR questions.  Every evaluation runs as a
Harbor Trial using the ``medagentbench@1.0`` registry dataset (prebuilt
Docker image with FHIR server, official grading).
"""

from pathlib import Path

import gepa.optimize_anything as oa
from gepa.optimize_anything import (
    EngineConfig,
    GEPAConfig,
    ReflectionConfig,
    optimize_anything,
)

from harbor_cookbook.gepa.utils import download_tasks, run_trial, split_tasks

# ---------------------------------------------------------------------------
# Seed agent — mirrors the official MedAgentBench protocol:
#   LLM outputs "GET url", "POST url\n[json]", or "FINISH([...])"
#   Harness parses, executes FHIR calls, feeds observations back.
# ---------------------------------------------------------------------------
SEED = r'''
import json
import requests
import litellm

PROMPT = """You are an expert in using FHIR functions to assist medical professionals. \
You are given a question and a set of possible functions. \
Based on the question, you will need to make one or more function/tool calls to achieve the purpose.

1. If you decide to invoke a GET function, you MUST put it in the format of
GET url?param_name1=param_value1&param_name2=param_value2...

2. If you decide to invoke a POST function, you MUST put it in the format of
POST url
[your payload data in JSON format]

3. If you have got answers for all the questions and finished all the requested tasks, \
you MUST call to finish the conversation in the format of \
(make sure the list is JSON loadable.)
FINISH([answer1, answer2, ...])

Your response must be in the format of one of the three cases, and you can call \
only one function each time. You SHOULD NOT include any other text in the response.

Here is a list of functions in JSON format that you can invoke. \
Note that you should use {api_base} as the api_base.
{functions}

Context: {context}
Question: {question}"""

MAX_ROUNDS = 8
ACK = ("POST request accepted and executed successfully. "
       "Please call FINISH if you have got answers for all the questions "
       "and finished all the requested tasks")


def solve(question, context, fhir_base, functions):
    history = [{"role": "user", "content": PROMPT.format(
        api_base=fhir_base, functions=functions,
        context=context or "(none)", question=question,
    )}]

    for _ in range(MAX_ROUNDS):
        resp = litellm.completion(
            model="openai/gpt-5-mini",
            messages=history,
        )
        reply = resp.choices[0].message.content.strip()
        reply = reply.replace("```tool_code", "").replace("```", "").strip()
        history.append({"role": "assistant", "content": reply})
        print(f"Agent: {reply[:200]}", flush=True)

        if reply.startswith("FINISH("):
            result = json.loads(reply[len("FINISH("):-1])
            return result, history

        if reply.startswith("GET"):
            url = reply[3:].strip()
            if "&_format=json" not in url and "?_format=json" not in url:
                url += "&_format=json" if "?" in url else "?_format=json"
            try:
                r = requests.get(url, timeout=30)
                r.raise_for_status()
                data = r.json()
            except Exception as e:
                data = {"error": str(e)}
            obs = f"Here is the response from the GET request:\n{json.dumps(data)}"
            print(f"GET {url} -> {str(data)[:200]}", flush=True)

        elif reply.startswith("POST"):
            lines = reply.split("\n", 1)
            url = lines[0][4:].strip()
            try:
                payload = json.loads(lines[1]) if len(lines) > 1 else {}
                r = requests.post(url, json=payload, timeout=30)
            except Exception:
                pass
            obs = ACK
            print(f"POST {url}", flush=True)

        else:
            obs = "Invalid action. Use GET, POST, or FINISH."

        history.append({"role": "user", "content": obs})

    return [], history
'''.strip()

OBJECTIVE = (
    "Optimize a solve(question, context, fhir_base, functions) function that "
    "answers clinical EHR questions by interacting with a FHIR server. "
    "The function uses litellm.completion() for LLM calls and requests for "
    "FHIR HTTP calls. It returns (result_list, history). "
    "Graded by the official MedAgentBench verifier (binary: 1=correct, 0=wrong)."
)

BACKGROUND = (
    "MedAgentBench tasks span 10 categories: patient lookup, lab results, "
    "vitals, medications, conditions, procedures, service requests, and "
    "clinical reasoning. The FHIR server holds synthetic patient records.\n\n"
    "The seed follows the official MedAgentBench protocol: the LLM outputs "
    "'GET url', 'POST url\\n[json]', or 'FINISH([answers])'. The harness "
    "executes FHIR calls and feeds observations back as chat history.\n\n"
)


def evaluate(candidate, example):
    """GEPA evaluator: run candidate in a Harbor trial for one task."""
    task_id = example.id.name
    result = run_trial(candidate, example.downloaded_path)
    score = result["reward"]

    # Compact summary for oa.log (aggregated across minibatch)
    summary = f"[{task_id}] reward={score}"
    if result["error"]:
        summary += f" error={result['error']}"
    elif result["verifier_output"]:
        summary += f" verifier={result['verifier_output']}"
    oa.log(summary)

    # Detailed trajectory goes in side_info dict — GEPA selects per-example
    # and only shows the reflection minibatch, so this stays manageable.
    return score, {
        "task_id": task_id,
        "Verifier": result["verifier_output"],
        "Agent Trajectory": result["agent_output"],
        "Error": result["error"] or "",
    }


def main():
    items = download_tasks()
    train, val = split_tasks(items)

    result = optimize_anything(
        seed_candidate=SEED,
        evaluator=evaluate,
        dataset=train,
        valset=val,
        objective=OBJECTIVE,
        background=BACKGROUND,
        config=GEPAConfig(
            engine=EngineConfig(
                max_metric_calls=100,
                max_workers=4,
                run_dir="outputs/medagentbench",
            ),
            reflection=ReflectionConfig(
                reflection_lm="openai/gpt-5.4",
            ),
        ),
    )

    out_dir = Path("outputs/medagentbench")
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "best_agent.py").write_text(result.best_candidate)

    best_score = result.val_aggregate_scores[result.best_idx]
    print(f"\nBest val score: {best_score:.3f}")
    print(f"Best agent written to {out_dir / 'best_agent.py'}")


if __name__ == "__main__":
    main()
