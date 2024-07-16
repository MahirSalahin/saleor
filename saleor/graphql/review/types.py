import graphene
from graphene_django.types import DjangoObjectType
from ...review.models import Review
from ..core.types import ModelObjectType
from ..core.scalars import DateTime


class ReviewType(ModelObjectType[Review]):
    id = graphene.GlobalID(required=True, description="ID of the review.")
    rating = graphene.Int(required=True, description="Rating of the review")
    review = graphene.String(required=True, description="Details of the review")
    title = graphene.String(required=True, description="Title of the review")
    created_at = DateTime(
        required=True, description="Date and time at which payment was created."
    )
    updated_at = DateTime(
        required=True, description="Date and time at which payment was updated."
    )
    status = graphene.Boolean(
        required=True, description="Determines if the review is approved or not"
    )
    helpful = graphene.Int(
        required=True, description="Number of times the review is voted as helpful"
    )

    user = graphene.Field(
        "saleor.graphql.account.types.User",
        required=True,
        description="ID of the user who created the review.",
    )

    class Meta:
        description = "Represents a review of a product"
        interfaces = [graphene.relay.Node]
        model = Review

    @staticmethod
    def resolve_rating(root, info):
        return root.rating

    @staticmethod
    def resolve_review(root, info):
        return root.review

    @staticmethod
    def resolve_title(root, info):
        return root.title

    @staticmethod
    def resolve_created_at(root, info):
        return root.created_at

    @staticmethod
    def resolve_updated_at(root, info):
        return root.updated_at

    @staticmethod
    def resolve_status(root, info):
        return root.status

    @staticmethod
    def resolve_helpful(root, info):
        return root.helpful

    @staticmethod
    def resolve_user(root, info):
        return root.user
