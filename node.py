from typing import Union

from ontology.condition.condition import Condition


class CollectionNode:
    def __init__(self, entity: str, verb: str, data: str, condition: Union[Condition,str], text: str = None, **kwargs):
        self.entity = entity
        self.verb = verb
        self.data = data
        self.condition = condition
        # The text.txt attribute is optional and can be used to store explanation information.
        self.text = text
        self.extra = kwargs

    def __str__(self):
        """Return a string representation of the node."""
        condition_str =  self.condition.name if isinstance(self.condition, Condition) else self.condition
        text_str = f", {self.text}" if self.text else ""
        return f"({self.entity}, {self.verb}, {self.data}, {condition_str}{text_str})"

    def __repr__(self):
        """Return a string representation of the node."""
        condition_str =  self.condition.name if isinstance(self.condition, Condition) else self.condition
        return f"({self.entity}, {self.verb}, {self.data}, {condition_str})"

    def pretty_print(self):
        """Return a string representation of the node."""
        condition_str =  self.condition.name if isinstance(self.condition, Condition) else self.condition
        text_str = f", {self.text}" if self.text else ""
        return f"({self.entity}, {self.verb}, {self.data}, {condition_str}{text_str})"

    def __hash__(self):
        """Generate a hash based on the unique attributes of the node."""
        if isinstance(self.condition, Condition):
            return hash((self.entity, self.verb, self.data, self.condition.name, self.text))
        else:
            return hash((self.entity, self.verb, self.data, self.condition, self.text))

    def __eq__(self, other):
        """Define equality between two CollectionBehaviorNode instances."""
        if isinstance(other, CollectionNode):
            return (self.entity == other.entity and
                    self.verb == other.verb and
                    self.data == other.data and
                    self.condition == other.condition and
                    self.text == other.text)
        return False

    def __dict__(self):
        obj = {
            'entity': self.entity,
            'verb': self.verb,
            'data': self.data,
            'condition': self.condition.name if isinstance(self.condition, Condition) else self.condition,
        }

        if self.text:
            obj['text.txt'] = self.text

        if self.extra:
            component_set = self.extra.get('component', set())
            level2_set = self.extra.get('level2', set())

            if component_set:
                obj['component'] = ','.join(map(str, component_set))

            if level2_set:
                tmp: list[Condition] = []
                for key in level2_set:
                    tmp.append(key.name)
                obj['level2'] = ','.join(tmp)

        return obj

    def to_dict(self):
        text_str = f"{self.text}" if self.text else ""
        return {
            'entity': self.entity,
            'verb': self.verb,
            'data': self.data,
            'condition': self.condition.name if isinstance(self.condition, Condition) else self.condition,
        }


class CollectionNodeWithContext(CollectionNode):
    def __init__(self, entity: str, verb: str, data: str, condition: Union[Condition,str],
                 candidateEntity: str,  candidateVerb: str,candidateData: str, candidateCondition: str,
                 sentence:str, context:str,
                 text: str = None, **kwargs):
        super().__init__(entity, verb, data, condition, text, **kwargs)
        self.candidateEntity = candidateEntity
        self.candidateVerb = candidateVerb
        self.candidateData = candidateData
        self.candidateCondition = candidateCondition
        self.sentence = sentence
        self.context = context

    def __str__(self):
        """Return a string representation of the node."""
        condition_str =  self.condition.name if isinstance(self.condition, Condition) else self.condition
        text_str = f", {self.text}" if self.text else ""
        return f"({self.entity}, {self.verb}, {self.data}, {condition_str}{text_str})"

    def __repr__(self):
        """Return a string representation of the node."""
        condition_str =  self.condition.name if isinstance(self.condition, Condition) else self.condition
        return f"({self.entity}, {self.verb}, {self.data}, {condition_str})"

    def pretty_print(self):
        """Return a string representation of the node."""
        condition_str =  self.condition.name if isinstance(self.condition, Condition) else self.condition
        text_str = f", {self.text}" if self.text else ""
        return f"({self.entity}, {self.verb}, {self.data}, {condition_str}{text_str})"

    def __hash__(self):
        """Generate a hash based on the unique attributes of the node."""
        if isinstance(self.condition, Condition):
            return hash((self.entity, self.verb, self.data, self.condition.name, self.text))
        else:
            return hash((self.entity, self.verb, self.data, self.condition, self.text))

    def __eq__(self, other):
        """Define equality between two CollectionBehaviorNode instances."""
        if isinstance(other, CollectionNode):
            return (self.entity == other.entity and
                    self.verb == other.verb and
                    self.data == other.data and
                    self.condition == other.condition and
                    self.text == other.text)
        return False

    def __dict__(self):
        obj = {
            'entity': self.entity,
            'verb': self.verb,
            'data': self.data,
            'condition': self.condition.name if isinstance(self.condition, Condition) else self.condition,
        }

        if self.text:
            obj['text.txt'] = self.text

        if self.extra:
            component_set = self.extra.get('component', set())
            level2_set = self.extra.get('level2', set())

            if component_set:
                obj['component'] = ','.join(map(str, component_set))

            if level2_set:
                tmp: list[Condition] = []
                for key in level2_set:
                    tmp.append(key.name)
                obj['level2'] = ','.join(tmp)

        return obj

    def to_dict(self):
        text_str = f"{self.text}" if self.text else ""
        return {
            'entity': self.entity,
            'verb': self.verb,
            'data': self.data,
            'condition': self.condition.name if isinstance(self.condition, Condition) else self.condition,
        }
