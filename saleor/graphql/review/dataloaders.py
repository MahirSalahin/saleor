from ..core.dataloaders import BaseThumbnailBySizeAndFormatLoader


class ThumbnailByReviewMediaIdSizeAndFormatLoader(BaseThumbnailBySizeAndFormatLoader):
    context_key = "thumbnail_by_reviewmedia_size_and_format"
    model_name = "review_media"
