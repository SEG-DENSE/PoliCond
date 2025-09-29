# Prompt

```python
system_prompt = "Help me review statements from a privacy policy."
"Classify the statement as one of the following categories: "
"A) Child protection"
"B) Irrelevant with child protection or data collection"
"Just respond with the letter of the category that best fits the statement."
```

```python
def build_user_prompt(statement: str) -> str:
    return f"Statement from a privacy policy:\n {statement}"
```

# Arguments
temperature=0.3
max_tokens=10
model=DeepSeek-V3
