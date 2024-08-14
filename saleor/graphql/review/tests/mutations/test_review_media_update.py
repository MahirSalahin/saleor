from unittest.mock import patch

import graphene

from .....graphql.tests.utils import get_graphql_content
from .....review.error_codes import ReviewErrorCode

REVIEW_MEDIA_UPDATE_QUERY = """
    mutation updateReviewMedia($mediaId: ID!, $alt: String) {
        updateReviewMedia(id: $mediaId, input: {alt: $alt}) {
            media {
                alt
            }
            errors {
                code
                field
            }
        }
    }
    """


@patch("saleor.plugins.manager.PluginsManager.review_media_updated")
@patch("saleor.plugins.manager.PluginsManager.review_updated")
def test_review_image_update_mutation(
    review_updated_mock,
    review_media_update_mock,
    monkeypatch,
    staff_api_client,
    review_with_image,
):
    # given

    media_obj = review_with_image.media.first()
    alt = "damage alt"
    assert media_obj.alt != alt
    variables = {
        "alt": alt,
        "mediaId": graphene.Node.to_global_id("ReviewMedia", media_obj.id),
    }

    # when
    response = staff_api_client.post_graphql(REVIEW_MEDIA_UPDATE_QUERY, variables)
    content = get_graphql_content(response)

    # then
    media_obj.refresh_from_db()
    assert content["data"]["updateReviewMedia"]["media"]["alt"] == alt
    assert media_obj.alt == alt

    review_updated_mock.assert_called_once_with(review_with_image)
    review_media_update_mock.assert_called_once_with(media_obj)


def test_review_image_update_mutation_alt_over_char_limit(
    monkeypatch,
    staff_api_client,
    review_with_image,
):
    # given
    media_obj = review_with_image.media.first()
    alt_over_250 = """
    Lorem ipsum dolor sit amet, consectetuer adipiscing elit.
    Aenean commodo ligula eget dolor. Aenean massa. Cym sociis natoque penatibus et
    magnis dis parturient montes, nascetur ridiculus mus. Donec quam felis, ultricies
    nec, pellentesque eu, pretium quis, sem.
    """
    variables = {
        "alt": alt_over_250,
        "mediaId": graphene.Node.to_global_id("ReviewMedia", media_obj.id),
    }

    # when
    response = staff_api_client.post_graphql(REVIEW_MEDIA_UPDATE_QUERY, variables)
    content = get_graphql_content(response)

    # then
    errors = content["data"]["updateReviewMedia"]["errors"]
    assert len(errors) == 1
    assert errors[0]["field"] == "input"
    assert errors[0]["code"] == ReviewErrorCode.INVALID.name
