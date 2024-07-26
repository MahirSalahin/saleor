import graphene
from django.core.exceptions import ValidationError
from ....review import models
from ....review.error_codes import ReviewErrorCode
from ...core.mutations import ModelMutation
from ...core.types import ReviewError
from ...core import ResolveInfo
from ..types import Review


class SubmitProductReviewInput(graphene.InputObjectType):
    product = graphene.ID(required=True, description="Id of the Reviewed Product")
    user = graphene.ID(
        required=True, description="Id of the user who submitted the review"
    )
    rating = graphene.Int(required=True, description="Rating of the product")
    title = graphene.String(required=True, description="Title of the Review")
    review = graphene.String(required=True, description="Description of the review")


class SubmitProductReview(ModelMutation):
    review = graphene.Field(Review)

    class Arguments:
        input = SubmitProductReviewInput(
            required=True, description="Fields require to create and submit a review"
        )

    class Meta:
        description = "Create a new product review."
        model = models.Review
        object_type = Review
        error_type_class = ReviewError
        error_type_field = "review_errors"

    @classmethod
    def clean_input(
        cls, info: ResolveInfo, instance: models.Review, data: dict, **kwargs
    ):
        validation_errors = {}
        for field in ["product", "user", "rating", "title", "review"]:
            if data[field] == "":
                validation_errors[field] = ValidationError(
                    f"{field} cannot be empty.",
                    code=ReviewErrorCode.REQUIRED.value,
                )
        if validation_errors:
            raise ValidationError(validation_errors)
        return data

    @classmethod
    def perform_mutation(cls, _root, info: ResolveInfo, /, **data):
        instance = cls.get_instance(info, **data)
        data = data["input"]
        cleaned_input = cls.clean_input(info, instance, data)
        instance = cls.construct_instance(instance, cleaned_input)
        cls.clean_instance(info, instance)
        cls.save(info, instance, cleaned_input)
        return cls.success_response(instance)
