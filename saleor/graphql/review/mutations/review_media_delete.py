import graphene

from ....permission.enums import ProductPermissions
from ....review import models
from ...core import ResolveInfo
from ...core.doc_category import DOC_CATEGORY_PRODUCTS
from ...core.mutations import BaseMutation
from ...core.types import ReviewError
from ...plugins.dataloaders import get_plugin_manager_promise
from ..types import Review, ReviewMedia


class DeleteReviewMedia(BaseMutation):
    review = graphene.Field(Review)
    media = graphene.Field(ReviewMedia)

    class Arguments:
        id = graphene.ID(required=True, description="ID of a review media to delete.")

    class Meta:
        description = "Deletes a review media."
        doc_category = DOC_CATEGORY_PRODUCTS
        # permissions = (ProductPermissions.MANAGE_PRODUCTS,)
        error_type_class = ReviewError
        error_type_field = "review_errors"

    @classmethod
    def perform_mutation(  # type: ignore[override]
        cls, _root, info: ResolveInfo, /, *, id: str
    ):
        media_obj = cls.get_node_or_error(info, id, only_type=ReviewMedia)
        review = models.Review.objects.get(pk=media_obj.review_id)  # type: ignore
        media_id = media_obj.id
        media_obj.delete()
        media_obj.id = media_id
        manager = get_plugin_manager_promise(info.context).get()
        cls.call_event(manager.review_updated, review)
        cls.call_event(manager.review_media_deleted, media_obj)
        return DeleteReviewMedia(review=review, media=media_obj)
