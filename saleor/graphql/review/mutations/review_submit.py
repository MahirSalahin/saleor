import graphene
from django.core.exceptions import ValidationError

from ....account.models import User
from ....product.models import Product
from ....review import models
from ....review.error_codes import ReviewErrorCode
from ...core.mutations import ModelMutation
from ...core.types import ReviewError
from ...core import ResolveInfo
from ...core.utils import from_global_id_or_error
from ...plugins.dataloaders import get_plugin_manager_promise
from ..types import Review


class SubmitProductReviewInput(graphene.InputObjectType):
    product = graphene.ID(required=True, description="Id of the Reviewed Product")
    user = graphene.ID(
        required=True, description="Id of the user who submitted the review"
    )
    rating = graphene.Int(required=True, description="Rating of the product")
    title = graphene.String(required=True, description="Title of the Review")
    review = graphene.String(required=True, description="Description of the review")
    status = graphene.Boolean(required=False, description="Status of the review")
    helpful = graphene.Int(required=False, description="Number of people found this review helpful")


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
        _, product = from_global_id_or_error(data["product"])
        _, user = from_global_id_or_error(data["user"])
        if not Product.objects.filter(pk=product).exists():
            validation_errors["product"] = ValidationError(
                "Product not found.",
                code=ReviewErrorCode.NOT_FOUND.value,
            )
        if not User.objects.filter(pk=user).exists():
            validation_errors["user"] = ValidationError(
                "User not found.",
                code=ReviewErrorCode.NOT_FOUND.value,
            )
        if models.Review.objects.filter(product=product, user=user).exists():
            validation_errors["input"] = ValidationError(
                "You have already reviewed this product.",
                code=ReviewErrorCode.ALREADY_EXISTS.value,
            )
        if validation_errors:
            raise ValidationError(validation_errors)

        data["product"] = product
        data["user"] = user
        return data

    @classmethod
    def perform_mutation(cls, _root, info: ResolveInfo, /, **data):
        data = data["input"]
        instance = cls.get_instance(info, **data)
        cleaned_input = cls.clean_input(info, instance, data)

        instance = cls.construct_instance(instance, cleaned_input)
        cls.clean_instance(info, instance)
        cls.save(info, instance, cleaned_input)

        manager = get_plugin_manager_promise(info.context).get()
        cls.call_event(manager.review_created, instance)

        return cls.success_response(instance)
