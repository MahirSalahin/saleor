import graphene
import pytest
import logging

from .....graphql.tests.utils import get_graphql_content
from .....review.models import Review


logger = logging.getLogger(__name__)

QUERY_GET_PRODUCT_REVIEW = """
    query getProductReview($product: ID, $id: ID) {
        getProductReview(product: $product, id: $id) {
            id
            rating
            title
            review
            status
            helpful
            product
            user
            media{
                id
                url
            }
        }
    }
"""


def test_get_product_review_by_product_id(staff_api_client, review_with_image):
    # given
    variables = {
        "product": graphene.Node.to_global_id("Product", review_with_image.product)
    }

    # when
    response = staff_api_client.post_graphql(QUERY_GET_PRODUCT_REVIEW, variables)
    content = get_graphql_content(response)

    # then
    data = content["data"]["getProductReview"]
    assert len(data) == 1
    assert data[0]["rating"] == review_with_image.rating
    assert data[0]["title"] == review_with_image.title
    assert data[0]["review"] == review_with_image.review
    assert data[0]["status"] == review_with_image.status
    assert data[0]["helpful"] == review_with_image.helpful
    assert data[0]["user"] == str(review_with_image.user)
    assert data[0]["product"] == str(review_with_image.product)
    assert len(data[0]["media"]) == 1
    assert data[0]["media"][0]["id"]
    assert data[0]["media"][0]["url"]


def test_get_product_review_by_review_id(staff_api_client, review_with_image):
    # given
    variables = {"id": graphene.Node.to_global_id("Review", review_with_image.id)}

    # when
    response = staff_api_client.post_graphql(QUERY_GET_PRODUCT_REVIEW, variables)
    content = get_graphql_content(response)

    # then
    data = content["data"]["getProductReview"]
    assert len(data) == 1
    assert data[0]["rating"] == review_with_image.rating
    assert data[0]["title"] == review_with_image.title
    assert data[0]["review"] == review_with_image.review
    assert data[0]["status"] == review_with_image.status
    assert data[0]["helpful"] == review_with_image.helpful
    assert data[0]["user"] == str(review_with_image.user)
    assert data[0]["product"] == str(review_with_image.product)
    assert len(data[0]["media"]) == 1
    assert data[0]["media"][0]["id"]
    assert data[0]["media"][0]["url"]


def test_get_product_review_by_product_and_review_id(
    staff_api_client, review_with_image
):
    # given
    variables = {
        "product": graphene.Node.to_global_id("Product", review_with_image.product),
        "id": graphene.Node.to_global_id("Review", review_with_image.id),
    }

    # when
    response = staff_api_client.post_graphql(QUERY_GET_PRODUCT_REVIEW, variables)
    content = get_graphql_content(response)

    # then
    data = content["data"]["getProductReview"]
    assert len(data) == 1
    assert data[0]["rating"] == review_with_image.rating
    assert data[0]["title"] == review_with_image.title
    assert data[0]["review"] == review_with_image.review
    assert data[0]["status"] == review_with_image.status
    assert data[0]["helpful"] == review_with_image.helpful
    assert data[0]["user"] == str(review_with_image.user)
    assert data[0]["product"] == str(review_with_image.product)
    assert len(data[0]["media"]) == 1
    assert data[0]["media"][0]["id"]
    assert data[0]["media"][0]["url"]


def test_get_product_review_by_product_and_review_id_with_invalid_product(
    staff_api_client, review_with_image
):
    # given
    variables = {
        "product": graphene.Node.to_global_id("Product", -1),
        "id": graphene.Node.to_global_id("Review", review_with_image.id),
    }
    # when
    response = staff_api_client.post_graphql(QUERY_GET_PRODUCT_REVIEW, variables)
    content = get_graphql_content(response)
    # then
    assert content["data"]["getProductReview"] == []


def test_get_product_review_no_filters(staff_api_client, review):
    # when
    response = staff_api_client.post_graphql(QUERY_GET_PRODUCT_REVIEW, {})
    content = get_graphql_content(response)

    # then
    data = content["data"]["getProductReview"]
    assert data is None


QUERY_GET_PRODUCT_REVIEW_MEDIA_BY_ID = """
    query reviewMediaById($product: ID, $id: ID,$mediaId: ID!) {
        getProductReview(product: $product, id: $id) {
            mediaById(id: $mediaId) {
                id
                url
            }
        }
    }
"""


def test_get_product_review_media_by_id(staff_api_client, review_with_image):
    # given
    media = review_with_image.media.first()
    variables = {
        "product": graphene.Node.to_global_id("Product", review_with_image.product),
        "id": graphene.Node.to_global_id("Review", review_with_image.id),
        "mediaId": graphene.Node.to_global_id("ReviewMedia", media.pk),
    }

    # when
    response = staff_api_client.post_graphql(
        QUERY_GET_PRODUCT_REVIEW_MEDIA_BY_ID, variables
    )
    content = get_graphql_content(response)

    # then
    logger.info(content)
    data = content["data"]["getProductReview"]
    assert data[0]["mediaById"]["id"]
    assert data[0]["mediaById"]["url"]


def test_get_product_review_media_by_id_invalid_media_id(
    staff_api_client, review_with_image
):
    # given
    variables = {
        "product": graphene.Node.to_global_id("Product", review_with_image.product),
        "id": graphene.Node.to_global_id("Review", review_with_image.id),
        "mediaId": graphene.Node.to_global_id("ReviewMedia", -1),
    }

    # when
    response = staff_api_client.post_graphql(
        QUERY_GET_PRODUCT_REVIEW_MEDIA_BY_ID, variables
    )
    content = get_graphql_content(response)

    # then
    assert content["data"]["getProductReview"][0]["mediaById"] is None


def test_get_product_review_media_by_id_invalid_product_id(
    staff_api_client, review_with_image
):
    # given
    variables = {
        "product": graphene.Node.to_global_id("Product", -1),
        "id": graphene.Node.to_global_id("Review", review_with_image.id),
        "mediaId": graphene.Node.to_global_id(
            "ReviewMedia", review_with_image.media.first().pk
        ),
    }

    # when
    response = staff_api_client.post_graphql(
        QUERY_GET_PRODUCT_REVIEW_MEDIA_BY_ID, variables
    )
    content = get_graphql_content(response)

    # then
    assert content["data"]["getProductReview"] == []


QUERY_GET_PRODUCT_REVIEWS = """
    query getProductReviews {
        getProductReviews {
            id
            rating
            title
            review
            status
            helpful
            product
            user
            media{
                id
                url
            }
        }
    }
"""


def test_get_product_reviews(staff_api_client, review_with_image):
    # when
    response = staff_api_client.post_graphql(QUERY_GET_PRODUCT_REVIEWS)
    content = get_graphql_content(response)
    # then
    assert content["data"]["getProductReviews"]
