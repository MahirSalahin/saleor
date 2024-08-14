import graphene
import pytest

from .....review.models import Review
from .....graphql.tests.utils import assert_no_permission, get_graphql_content
from .....review.error_codes import ReviewErrorCode

DELETE_REVIEW_MUTATION = """
    mutation DeleteProductReview($id: ID!) {
        deleteProductReview(id: $id) {
            review {
                id
            }
            errors {
                field
                code
            }
        }
    }
"""


def test_delete_review(staff_api_client, review):
    # given
    review_id = graphene.Node.to_global_id("Review", review.id)
    variables = {"id": review_id}

    # when
    response = staff_api_client.post_graphql(DELETE_REVIEW_MUTATION, variables)

    # then
    content = get_graphql_content(response)
    data = content["data"]["deleteProductReview"]

    assert data["review"]["id"] == review_id
    with pytest.raises(Review.DoesNotExist):
        review.refresh_from_db()


# def test_delete_review_no_permissions(staff_api_client, review):
#     # given
#     review_id = graphene.Node.to_global_id("Review", review.id)
#     variables = {"id": review_id}

#     # when
#     response = staff_api_client.post_graphql(DELETE_REVIEW_MUTATION, variables)

#     # then
#     assert_no_permission(response)


def test_delete_review_invalid_id(staff_api_client):
    # given
    invalid_review_id = graphene.Node.to_global_id("Review", -1)
    variables = {"id": invalid_review_id}

    # when
    response = staff_api_client.post_graphql(DELETE_REVIEW_MUTATION, variables)

    # then
    content = get_graphql_content(response)
    errors = content["data"]["deleteProductReview"]["errors"]

    assert len(errors) == 1
    assert errors[0]["field"] == "id"
    assert errors[0]["code"] == ReviewErrorCode.NOT_FOUND.name


def test_delete_review_already_deleted(staff_api_client, review):
    # given
    review_id = graphene.Node.to_global_id("Review", review.id)
    review.delete()
    variables = {"id": review_id}

    # when
    response = staff_api_client.post_graphql(DELETE_REVIEW_MUTATION, variables)

    # then
    content = get_graphql_content(response)
    errors = content["data"]["deleteProductReview"]["errors"]

    assert len(errors) == 1
    assert errors[0]["field"] == "id"
    assert errors[0]["code"] == ReviewErrorCode.NOT_FOUND.name
