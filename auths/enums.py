from enum import Enum

class UserRoles(str, Enum):
    EMPLOYEE="employee"
    ADMIN="admin"
    MANAGER="manager"
    DESIGNER="designer"

    @classmethod
    def _missing_(cls, value):
        if isinstance(value, str):
            value = value.lower()
            for member in cls:
                if member.value == value:
                    return value
        return None

class Branches(str, Enum):
    CHENNAI="chennai"
    HYDERABAD="hyderabad"
    BANGALORE="bangalore"

    @classmethod
    def _missing_(cls, value):
        if isinstance(value, str):
            value = value.lower()
            for member in cls:
                if member.value == value:
                    return member
        return None