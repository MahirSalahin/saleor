import graphene
from .mutations import (
    SubmitProductReview,
    UpdateProductReview,
    DeleteProductReview,
    CreateReviewMedia,
    UpdateReviewMedia,
    DeleteReviewMedia,
)
from ...review import models
from .types import Review


class ReviewQueries(graphene.ObjectType):
    getProductReview = graphene.List(
        Review,
        product=graphene.ID(),
        id=graphene.ID(),
        description="Look up review(s) by id and/or product",
    )
    getAllProductReviews = graphene.List(
        Review, description="Look up the list of reviews"
    )

    def resolve_getProductReview(self, info, product=None, id=None):
        if product and id:
            return models.Review.objects.filter(product=product, id=id)
        if product:
            return models.Review.objects.filter(product=product)
        if id:
            return models.Review.objects.filter(id=id)

    def resolve_getAllProductReviews(self, info):
        return models.Review.objects.all()


class ReviewMutations(graphene.ObjectType):
    submitProductReview = SubmitProductReview.Field()
    updateProductReview = UpdateProductReview.Field()
    deleteProductReview = DeleteProductReview.Field()
    createReviewMedia = CreateReviewMedia.Field()
    updateReviewMedia = UpdateReviewMedia.Field()
    deleteReviewMedia = DeleteReviewMedia.Field()
