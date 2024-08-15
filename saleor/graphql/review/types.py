import graphene
import logging
from ...review import models
from ...core.utils import build_absolute_uri
from ..core.types import ModelObjectType
from ..core.scalars import DateTime
from ..core.types import NonNullList
from ..core.fields import JSONString
from ..core.context import get_database_connection_name
from ..core.federation import resolve_federation_references
from ..core.utils import from_global_id_or_error
from ..meta.types import ObjectWithMetadata
from .enums import ReviewMediaType
from ..product.schema import ProductQueries
from ..account.schema import AccountQueries


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

    user = AccountQueries.user
    product = ProductQueries.product
    media_by_id = graphene.Field(
        lambda: ReviewMedia,
        id=graphene.Argument(graphene.ID, description="ID of a review media."),
        description="Get a single review media by ID.",
    )

    media = NonNullList(
        lambda: ReviewMedia,
        description="List of media for the review.",
    )

    class Meta:
        description = "Represents a review of a product"
        interfaces = [graphene.relay.Node]
        model = models.Review

    @staticmethod
    def resolve_user(root: ModelObjectType[models.Review], info):
        return AccountQueries.resolve_user(
            root, info, id=graphene.Node.to_global_id("User", root.user)
        )

    @staticmethod
    def resolve_product(root: ModelObjectType[models.Review], info):
        return ProductQueries.resolve_product(
            root, info, id=graphene.Node.to_global_id("Product", root.product)
        )

    @staticmethod
    def resolve_media(root: ModelObjectType[models.Review], info):
        return root.media.all()

    @staticmethod
    def resolve_media_by_id(root: ModelObjectType[models.Review], info, id):
        _type, pk = from_global_id_or_error(id, ReviewMedia)
        return (
            root.media.using(get_database_connection_name(info.context))
            .filter(pk=pk)
            .first()
        )


class ReviewMedia(ModelObjectType[models.ReviewMedia]):
    id = graphene.GlobalID(
        required=True, description="The unique ID of the review media."
    )
    sort_order = graphene.Int(description="The sort order of the media.")
    alt = graphene.String(required=True, description="The alt text of the media.")
    type = ReviewMediaType(required=True, description="The type of the media.")
    oembed_data = JSONString(required=True, description="The oEmbed data of the media.")
    url = graphene.String(required=True, description="The URL of the media.")
    review_id = graphene.ID(description="Review id the media refers to.")

    class Meta:
        description = "Represents a review media."
        interfaces = [graphene.relay.Node, ObjectWithMetadata]
        model = models.ReviewMedia

    @staticmethod
    def resolve_url(root: models.ReviewMedia, info):
        if root.external_url:
            return root.external_url

        if not root.image:
            return None

        return build_absolute_uri(root.image.url)

    @staticmethod
    def __resolve_references(roots: list["ReviewMedia"], info):
        database_connection_name = get_database_connection_name(info.context)
        return resolve_federation_references(
            ReviewMedia,
            roots,
            models.ReviewMedia.objects.using(database_connection_name),
        )

    @staticmethod
    def resolve_review_id(root: models.ReviewMedia, info):
        return graphene.Node.to_global_id("Review", root.review_id)
