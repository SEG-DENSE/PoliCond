from dataclasses import dataclass
try:
    from .condition import Condition
except ImportError:
    # For direct execution
    try:
        from condition import Condition
    except ImportError:
        from ontology.condition.condition import Condition


@dataclass(frozen=True)
class ConditionDTO:
    """
    Data Transfer Object for Condition with matched text
    """
    condition: Condition
    text: str
    
    def __str__(self):
        return f"ConditionDTO(condition={self.condition}, text='{self.text}')"
    
    def __repr__(self):
        return self.__str__()
    
    def __eq__(self, other):
        if isinstance(other, ConditionDTO):
            return self.condition == other.condition and self.text == other.text
        return False
    
    def __hash__(self):
        return hash((self.condition, self.text))
