"""Optional prototype: runs the extraction prompt on proposal text files YOU place in ./local_proposals/ (git-ignored).
Usage: python extract.py local_proposals/A.txt
Real extraction output would then be saved as facts.json and passed to score.py."""
import json, os, re, sys
from anthropic import Anthropic

MODEL = os.getenv("MODEL", "claude-sonnet-4-6")
here = os.path.dirname(__file__)
read = lambda n: open(os.path.join(here, n)).read()

def build(text, crit):
    user = (read("prompt_extraction_user.txt")
            .replace("{{category_name}}", crit["category"]).replace("{{criteria_version}}", str(crit["version"]))
            .replace("{{budget_ceiling}}", str(crit["budget_ceiling"])).replace("{{max_weeks}}", str(crit["max_weeks"]))
            .replace("{{criteria_field_list}}", ", ".join(crit["mandatory"] + list(crit["weights"])))
            .replace("{{proposal_text}}", text))
    return read("prompt_extraction_system.txt"), user

def check_evidence(result, text):
    """Rule-based guard: every quote must exist verbatim in the source, else the field is rejected."""
    norm = lambda s: re.sub(r"\s+", " ", s).strip().lower()
    src, bad = norm(text), []
    for k, v in result.items():
        if isinstance(v, dict) and v.get("found") and (not v.get("evidence") or norm(v["evidence"]) not in src):
            v["found"], v["value"] = False, None
            bad.append(k)
    return bad

if __name__ == "__main__":
    crit = json.load(open(os.path.join(here, "criteria.json")))
    text = open(sys.argv[1]).read()
    system, user = build(text, crit)
    msg = Anthropic().messages.create(model=MODEL, max_tokens=2000, temperature=0, system=system,
                                      messages=[{"role": "user", "content": user}])
    result = json.loads(msg.content[0].text)
    rejected = check_evidence(result, text)
    print(json.dumps({"result": result, "rejected_for_bad_evidence": rejected}, indent=2))
