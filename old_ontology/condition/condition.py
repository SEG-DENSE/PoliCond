import os
from enum import Enum


class Condition(Enum):
    NO_COND = "no condition"
    THIRD_PARTY = "third party"
    THIRD_PARTY_SERVICE = "third party service"
    SHARING="sharing"
    SPECIAL_AUDIENCE = "special audience"
    CHILDREN = "children"
    REGION = "region"
    MANAGEMENT = "management" # data management
    SECURITY = "security" # data security
    NON_BUSINESS = "non-business"
    RETENTION = "retention" # data retention
    USER_ACTION = "user action"
    CONSENT = "consent"
    INPUT = "input"
    SPECIFIC_OPERATION = "specific operation"

    # help messages
    help_msgs = {
        NO_COND: "no condition/ not mentioned/probably any case",
        THIRD_PARTY: "third party related(e.g. data sharing, third party service)",
        THIRD_PARTY_SERVICE: "third party service(e.g. google analytics, facebook)",
        SHARING: "data sharing(e.g. sharing with third party)",
        SPECIAL_AUDIENCE: "special audience(e.g. children, specific region, jurisdiction)",
        CHILDREN: "children protection",
        REGION: "region/regional law(e.g. GDPR)",
        MANAGEMENT: "data management(e.g. data security, retention, or purpose",
        SECURITY: "data security",
        NON_BUSINESS: "non-business related(e.g. personal use, non-commercial)",
        RETENTION: "data retention",
        USER_ACTION: "user action(e.g. user consent, user input, user specific operation)",
        CONSENT: "user consent/user choice(e.g. opt-in, opt-out)",
        INPUT: "user input(content which can be accessed, edited, deleted)",
        SPECIFIC_OPERATION: "specific user operation(eg. register, login, subscription)"
    }

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