import graphene
from .mutations.review_submit import SubmitProductReview
from ...review.models import Review
from .types import ReviewType


class ReviewQueries(graphene.ObjectType):
    getProductReview = graphene.List(ReviewType, product_id=graphene.ID(required=True))
    getAllProductReviews = graphene.List(ReviewType)

    def resolve_getProductReview(self, info, product_id):
        return Review.objects.filter(product_id=product_id)

    def resolve_getAllProductReviews(self, info):
        return Review.objects.all()


class ReviewMutations(graphene.ObjectType):
    submitProductReview = SubmitProductReview.Field()
