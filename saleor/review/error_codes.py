from enum import Enum


class ReviewErrorCode(Enum):
    ALREADY_EXISTS = "review_already_exists"
    DUPLICATED_INPUT_ITEM = "duplicated_input_item"
    INVALID = "invalid"
    NOT_FOUND = "review_not_found"
    NOT_OWNER = "not_owner"
    NOT_APPROVED = "not_approved"
    REQUIRED = 'required'
