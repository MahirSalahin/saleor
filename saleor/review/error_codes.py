from enum import Enum


class ReviewErrorCode(Enum):
    ALREADY_EXISTS = "review_already_exists"
    DUPLICATED_INPUT_ITEM = "duplicated_input_item"
    INVALID = "invalid"
    NOT_FOUND = "not_found"
    NOT_OWNER = "not_owner"
    NOT_APPROVED = "not_approved"
    REQUIRED = "required"
    UNSUPPORTED_MEDIA_PROVIDER = "unsupported_media_provider"
