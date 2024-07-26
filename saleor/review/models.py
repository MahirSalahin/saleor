from django.db import models, transaction
from ..core.models import ModelWithMetadata, SortableModel
from . import ReviewMediaTypes


class Review(ModelWithMetadata):

    product = models.IntegerField()

    user = models.IntegerField()

    rating = models.PositiveSmallIntegerField()
    review = models.TextField(verbose_name="review")
    title = models.CharField(max_length=255, verbose_name="title")
    created_at = models.DateTimeField(
        auto_now_add=True,
    )
    updated_at = models.DateTimeField(
        auto_now=True,
    )
    status = models.BooleanField(default=False, verbose_name="status")
    helpful = models.IntegerField(default=0, verbose_name="helpful")

    class Meta:
        ordering = ["rating"]
        verbose_name = "review"
        verbose_name_plural = "reviews"

    def __str__(self):
        return f"{self.title} - {self.rating}"

    def approve(self):
        self.status = True
        self.save()

    def mark_as_helpful(self):
        self.helpful += 1
        self.save()


class ReviewMedia(SortableModel, ModelWithMetadata):
    review = models.ForeignKey(
        Review,
        related_name="media",
        on_delete=models.CASCADE,
        # DEPRECATED
        null=True,
        blank=True,
    )
    image = models.ImageField(upload_to="reviews", blank=True, null=True)
    alt = models.CharField(max_length=250, blank=True)
    type = models.CharField(
        max_length=32,
        choices=ReviewMediaTypes.CHOICES,
        default=ReviewMediaTypes.IMAGE,
    )
    external_url = models.CharField(max_length=256, blank=True, null=True)
    oembed_data = models.JSONField(blank=True, default=dict)
    # DEPRECATED
    to_remove = models.BooleanField(default=False)

    class Meta(ModelWithMetadata.Meta):
        ordering = ("sort_order", "pk")
        app_label = "review"

    def get_ordering_queryset(self):
        if not self.review:
            return ReviewMedia.objects.none()
        return self.review.media.all()

    @transaction.atomic
    def delete(self, *args, **kwargs):
        super(SortableModel, self).delete(*args, **kwargs)
