import json
import os
from unittest.mock import patch

import graphene
import pytest

from .....graphql.tests.utils import get_graphql_content, get_multipart_request_body
from .....review.error_codes import ReviewErrorCode
from .....review import ReviewMediaTypes
from .....review.tests.utils import create_image, create_zip_file_with_image_ext

REVIEW_MEDIA_CREATE_QUERY = """
    mutation createReviewMedia(
        $review: ID!,
        $image: Upload,
        $mediaUrl: String,
        $alt: String
    ) {
        createReviewMedia(input: {
            review: $review,
            mediaUrl: $mediaUrl,
            alt: $alt,
            image: $image
        }) {
            review {
                media {
                    url
                    alt
                    type
                    oembedData
                }
            }
            errors {
                code
                field
            }
        }
    }
"""


@patch("saleor.plugins.manager.PluginsManager.review_media_created")
@patch("saleor.plugins.manager.PluginsManager.review_updated")
def test_review_media_create_mutation(
    review_updated_mock,
    review_media_created,
    monkeypatch,
    staff_api_client,
    review,
    media_root,
):
    # given
    image_file, image_name = create_image()
    variables = {
        "review": graphene.Node.to_global_id("Review", review.id),
        "alt": "",
        "image": image_name,
    }
    body = get_multipart_request_body(
        REVIEW_MEDIA_CREATE_QUERY, variables, image_file, image_name
    )

    # when
    response = staff_api_client.post_multipart(body)
    get_graphql_content(response)

    # then
    review.refresh_from_db()
    review_image = review.media.last()
    assert review_image.image.file
    img_name, format = os.path.splitext(image_file._name)
    file_name = review_image.image.name
    assert file_name != image_file._name
    assert file_name.startswith(f"reviews/{img_name}")
    assert file_name.endswith(format)

    review_updated_mock.assert_called_once_with(review)
    review_media_created.assert_called_once_with(review_image)


def test_review_media_create_mutation_without_file(
    monkeypatch, staff_api_client, review, media_root
):
    # given
    variables = {
        "review": graphene.Node.to_global_id("Review", review.id),
        "image": "image name",
    }
    body = get_multipart_request_body(
        REVIEW_MEDIA_CREATE_QUERY, variables, file="", file_name="name"
    )

    # when
    response = staff_api_client.post_multipart(body)
    content = get_graphql_content(response)

    # then
    errors = content["data"]["createReviewMedia"]["errors"]
    assert errors[0]["field"] == "image"
    assert errors[0]["code"] == ReviewErrorCode.REQUIRED.name


# @pytest.mark.vcr
# def test_review_media_create_mutation_with_media_url(
#     monkeypatch, staff_api_client, review, media_root
# ):
#     # given
#     variables = {
#         "review": graphene.Node.to_global_id("Review", review.id),
#         "mediaUrl": "https://www.youtube.com/watch?v=XB-wiC2AGoM",
#         "alt": "",
#     }
#     body = get_multipart_request_body(
#         REVIEW_MEDIA_CREATE_QUERY, variables, file="", file_name="name1"
#     )

#     # when
#     response = staff_api_client.post_multipart(body)
#     content = get_graphql_content(response)

#     # then
#     media = content["data"]["createReviewMedia"]["review"]["media"]
#     alt = "BRILLIANT WIN!!!!!!!"

#     assert len(media) == 1
#     assert media[0]["url"] == "https://www.youtube.com/watch?v=XB-wiC2AGoM"
#     assert media[0]["alt"] == alt
#     assert media[0]["type"] == ReviewMediaTypes.VIDEO

#     oembed_data = json.loads(media[0]["oembedData"])
#     assert oembed_data["url"] == "https://www.youtube.com/watch?v=XB-wiC2AGoM"
#     assert oembed_data["type"] == "video"
#     assert oembed_data["html"] is not None


def test_review_media_create_mutation_without_url_or_image(
    monkeypatch, staff_api_client, review, media_root
):
    # given
    variables = {
        "review": graphene.Node.to_global_id("Review", review.id),
        "alt": "Test Alt Text",
    }
    body = get_multipart_request_body(
        REVIEW_MEDIA_CREATE_QUERY, variables, file="", file_name="name"
    )

    # when
    response = staff_api_client.post_multipart(body)
    content = get_graphql_content(response)

    # then
    errors = content["data"]["createReviewMedia"]["errors"]
    assert len(errors) == 1
    assert errors[0]["code"] == ReviewErrorCode.REQUIRED.name
    assert errors[0]["field"] == "input"


def test_review_media_create_mutation_with_both_url_and_image(
    monkeypatch, staff_api_client, review, media_root
):
    # given
    image_file, image_name = create_image()
    variables = {
        "review": graphene.Node.to_global_id("Review", review.id),
        "mediaUrl": "https://www.youtube.com/watch?v=SomeVideoID&ab_channel=Test",
        "image": image_name,
        "alt": "Test Alt Text",
    }
    body = get_multipart_request_body(
        REVIEW_MEDIA_CREATE_QUERY, variables, image_file, image_name
    )

    # when
    response = staff_api_client.post_multipart(body)
    content = get_graphql_content(response)

    # then
    errors = content["data"]["createReviewMedia"]["errors"]
    assert len(errors) == 1
    assert errors[0]["code"] == ReviewErrorCode.DUPLICATED_INPUT_ITEM.name
    assert errors[0]["field"] == "input"


def test_review_media_create_mutation_with_unknown_url(
    monkeypatch, staff_api_client, review, media_root
):
    # given
    variables = {
        "review": graphene.Node.to_global_id("Review", review.id),
        "mediaUrl": "https://www.videohosting.com/SomeVideoID",
        "alt": "Test Alt Text",
    }
    body = get_multipart_request_body(
        REVIEW_MEDIA_CREATE_QUERY, variables, file="", file_name="name"
    )

    # when
    response = staff_api_client.post_multipart(body)
    content = get_graphql_content(response)

    # then
    errors = content["data"]["createReviewMedia"]["errors"]
    assert len(errors) == 1
    assert errors[0]["code"] == ReviewErrorCode.UNSUPPORTED_MEDIA_PROVIDER.name
    assert errors[0]["field"] == "mediaUrl"


def test_invalid_review_media_create_mutation(staff_api_client, review):
    # given
    query = """
    mutation createReviewMedia($image: Upload!, $review: ID!) {
        createReviewMedia(input: {image: $image, review: $review}) {
            media {
                id
                url
            }
            errors {
                field
                message
            }
        }
    }
    """
    image_file, image_name = create_zip_file_with_image_ext()
    variables = {
        "review": graphene.Node.to_global_id("Review", review.id),
        "image": image_name,
    }
    body = get_multipart_request_body(query, variables, image_file, image_name)

    # when
    response = staff_api_client.post_multipart(body)
    content = get_graphql_content(response)

    # then
    assert content["data"]["createReviewMedia"]["errors"] == [
        {"field": "image", "message": "Invalid file type."}
    ]
    review.refresh_from_db()
    assert review.media.count() == 0


def test_review_media_create_mutation_alt_character_limit(
    monkeypatch, staff_api_client, review, media_root
):
    alt_260_chars = """
    Lorem ipsum dolor sit amet, consectetuer adipiscing elit.
    Aenean commodo ligula eget dolor. Aenean massa. Cym sociis natoque penatibus et
    magnis dis parturient montes, nascetur ridiculus mus. Donec quam felis, ultricies
    nec, pellentesque eu, pretium quis, sem.
    """
    # given
    image_file, image_name = create_image()
    variables = {
        "review": graphene.Node.to_global_id("review", review.id),
        "alt": alt_260_chars,
        "image": image_name,
    }
    body = get_multipart_request_body(
        REVIEW_MEDIA_CREATE_QUERY, variables, image_file, image_name
    )

    # when
    response = staff_api_client.post_multipart(body)
    content = get_graphql_content(response)

    # then

    errors = content["data"]["createReviewMedia"]["errors"]
    assert errors[0]["field"] == "input"
    assert errors[0]["code"] == ReviewErrorCode.INVALID.name
