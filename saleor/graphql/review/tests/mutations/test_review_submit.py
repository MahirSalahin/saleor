import graphene
import pytest

from .....graphql.tests.utils import assert_no_permission, get_graphql_content
from .....review.models import Review
from .....review.error_codes import ReviewErrorCode

SUBMIT_REVIEW_MUTATION = """
    mutation submitReview($input: SubmitProductReviewInput!) {
        submitProductReview(input: $input) {
            review {
                id
                rating
                title
                review
                user
                product
                status
            }
            errors {
                field
                code
            }
        }
    }
"""


def test_submit_review(user_api_client, product):
    # given
    product_id = graphene.Node.to_global_id("Product", product.pk)
    user_id = graphene.Node.to_global_id("User", user_api_client.user.pk)
    title = "Great product!"
    review_text = "I really liked this product"
    rating = 5
    variables = {
        "input": {
            "product": product_id,
            "user": user_id,
            "title": title,
            "review": review_text,
            "rating": rating,
        }
    }

    # when
    response = user_api_client.post_graphql(SUBMIT_REVIEW_MUTATION, variables)

    # then
    content = get_graphql_content(response)
    review = Review.objects.get(product=product.pk, user=user_api_client.user.pk)
    assert (
        int(content["data"]["submitProductReview"]["review"]["product"])
        == review.product
    )
    assert int(content["data"]["submitProductReview"]["review"]["user"]) == review.user
    assert content["data"]["submitProductReview"]["review"]["title"] == review.title
    assert content["data"]["submitProductReview"]["review"]["review"] == review.review
    assert content["data"]["submitProductReview"]["review"]["rating"] == review.rating
    assert not review.status


def test_submit_review_empty_fields(user_api_client, product):
    # given
    product_id = graphene.Node.to_global_id("Product", product.pk)
    user_id = graphene.Node.to_global_id("User", user_api_client.user.pk)
    variables = {
        "input": {
            "product": product_id,
            "user": user_id,
            "title": "",
            "review": "",
            "rating": 4,
        }
    }

    # when
    response = user_api_client.post_graphql(SUBMIT_REVIEW_MUTATION, variables)

    # then
    content = get_graphql_content(response)
    errors = content["data"]["submitProductReview"]["errors"]
    assert errors[0] == {
        "field": "title",
        "code": ReviewErrorCode.REQUIRED.name,
    }
    assert errors[1] == {
        "field": "review",
        "code": ReviewErrorCode.REQUIRED.name,
    }
    assert not Review.objects.filter(
        product=product.pk, user=user_api_client.user.pk
    ).exists()


def test_submit_review_duplicate(user_api_client, product):
    # given
    product_id = graphene.Node.to_global_id("Product", product.pk)
    user_id = graphene.Node.to_global_id("User", user_api_client.user.pk)
    title = "Duplicate Review"
    review_text = "This review should already exist."
    rating = 4
    Review.objects.create(
        product=product.pk,
        user=user_api_client.user.pk,
        title=title,
        review=review_text,
        rating=rating,
    )
    variables = {
        "input": {
            "product": product_id,
            "user": user_id,
            "title": title,
            "review": review_text,
            "rating": rating,
        }
    }

    # when
    response = user_api_client.post_graphql(SUBMIT_REVIEW_MUTATION, variables)

    # then
    content = get_graphql_content(response)
    error = content["data"]["submitProductReview"]["errors"][0]
    assert error["code"] == ReviewErrorCode.ALREADY_EXISTS.name
    assert (
        Review.objects.filter(product=product.pk, user=user_api_client.user.pk).count()
        == 1
    )


def test_submit_review_product_not_found(user_api_client, product):
    # given
    variables = {
        "input": {
            "product": graphene.Node.to_global_id("Product", -1),
            "user": graphene.Node.to_global_id("User", user_api_client.user.pk),
            "title": "Test Review",
            "review": "Test review",
            "rating": 5,
        }
    }
    # when
    response = user_api_client.post_graphql(SUBMIT_REVIEW_MUTATION, variables)
    # then
    content = get_graphql_content(response)
    error = content["data"]["submitProductReview"]["errors"][0]
    assert error["code"] == ReviewErrorCode.NOT_FOUND.name
    assert error["field"] == "product"
    assert not Review.objects.filter(
        product=product.pk, user=user_api_client.user.pk
    ).exists()


def test_submit_review_user_not_found(user_api_client, product):
    # given
    variables = {
        "input": {
            "product": graphene.Node.to_global_id("Product", product.pk),
            "user": graphene.Node.to_global_id("User", -1),
            "title": "Test Review",
            "review": "Test review",
            "rating": 5,
        }
    }
    # when
    response = user_api_client.post_graphql(SUBMIT_REVIEW_MUTATION, variables)
    # then
    content = get_graphql_content(response)
    error = content["data"]["submitProductReview"]["errors"][0]
    assert error["code"] == ReviewErrorCode.NOT_FOUND.name
    assert error["field"] == "user"
    assert not Review.objects.filter(
        product=product.pk, user=user_api_client.user.pk
    ).exists()
