from typing import Optional
from ...review import models
from ..core.context import get_database_connection_name
from ..core.utils import from_global_id_or_error
from ..product.types import Product
from .types import Review


def resolve_getProductReview(info, product: Optional[str], id: Optional[str]):
    if product and id:
        _, product = from_global_id_or_error(product, Product)
        _, id = from_global_id_or_error(id, Review)
        return models.Review.objects.using(
            get_database_connection_name(info.context)
        ).filter(product=product, id=id)
    elif product:
        _, product = from_global_id_or_error(product, Product)
        return models.Review.objects.using(
            get_database_connection_name(info.context)
        ).filter(product=product)
    elif id:
        _, id = from_global_id_or_error(id, Review)
        return models.Review.objects.using(
            get_database_connection_name(info.context)
        ).filter(id=id)
    return None


def resolve_getProductReviews(info):
    return models.Review.objects.using(get_database_connection_name(info.context)).all()
