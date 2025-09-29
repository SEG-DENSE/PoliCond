# prompt template used in first submission
from ontology.condition.condition import Condition
from ontology.data.Data import Data


def prompt_template() -> str:
    return """According to the context below, summarize the data collection behavior and respond using the tuple format.
We will provide candidate entity, data, and conditions.
These entity, data, and conditions are extracted from the context.
Your answers should be based on the candidates and context, and you should follow rules.

# Rules
- Tuple: Your output is like: (entity; verb; data type; condition)
- Every tuple should be in a new line, and only tuple conditions can be composite, others should be a specific value.
- entity and data type in candidates are preferred.
- Available verbs:
    {collect, not collect}
- No Conflict: For a given (entity, data type) pair, you can generate at most 1 'collect' tuple and 1 'not collect' tuple. 
They should have different conditions.

- Available conditions:
    no condition
    user action: user consent, user input, specific operation
    third party: third party service, third party sharing
    special audience: children, regional law
    data management: data retention, non-business (like education or research), data security
- Condition combination rules:
    - Except no condition, other conditions can be combined with 'and'.
    - Priority: Among similar conditions, choose the more specific one. For example, data purpose is more specific than data management.
    - Condition relation: no condition is the most general condition, followed by [user action, third party, special audience, data management], others are specific conditions.

- Not a collection case: If the context describes is unrelated with user data collection or negation claim, then output 'not a collection'.    
# Examples
Example 1:
    (we; collect; location; no condition)

Example 2:
    (we; collect; personal_info; user consent)
    (we; not collect; personal_info; children)

Example 3:
    (we; collect; ip address; data security and third party)

Example 4:
    Input: We will update our privacy policy.
    Output: not a collection
"""

def build_query_template(candidate_entities: set[str], candidate_data: set[Data],
                         candidate_conditions: set[Condition], context: str) -> str:
    """Generate the query template for the OpenAI model."""
    entity_str = "{" + ",".join(
        e for e in candidate_entities) + "}" if candidate_entities else "unspecified entity"
    data_str = "{" + ",".join(d.value for d in candidate_data) + "}" if candidate_data else "unspecified data"
    condition_str = "{" + ",".join(
        c.value for c in candidate_conditions) + "}" if candidate_conditions else "no condition"

    return f"""(?,?,?, ?)
    # Candidate entities:
    {entity_str}
    # Candidate data:
    {data_str}
    # Candidate conditions:
    {condition_str}
    # Context:
    {context}"""


# Ablation
def build_query_template_no_candidate_ablation(context: str) -> str:
    """Generate the query template for the OpenAI model."""
    # entity_str = "{" + ",".join(
    #     e.value for e in candidate_entities) + "}" if candidate_entities else "unspecified entity"
    # data_str = "{" + ",".join(d.value for d in candidate_data) + "}" if candidate_data else "unspecified data"
    # condition_str = "{" + ",".join(
    #     c.value for c in candidate_conditions) + "}" if candidate_conditions else "no condition"
    # logger.info("using ablation template, no candidate")
    return f"""(?,?,?, ?)
    no candidate for ablation
    # Context:
    {context}"""

