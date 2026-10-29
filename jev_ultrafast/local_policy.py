"""Local operation selection, observed target selection, and field text."""

import json
import time

from .local_model import (
    PREFILL_CHUNK_TOKENS,
    begin_decision_group,
    check_prompt_size,
    decision_prefix_cache,
    get_model,
    score_decision,
)
from .model import action_space
from .questions import NEXT_ACTION, TARGET, TEXT_VALUE
from .submit_guard import completion_allowed

MODEL_ID = "mlx-community/Qwen3-4B-Instruct-2507-4bit"


def _score(goal, observation, candidates):
    return score_decision(*get_model(), goal, observation, candidates)


def _select(goal, observation, candidates, records):
    # Rescore winners in the same prompt. Logits from different prompts are not comparable.
    while len(candidates) > 20:
        winners = []
        for offset in range(0, len(candidates), 20):
            result = _score(goal, observation, candidates[offset:offset + 20])
            records.append(result)
            winners.append(result["selected_action"])
        candidates = winners
    result = _score(goal, observation, candidates)
    records.append(result)
    return result


def local_choose(state, goal, history, required_fields=None):
    started = time.perf_counter()
    begin_decision_group()
    elements, targets, controls = action_space(state["actions"])
    labels = {
        "CLICK": "Click an observed element, button, suggestion, or calendar day.",
        "TYPE_TEXT": "Enter text in an editable field. The text model supplies the value from the goal.",
        "SELECT": "Select an observed dropdown option.",
    }
    operations = {key: labels[key] for key in targets}
    operations.update({key: value["label"] for key, value in controls.items()})
    operations.update(BLOCKED="No supported operation can progress.")
    if completion_allowed(state["actions"], required_fields or []):
        operations["DONE"] = "All requirements are visibly satisfied."
    request = {
        "page": {k: state[k][:3000] if k == "text" else state[k] for k in ("url", "title", "text")},
        "elements": elements,
        "recent_actions": [
            {k: h.get(k) for k in ("action", "kind", "text", "page_changed")} for h in history[-10:]
        ],
    }
    lines = [f"Title: {state['title']}", f"URL: {state['url']}", "Current observed elements:"]
    for element in elements:
        properties = {k: v for k, v in element.items() if k not in {"index", "label"}}
        if "options" in properties:
            properties["current_selection"] = properties.pop("value")
            properties["available_changes"] = [
                {"index": option["index"], "replace_current_selection_with": option["value"]}
                for option in properties.pop("options")
            ]
        lines.append(f"[{element['index']}] {element['label']} {json.dumps(properties, ensure_ascii=False)}")
    lines.extend(["Visible page text:", request["page"]["text"],
                  "Recent executed actions:", json.dumps(request["recent_actions"], ensure_ascii=False)])
    observation = "\n".join(lines)
    instruction = goal + "\nDecision rules:\n" + NEXT_ACTION
    records = []
    if len(operations) + sum(len(group) for group in targets.values()) <= 26:
        candidates = []
        for operation, group in targets.items():
            for index, action in group.items():
                description = action["label"]
                value = action.get("current_value", action.get("value", ""))
                if operation == "SELECT":
                    description = f"{description.split(' → ')[0]}: {value!r} -> {action['value']!r}"
                elif operation == "TYPE_TEXT" or "empty" in action:
                    description += f" (current value: {value!r})" if value else " (empty)"
                details = {k: action[k] for k in ("context", "empty", "required", "placeholder") if k in action}
                if details:
                    description += " " + json.dumps(details, ensure_ascii=False)
                candidates.append({"id": action["id"], "operation": operation,
                                   "target": index, "description": description})
        candidates.extend({"id": controls[op]["id"] if op in controls else op,
                           "operation": op, "target": "", "description": description}
                          for op, description in operations.items() if op not in targets)
        answer = _score(instruction, observation, candidates)
        selected = answer["selected_action"]
        operation, target, choice = selected["operation"], selected["target"], selected["id"]
        operation_scores = {op: sum(answer["scores"][c["id"]] for c in candidates if c["operation"] == op)
                            for op in operations}
        return {
            "choice": choice, "operation": operation, "target": target or None,
            "confidence": answer["scores"][choice], "probabilities": answer["scores"],
            "operation_probabilities": operation_scores, "target_probabilities": {}, "target_confidence": None,
            "raw_answers": {"joint": answer}, "decision_path": "joint", "model": MODEL_ID,
            "usage": {"prompt_tokens": answer["prompt_tokens"], "completion_tokens": 0},
            "latency_ms": round((time.perf_counter() - started) * 1000), "request": request,
        }
    with decision_prefix_cache():
        operation_answer = _select(instruction, observation, [
            {"id": op, "operation": op, "target": "", "description": description}
            for op, description in operations.items()
        ], records)
        operation = operation_answer["selected_action"]["id"]
        target, target_answer = None, None
        if operation in targets:
            candidates = [
                {"id": index, "operation": operation, "target": index, "description": json.dumps({
                    "label": action["label"], "current_value": action.get("current_value", action.get("value", "")),
                    **{k: action[k] for k in ("role", "checked", "selected", "expanded", "context",
                                               "empty", "required", "placeholder") if k in action},
                }, ensure_ascii=False)}
                for index, action in targets[operation].items()
            ]
            target_answer = _select(instruction + "\n" + TARGET, observation, candidates, records)
            target = target_answer["selected_action"]["id"]
            choice = targets[operation][target]["id"]
            probabilities = {a["id"]: target_answer["scores"].get(index, 0.0)
                             for index, a in targets[operation].items()}
        else:
            choice = controls[operation]["id"] if operation in controls else operation
            probabilities = {choice: operation_answer["scores"][operation]}
        return {
            "choice": choice, "operation": operation, "target": target,
            "confidence": operation_answer["scores"][operation], "probabilities": probabilities,
            "operation_probabilities": operation_answer["scores"],
            "target_probabilities": target_answer["scores"] if target_answer else {},
            "target_confidence": target_answer["scores"][target] if target_answer else None,
            "raw_answers": {"operation": operation_answer, "target": target_answer},
            "model": MODEL_ID, "usage": {"prompt_tokens": sum(r["prompt_tokens"] for r in records),
                                         "completion_tokens": 0},
            "latency_ms": round((time.perf_counter() - started) * 1000), "request": request,
        }


def local_field_text(context):
    from mlx_lm import generate
    from mlx_lm.sample_utils import make_sampler

    started = time.perf_counter()
    model, tokenizer, _mx = get_model()
    prompt_tokens, completion_tokens = 0, 0
    for attempt in range(2):
        content = json.dumps(context, ensure_ascii=False)
        if attempt:
            content += '\nReturn only a JSON object with one key, "text", and a nonempty string value.'
        prompt = tokenizer.apply_chat_template(
            [{"role": "system", "content": TEXT_VALUE}, {"role": "user", "content": content}],
            tokenize=False, add_generation_prompt=True, enable_thinking=False,
        )
        prompt_ids = tokenizer.encode(prompt, add_special_tokens=False)
        check_prompt_size(prompt_ids)
        prompt_tokens += len(prompt_ids)
        output = generate(model, tokenizer, prompt=prompt, max_tokens=128, sampler=make_sampler(temp=0),
                          prefill_step_size=PREFILL_CHUNK_TOKENS, verbose=False)
        completion_tokens += len(tokenizer.encode(output, add_special_tokens=False))
        try:
            data = json.loads(output.strip())
            value = data["text"]
            if set(data) != {"text"} or not isinstance(value, str) or not value.strip() or len(value) > 2000:
                raise ValueError()
        except (ValueError, KeyError, TypeError):
            continue
        return value, {
            "model": MODEL_ID, "latency_ms": round((time.perf_counter() - started) * 1000),
            "usage": {"prompt_tokens": prompt_tokens, "completion_tokens": completion_tokens},
        }
    raise ValueError("Text helper returned no valid field value. Nothing typed.")
