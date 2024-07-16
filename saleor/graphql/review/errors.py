import graphene
from ..core.types import Error
from ..core.enums import ReviewErrorCode

class ReviewError(Error):
    code = ReviewErrorCode(description="The error code", required=True)
    
