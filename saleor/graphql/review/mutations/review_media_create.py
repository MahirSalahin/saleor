import graphene
from django.core.exceptions import ValidationError
from django.core.files import File
from ....core.http_client import HTTPClient
from ....review import ReviewMediaTypes, models
from ....review.error_codes import ReviewErrorCode
from ....core.utils.validators import get_oembed_data
from ....thumbnail.utils import get_filename_from_url
from ...core import ResolveInfo
from ...core.types import BaseInputObjectType, Upload
from ...core.doc_category import DOC_CATEGORY_PRODUCTS
from ...core.mutations import BaseMutation
from ...core.types import ReviewError
from ...plugins.dataloaders import get_plugin_manager_promise
from ...core.validators.file import clean_image_file, is_image_url, validate_image_url
from ..types import Review, ReviewMedia

ALT_CHAR_LIMIT = 250


class CreateReviewMediaInput(BaseInputObjectType):
    alt = graphene.String(description="Alt text for a review media.")
    image = Upload(
        required=False, description="Represents an image file in a multipart request."
    )
    review = graphene.ID(required=True, description="ID of a review.", name="review")
    media_url = graphene.String(
        required=False, description="Represents an URL to an external media."
    )

    class Meta:
        doc_category = DOC_CATEGORY_PRODUCTS


class CreateReviewMedia(BaseMutation):
    review = graphene.Field(Review)
    media = graphene.Field(ReviewMedia)

    class Arguments:
        input = CreateReviewMediaInput(
            required=True, description="Fields required to create a review media."
        )

    class Meta:
        description = (
            "Create a media object (image or video URL) associated with review. "
            "For image, this mutation must be sent as a `multipart` request. "
            "More detailed specs of the upload format can be found here: "
            "https://github.com/jaydenseric/graphql-multipart-request-spec"
        )
        doc_category = DOC_CATEGORY_PRODUCTS
        error_type_class = ReviewError
        error_type_field = "review_errors"

    @classmethod
    def validate_input(cls, data):
        image = data.get("image")
        media_url = data.get("media_url")
        alt = data.get("alt")

        if not image and not media_url:
            raise ValidationError(
                {
                    "input": ValidationError(
                        "Image or external URL is required.",
                        code=ReviewErrorCode.REQUIRED.value,
                    )
                }
            )
        if image and media_url:
            raise ValidationError(
                {
                    "input": ValidationError(
                        "Either image or external URL is required.",
                        code=ReviewErrorCode.DUPLICATED_INPUT_ITEM.value,
                    )
                }
            )

        if alt and len(alt) > ALT_CHAR_LIMIT:
            raise ValidationError(
                {
                    "input": ValidationError(
                        f"Alt field exceeds the character "
                        f"limit of {ALT_CHAR_LIMIT}.",
                        code=ReviewErrorCode.INVALID.value,
                    )
                }
            )

    @classmethod
    def perform_mutation(  # type: ignore[override]
        cls, _root, info: ResolveInfo, /, *, input
    ):
        cls.validate_input(input)
        review = cls.get_node_or_error(
            info,
            input["review"],
            field="review",
            only_type=Review,
            qs=models.Review.objects.all(),
        )

        alt = input.get("alt", "")
        media_url = input.get("media_url")
        media = None
        if img_data := input.get("image"):
            input["image"] = info.context.FILES.get(img_data)
            image_data = clean_image_file(input, "image", ReviewErrorCode)
            media = review.media.create(
                image=image_data, alt=alt, type=ReviewMediaTypes.IMAGE
            )
        if media_url:
            # Remote URLs can point to the images or oembed data.
            # In case of images, file is downloaded. Otherwise we keep only
            # URL to remote media.
            if is_image_url(media_url):
                validate_image_url(
                    media_url, "media_url", ReviewErrorCode.INVALID.value
                )
                filename = get_filename_from_url(media_url)
                image_data = HTTPClient.send_request(
                    "GET", media_url, stream=True, allow_redirects=False
                )
                image_file = File(image_data.raw, filename)
                media = review.media.create(
                    image=image_file,
                    alt=alt,
                    type=ReviewMediaTypes.IMAGE,
                )
            else:
                oembed_data, media_type = get_oembed_data(media_url, "media_url")
                media = review.media.create(
                    external_url=oembed_data["url"],
                    alt=oembed_data.get("title", alt),
                    type=media_type,
                    oembed_data=oembed_data,
                )
        manager = get_plugin_manager_promise(info.context).get()
        cls.call_event(manager.review_updated, review)
        cls.call_event(manager.review_media_created, media)
        return CreateReviewMedia(review=review, media=media)
