import graphene
from ....review.models import Review
from ....account.models import User
from ....product.models import Product
from ....permission.enums import ProductPermissions
from ...core.mutations import ModelMutation
from ..types import ReviewType
from ..errors import ReviewError


class UpdateProductReviewInput(graphene.InputObjectType):
    review_id = graphene.ID(required=True, description="ID of the Review to update")

class UpdateProductReview(ModelMutation):

    class Arguments:
        input = UpdateProductReviewInput(
            required=True, description="Fields require to update a review"
        )

    class Meta:
        description = "Change status of existing review."
        model = Review
        object_type = ReviewType
        error_type_class = ReviewError
        error_type_field = "review_errors"

    @classmethod
    def perform_mutation(cls, root, info, **data):
        input_data = data.get("input")

        if input_data is None:
            raise cls.error_type().error_fields_missing()

        # Extract fields from input_data
        product_id = input_data.get("product_id")
        user_id = input_data.get("user_id")
        rating = input_data.get("rating")
        title = input_data.get("title")
        review = input_data.get("review")

        if not all([product_id, user_id, rating, title, review]):
            raise cls.error_type().error_fields_missing()

        # Fetch related objects
        user = User.objects.get(pk=user_id)
        product = Product.objects.get(pk=product_id)

        # Create and save the review
        review_instance = Review(
            user=user,
            product=product,
            rating=rating,
            title=title,
            review=review,
        )
        review_instance.save()

        return UpdateProductReview(review=review_instance)

    @classmethod
    def save(cls, info, instance, cleaned_input):
        super().save(info, instance, cleaned_input)
