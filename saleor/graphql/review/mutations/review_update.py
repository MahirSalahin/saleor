import graphene
from django.core.exceptions import ValidationError
from ....review import models
from ....permission.enums import ProductPermissions
from ....core.exceptions import PermissionDenied
from ...core.mutations import ModelMutation
from ...core.context import disallow_replica_in_context, setup_context_user
from ...core.types import ReviewError
from ..types import Review


class UpdateProductReviewInput(graphene.InputObjectType):
    id = graphene.GlobalID(required=True, description="ID of the Review to update")
    status = graphene.Boolean(description="Whether the review is approved or not")
    isHelpful = graphene.Boolean(description="Whether the review is helpful or not")


class UpdateProductReview(ModelMutation):
    class Arguments:
        input = UpdateProductReviewInput(
            required=True, description="Fields require to update a review"
        )

    class Meta:
        description = "Update existing review."
        model = models.Review
        object_type = Review
        error_type_class = ReviewError
        error_type_field = "review_errors"
        permissions = (ProductPermissions.MANAGE_PRODUCTS,)

    @classmethod
    def perform_mutation(cls, root, info, **data):
        review_id = data["input"]["id"]
        
        try:
            review = models.Review.objects.get(pk=review_id)
        except models.Review.DoesNotExist:
            raise ValidationError({"id": "Review not found."})

        if "status" in data["input"]:
            review.status = data["input"]["status"]

        if "isHelpful" in data["input"]:
            review.helpful += int(data["input"]["isHelpful"])

        review.save()
        return cls.success_response(review)
