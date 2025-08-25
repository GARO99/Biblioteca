from enum import Enum


class LoanStatus(str, Enum):
    OPEN = "OPEN"
    RETURNED = "RETURNED"
    LATE = "LATE"
    LOST = "LOST"