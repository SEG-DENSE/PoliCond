from enum import Enum


class Condition(Enum):
    """
    Enumeration of condition types based on the new ontology structure
    """
    ADVERTISING = "advertising"
    ANALYTICS = "analytics"
    CHILDREN = "children"
    CONSENT = "consent"
    DATA_PROTECTION = "data_protection"
    DATA_SHARING = "data_sharing"
    FRAUD_DETECTION = "fraud_detection"
    GOVERNMENT = "government"
    INDUSTRY = "industry"
    INPUT = "input"
    ANY_CONDITION = "any_condition"
    PERSONALIZATION = "personalization"
    PRODUCT_IMPROVEMENT = "product_improvement"
    PROHIBITED_USE = "prohibited_use"
    PURPOSE = "purpose"
    REGION = "region"
    REQUIREMENTS = "requirements"
    RESEARCH = "research"
    RETENTION = "retention"
    SECURITY = "security"
    SERVICE_NECESSITY = "service_necessity"
    SPECIFIC_AUDIENCE = "specific_audience"
    SPECIFIC_OPERATION = "specific_operation"
    THIRD_PARTY_SERVICE = "third_party_service"
    THIRD_PARTY = "third_party"
    USER_ACTION = "user_action"
    NO_COND="any condition"
    def related(self, other) -> bool:
        if isinstance(other, Condition):
            if self <= other or self > other: return True
        return False

    def __hash__(self):
        return hash(self.value)

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.__str__()

    # operator overloading
    # self == other?
    def __eq__(self, other):
        if isinstance(other, Condition):
            return self.name == other.name
        return NotImplemented

    # self != other?
    def __ne__(self, other):
        if isinstance(other, Condition):
            return self.name != other.name
        return NotImplemented

if __name__ == '__main__':
    # allvalues of
    all_values = [c.value for c in Condition]
    print(all_values)
