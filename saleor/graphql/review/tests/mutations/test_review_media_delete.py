from unittest.mock import patch

import graphene
import pytest

from .....graphql.tests.utils import get_graphql_content


@patch("saleor.plugins.manager.PluginsManager.review_media_deleted")
@patch("saleor.plugins.manager.PluginsManager.review_updated")
def test_review_media_delete(
    review_updated_mock,
    review_media_deleted_mock,
    staff_api_client,
    review_with_image,
):
    # given
    review = review_with_image
    query = """
            mutation deleteReviewMedia($id: ID!) {
                deleteReviewMedia(id: $id) {
                    media {
                        id
                        url
                    }
                }
            }
        """
    media_obj = review.media.first()
    node_id = graphene.Node.to_global_id("ReviewMedia", media_obj.id)
    variables = {"id": node_id}

    # when
    response = staff_api_client.post_graphql(query, variables)
    content = get_graphql_content(response)

    # then
    data = content["data"]["deleteReviewMedia"]
    assert media_obj.image.url in data["media"]["url"]
    review_media_deleted_mock.assert_called_once_with(media_obj)

    with pytest.raises(media_obj._meta.model.DoesNotExist):
        media_obj.refresh_from_db()
    assert node_id == data["media"]["id"]
    review_updated_mock.assert_called_once_with(review)
