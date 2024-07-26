from ..core.enums import to_enum
from ...review import ReviewMediaTypes
from ..core.doc_category import DOC_CATEGORY_PRODUCTS

ReviewMediaType = to_enum(ReviewMediaTypes, type_name="ReviewMediaType")
ReviewMediaType.doc_category = DOC_CATEGORY_PRODUCTS
