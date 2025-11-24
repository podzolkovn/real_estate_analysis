from enum import Enum


class SortOrderEnum(str, Enum):
    ASC = "ASC"
    DESC = "DESC"


class StatusSearchEnum(str, Enum):
    PENDING = "PENDING"
    STARTED = "STARTED"
    COMPLETED = "COMPLETED"
    ERROR = "ERROR"
    NO_DATA = "NO_DATA"


class CurrencyEnum(str, Enum):
    USD = "USD"
    EUR = "EUR"
    KZT = "KZT"


class CurrencyOnlineKompasEnum(int, Enum):
    USD = 2
    EUR = 3
    KZT = 1
