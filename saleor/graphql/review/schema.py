import graphene
from .mutations import (
    SubmitProductReview,
    UpdateProductReview,
    DeleteProductReview,
    CreateReviewMedia,
    UpdateReviewMedia,
    DeleteReviewMedia,
)
from ..core import ResolveInfo
from .types import Review
from .resolvers import resolve_getProductReviews, resolve_getProductReview


class ReviewQueries(graphene.ObjectType):
    getProductReview = graphene.List(
        Review,
        product=graphene.Argument(
            graphene.ID, description="Review of the product", required=False
        ),
        id=graphene.Argument(
            graphene.ID, description="ID of the review.", required=False
        ),
        description="Look up review(s) by id and/or product",
        status=graphene.Argument(
            graphene.Boolean,
            description="Status of the review",
        ),
    )
    getProductReviews = graphene.List(Review, description="Look up the list of reviews")

    def resolve_getProductReview(
        _root, info: ResolveInfo, *, product=None, id=None, status=None, **kwargs
    ):
        return resolve_getProductReview(info, product, id, status)

    def resolve_getProductReviews(_root, info: ResolveInfo, **kwargs):
        return resolve_getProductReviews(info)


class ReviewMutations(graphene.ObjectType):
    submitProductReview = SubmitProductReview.Field()
    updateProductReview = UpdateProductReview.Field()
    deleteProductReview = DeleteProductReview.Field()
    createReviewMedia = CreateReviewMedia.Field()
    updateReviewMedia = UpdateReviewMedia.Field()
    deleteReviewMedia = DeleteReviewMedia.Field()
