# matacs-th-2026-02

- **Name:** RABIA REHMAN 
- **Reference:** MATACS-TH-2026-02
- **Time actually spent:** I took 40 minutes in this task.

## Files
- [WRITEUP.md](WRITEUP.md): answers to the five questions
- [diagram/process_flow.png](diagram/process_flow.png): process flow (AI, rule-based and human steps)
- [PROMPTS.md](PROMPTS.md): extraction and injection-screen prompts
- [ranking.json](ranking.json): expected ranking of proposals A to E
- [prototype/](prototype/): optional scripts. `score.py` is the deterministic scorer and reproduces `ranking.json` from `facts.json` and `criteria.json`. `extract.py` runs the extraction prompt on text files you supply locally. Use `.env.example`; no keys are committed.

## How I used AI tools
I used Claude and Chatgpt to help draft the process design, the write-up, the prompts, the flow diagram and a small scoring prototype. I reviewed each file, checked the scoring numbers by running `score.py`, and edited the parts I disagreed with.

**Where I disagreed with / corrected the AI:** AI originally ranked Proposal D third and gave it zero for timeline. I disagreed because the brief requires completion within 16 weeks and D states no schedule, so a ranked position implies something we cannot confirm. I changed D to "flagged" so a person can ask the bidder, and I updated `score.py`, `ranking.json` and the write-up to match.
