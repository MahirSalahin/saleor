from typing import Optional
from ...review import models
from ..core.context import get_database_connection_name
from ..core.utils import from_global_id_or_error
from ..product.types import Product
from .types import Review


def resolve_getProductReview(
    info, product: Optional[str], id: Optional[str], status: Optional[bool]
):
    filters = {}
    if product:
        _, filters["product"] = from_global_id_or_error(product, Product)
    if id:
        _, filters["id"] = from_global_id_or_error(id, Review)
    if status is not None:
        filters["status"] = status
    if filters:
        return models.Review.objects.using(
            get_database_connection_name(info.context)
        ).filter(**filters)
    return None


def resolve_getProductReviews(info):
    return models.Review.objects.using(get_database_connection_name(info.context)).all()
