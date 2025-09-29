from ontology.condition.condition import Condition

class ConditionDTO:
    def __init__(self, condition: Condition, text: str):
        self.condition = condition
        self.text = text

    def __repr__(self):
        return f"ConditionDTO(condition={self.condition}, text='{self.text}')"

    def __str__(self):
        return f"Condition: {self.condition}, Text: '{self.text}'"

    def __hash__(self):
        return hash((self.condition, self.text))

    def __eq__(self, other):
        if not isinstance(other, ConditionDTO):
            return NotImplemented
        return (self.condition, self.text) == (other.condition, other.text)