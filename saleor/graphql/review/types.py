import graphene
from typing import Optional
from ...review import models
from ...core.utils import build_absolute_uri
from ...thumbnail.utils import (
    get_thumbnail_format,
    get_thumbnail_size,
    get_image_or_proxy_url,
)
from ..core.types import ModelObjectType
from ..core.scalars import DateTime
from ..core.types import ThumbnailField, NonNullList
from ..core.fields import JSONString
from ..core.context import get_database_connection_name
from ..core.federation import resolve_federation_references
from ..core.utils import from_global_id_or_error
from ..channel import ChannelContext
from ..meta.types import ObjectWithMetadata
from .enums import ReviewMediaType
from .dataloaders import ThumbnailByReviewMediaIdSizeAndFormatLoader


class Review(ModelObjectType[models.Review]):
    id = graphene.GlobalID(required=True, description="ID of the review.")
    rating = graphene.Int(required=True, description="Rating of the review")
    review = graphene.String(required=True, description="Details of the review")
    title = graphene.String(required=True, description="Title of the review")
    created_at = DateTime(
        required=True, description="Date and time at which review was created."
    )
    updated_at = DateTime(
        required=True, description="Date and time at which review was updated."
    )
    status = graphene.Boolean(
        required=True, description="Determines if the review is approved or not"
    )
    helpful = graphene.Int(
        required=True, description="Number of times the review is voted as helpful"
    )

    user = graphene.ID(
        required=True, description="ID of the user who created the review."
    )
    product = graphene.ID(required=True, description="ID of the reviewed product.")

    media_by_id = graphene.Field(
        lambda: ReviewMedia,
        id=graphene.Argument(graphene.ID, description="ID of a review media."),
        description="Get a single review media by ID.",
    )
    # image_by_id = graphene.Field(
    #     lambda: ProductImage,
    #     id=graphene.Argument(graphene.ID, description="ID of a product image."),
    #     description="Get a single product image by ID.",
    #     deprecation_reason=(
    #         f"{DEPRECATED_IN_3X_FIELD} Use the `mediaById` field instead."
    #     ),
    # )
    # media = NonNullList(
    #     lambda: ReviewMedia,
    #     # sort_by=graphene.Argument(
    #     #     MediaSortingInput, description=f"Sort media. {ADDED_IN_39}"
    #     # ),
    #     description="List of media for the review.",
    # )

    @staticmethod
    def resolve_media_by_id(root: ChannelContext[models.Review], info, *, id):
        _type, pk = from_global_id_or_error(id, ReviewMedia)
        return (
            root.node.media.using(get_database_connection_name(info.context))
            .filter(pk=pk)
            .first()
        )

    class Meta:
        description = "Represents a review of a product"
        interfaces = [graphene.relay.Node]
        model = models.Review


class ReviewMedia(ModelObjectType[models.ReviewMedia]):
    id = graphene.GlobalID(
        required=True, description="The unique ID of the review media."
    )
    sort_order = graphene.Int(description="The sort order of the media.")
    alt = graphene.String(required=True, description="The alt text of the media.")
    type = ReviewMediaType(required=True, description="The type of the media.")
    oembed_data = JSONString(required=True, description="The oEmbed data of the media.")
    url = ThumbnailField(
        graphene.String, required=True, description="The URL of the media."
    )
    review_id = graphene.ID(description="Review id the media refers to.")

    class Meta:
        description = "Represents a review media."
        interfaces = [graphene.relay.Node, ObjectWithMetadata]
        model = models.ReviewMedia

    @staticmethod
    def resolve_url(
        root: models.ReviewMedia,
        info,
        *,
        size: Optional[int] = None,
        format: Optional[str] = None,
    ):
        if root.external_url:
            return root.external_url

        if not root.image:
            return

        if size == 0:
            return build_absolute_uri(root.image.url)

        format = get_thumbnail_format(format)
        selected_size = get_thumbnail_size(size)

        def _resolve_url(thumbnail):
            url = get_image_or_proxy_url(
                thumbnail, str(root.id), "ReviewMedia", selected_size, format
            )
            return build_absolute_uri(url)

        return (
            ThumbnailByReviewMediaIdSizeAndFormatLoader(info.context)
            .load((root.id, selected_size, format))
            .then(_resolve_url)
        )

    @staticmethod
    def __resolve_references(roots: list["ReviewMedia"], info):
        database_connection_name = get_database_connection_name(info.context)
        return resolve_federation_references(
            ReviewMedia,
            roots,
            models.ReviewMedia.objects.using(database_connection_name),
        )

    @staticmethod
    def resolve_product_id(root: models.ReviewMedia, info):
        return graphene.Node.to_global_id("Review", root.review_id)
