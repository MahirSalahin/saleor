import graphene
import pytest

from .....graphql.tests.utils import assert_no_permission, get_graphql_content
from .....review.error_codes import ReviewErrorCode


UPDATE_REVIEW_MUTATION = """
    mutation UpdateProductReview($input: UpdateProductReviewInput!) {
        updateProductReview(input: $input) {
            review {
                id
                status
                helpful
            }
            errors {
                field
                code
            }
        }
    }
"""


def test_update_review_status(staff_api_client, permission_manage_products, review):
    # given
    review_id = graphene.Node.to_global_id("Review", review.id)
    variables = {"input": {"id": review_id, "status": True}}

    # when
    response = staff_api_client.post_graphql(
        UPDATE_REVIEW_MUTATION, variables, permissions=[permission_manage_products]
    )

    # then
    content = get_graphql_content(response)
    data = content["data"]["updateProductReview"]["review"]
    review.refresh_from_db()

    assert data["status"]
    assert review.status


def test_update_review_helpfulness(
    staff_api_client, permission_manage_products, review
):
    # given
    review_id = graphene.Node.to_global_id("Review", review.id)
    current_helpful = review.helpful
    variables = {"input": {"id": review_id, "isHelpful": True}}

    # when
    response = staff_api_client.post_graphql(
        UPDATE_REVIEW_MUTATION, variables, permissions=[permission_manage_products]
    )

    # then
    content = get_graphql_content(response)
    data = content["data"]["updateProductReview"]["review"]
    review.refresh_from_db()

    assert data["helpful"] == current_helpful + 1
    assert review.helpful == current_helpful + 1


def test_update_review_no_permissions(staff_api_client, review):
    # given
    review_id = graphene.Node.to_global_id("Review", review.id)
    variables = {"input": {"id": review_id, "status": True}}

    # when
    response = staff_api_client.post_graphql(UPDATE_REVIEW_MUTATION, variables)

    # then
    assert_no_permission(response)


def test_update_review_invalid_id(staff_api_client, permission_manage_products):
    # given
    invalid_review_id = graphene.Node.to_global_id("Review", -1)
    variables = {"input": {"id": invalid_review_id, "status": True}}

    # when
    response = staff_api_client.post_graphql(
        UPDATE_REVIEW_MUTATION, variables, permissions=[permission_manage_products]
    )

    # then
    content = get_graphql_content(response)
    errors = content["data"]["updateProductReview"]["errors"]

    assert len(errors) == 1
    assert errors[0]["field"] == "id"
    assert errors[0]["code"] == ReviewErrorCode.NOT_FOUND.name


@pytest.mark.parametrize("helpful_value", [True, False])
def test_update_review_helpfulness_toggle(
    staff_api_client, permission_manage_products, review, helpful_value
):
    # given
    review_id = graphene.Node.to_global_id("Review", review.id)
    current_helpful = review.helpful
    variables = {"input": {"id": review_id, "isHelpful": helpful_value}}

    # when
    response = staff_api_client.post_graphql(
        UPDATE_REVIEW_MUTATION, variables, permissions=[permission_manage_products]
    )

    # then
    content = get_graphql_content(response)
    data = content["data"]["updateProductReview"]["review"]
    review.refresh_from_db()

    if helpful_value:
        assert data["helpful"] == current_helpful + 1
        assert review.helpful == current_helpful + 1
    else:
        assert data["helpful"] == current_helpful - 1
        assert review.helpful == current_helpful - 1
