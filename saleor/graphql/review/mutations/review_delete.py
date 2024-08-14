import graphene
from saleor.graphql.core import ResolveInfo
from ....review import models
from ...core.mutations import ModelDeleteMutation
from ...core.types.common import ReviewError
from ...plugins.dataloaders import get_plugin_manager_promise
from ..types import Review


class DeleteProductReview(ModelDeleteMutation):
    class Arguments:
        id = graphene.ID(required=True, description="ID of a review to delete")

    class Meta:
        description = "Deletes a product review"
        model = models.Review
        object_type = Review
        error_type_class = ReviewError
        error_type_field = "review_errors"
        # permissions = (ProductPermissions.MANAGE_PRODUCTS,)

    @classmethod
    def perform_mutation(cls, _root, info:ResolveInfo, **data):
        review = cls.get_node_or_error(info, data["id"], only_type=Review)
        review_id = review.id
        review.delete()
        review.id = review_id
        manager = get_plugin_manager_promise(info.context).get()
        cls.call_event(manager.review_deleted, review)
        return DeleteProductReview(review=review)
