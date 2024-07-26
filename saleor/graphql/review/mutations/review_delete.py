import graphene
from graphql import GraphQLError
from saleor.graphql.core import ResolveInfo
from ....review import models
from ....permission.enums import ProductPermissions
from ....core.exceptions import PermissionDenied
from ...core.mutations import ModelDeleteMutation
from ...core.types.common import ReviewError
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
        permissions = (ProductPermissions.MANAGE_PRODUCTS,)

    @classmethod
    def clean_instance(cls, info, instance):
        if not instance:
            raise GraphQLError("Review not found.")

    @classmethod
    def get_instance(cls, info, **data):
        review_id = data.get("id")
        try:
            instance = models.Review.objects.get(pk=review_id)
        except models.Review.DoesNotExist:
            raise GraphQLError(f"Review with id {review_id} does not exist.")
        return instance

    @classmethod
    def perform_mutation(cls, _root, info, **data):
        instance = cls.get_instance(info, **data)
        cls.clean_instance(info, instance)
        db_id = instance.id
        instance.delete()

        instance.id = db_id
        cls.post_save_action(info, instance, None)
        return cls.success_response(instance)
