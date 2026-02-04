# src/rules/evaluator.py
# 룰 매칭만 담당
def evaluate_rules(entities, rules):
    matched = []

    for rule in rules:
        cond = rule.get("condition", {})

        if "contains" in cond:
            targets = cond["contains"]
            if any(t in entities.get("all", []) for t in targets):
                matched.append(rule)

    return matched
