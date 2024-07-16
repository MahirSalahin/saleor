from django.conf import settings
from django.db import models
from ..core.models import ModelWithMetadata
from ..product.models import Product
from ..account.models import User
from ..graphql.core.fields import JSONString
from ..graphql.core.scalars import DateTime
from ..permission.enums import ProductPermissions

ALL_PRODUCTS_PERMISSIONS = [
    ProductPermissions.MANAGE_PRODUCTS,
]


class Review(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        verbose_name="product",
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="user",
    )
    # rating with choice from 1 to 5
    # RATING_CHOICES = [
    #     (1, "1"),
    #     (2, "2"),
    #     (3, "3"),
    #     (4, "4"),
    #     (5, "5"),
    # ]

    rating = models.PositiveSmallIntegerField()
    review = models.TextField(verbose_name="review")
    title = models.CharField(max_length=255, verbose_name="title")
    media = JSONString(
        blank=True, null=True, verbose_name="media"
    )  # Store URLs of images/videos

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
        permissions = (("manage_reviews", "Can manage product reviews"),)
        verbose_name = "review"
        verbose_name_plural = "reviews"

    def __str__(self):
        return f"Review for {self.product.name} by {self.user.email}"

    def approve(self):
        self.status = True
        self.save()

    def mark_as_helpful(self):
        self.helpful += 1
        self.save()

    def clean(self):
        from django.core.exceptions import ValidationError

        if not (1 <= self.rating <= 5):
            raise ValidationError("Rating must be between 1 and 5")

        super().clean()
