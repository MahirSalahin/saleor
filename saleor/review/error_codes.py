from enum import Enum


class ReviewErrorCode(Enum):
    NOT_FOUND = "review_not_found"
    ALREADY_EXISTS = "review_already_exists"
    INVALID = "invalid"
    NOT_OWNER = "not_owner"
    NOT_APPROVED = "not_approved"
    REQUIRED = 'required'
