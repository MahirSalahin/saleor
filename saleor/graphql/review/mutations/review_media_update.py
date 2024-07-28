import graphene
from django.core.exceptions import ValidationError

from ....permission.enums import ProductPermissions
from ....review import models
from ....review.error_codes import ReviewErrorCode
from ...core import ResolveInfo
from ...core.doc_category import DOC_CATEGORY_PRODUCTS
from ...core.mutations import BaseMutation
from ...core.types import BaseInputObjectType, ReviewError
from ...plugins.dataloaders import get_plugin_manager_promise
from ..types import Review, ReviewMedia

ALT_CHAR_LIMIT = 250


class UpdateReviewMediaInput(BaseInputObjectType):
    alt = graphene.String(description="Alt text for a review media.")

    class Meta:
        doc_category = DOC_CATEGORY_PRODUCTS


class UpdateReviewMedia(BaseMutation):
    review = graphene.Field(Review)
    media = graphene.Field(ReviewMedia)

    class Arguments:
        id = graphene.ID(required=True, description="ID of a review media to update.")
        input = UpdateReviewMediaInput(
            required=True, description="Fields required to update a review media."
        )

    class Meta:
        description = "Updates a review media."
        doc_category = DOC_CATEGORY_PRODUCTS
        # permissions = (ProductPermissions.MANAGE_PRODUCTS,)
        error_type_class = ReviewError
        error_type_field = "review_errors"

    @classmethod
    def perform_mutation(  # type: ignore[override]
        cls, _root, info: ResolveInfo, /, *, id, input
    ):
        media = cls.get_node_or_error(info, id, only_type=ReviewMedia)
        review = models.Review.objects.get(pk=media.review_id)
        alt = input.get("alt")
        if alt is not None:
            if len(alt) > ALT_CHAR_LIMIT:
                raise ValidationError(
                    {
                        "input": ValidationError(
                            f"Alt field exceeds the character "
                            f"limit of {ALT_CHAR_LIMIT}.",
                            code=ReviewErrorCode.INVALID.value,
                        )
                    }
                )
            media.alt = alt
            media.save(update_fields=["alt"])
        manager = get_plugin_manager_promise(info.context).get()
        cls.call_event(manager.review_updated, review)
        cls.call_event(manager.review_media_updated, media)
        return UpdateReviewMedia(review=review, media=media)
