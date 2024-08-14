import pytest
from django.db.utils import IntegrityError
from ..models import Review, ReviewMedia

@pytest.mark.django_db
def test_create_review():
    review = Review.objects.create(
        product=1,
        user=1,
        rating=5,
        review="This is a test review.",
        title="Test Review",
    )
    assert review.id is not None
    assert review.rating == 5
    assert review.review == "This is a test review."
    assert review.title == "Test Review"
    assert not review.status
    assert review.helpful == 0


@pytest.mark.django_db
def test_approve_review():
    review = Review.objects.create(
        product=1,
        user=1,
        rating=5,
        review="This is a test review.",
        title="Test Review",
    )
    review.approve()
    assert review.status


@pytest.mark.django_db
def test_mark_as_helpful():
    review = Review.objects.create(
        product=1,
        user=1,
        rating=5,
        review="This is a test review.",
        title="Test Review",
    )
    review.mark_as_helpful()
    assert review.helpful == 1
    review.mark_as_helpful()
    assert review.helpful == 2


@pytest.mark.django_db
def test_create_review_media():
    review = Review.objects.create(
        product=1,
        user=1,
        rating=5,
        review="This is a test review.",
        title="Test Review",
    )
    media = ReviewMedia.objects.create(
        review=review,
        image="path/to/image.jpg",
        alt="An image",
        type="IMAGE",
    )
    assert media.id is not None
    assert media.review == review
    assert media.image == "path/to/image.jpg"
    assert media.alt == "An image"
    assert media.type == "IMAGE"


@pytest.mark.django_db
def test_review_media_deletion():
    review = Review.objects.create(
        product=1,
        user=1,
        rating=5,
        review="This is a test review.",
        title="Test Review",
    )
    media = ReviewMedia.objects.create(
        review=review,
        image="path/to/image.jpg",
        alt="An image",
        type="IMAGE",
    )
    media_id = media.id
    media.delete()
    assert not ReviewMedia.objects.filter(id=media_id).exists()


@pytest.mark.django_db
def test_review_str():
    review = Review.objects.create(
        product=1,
        user=1,
        rating=5,
        review="This is a test review.",
        title="Test Review",
    )
    assert str(review) == "Test Review - 5"


@pytest.mark.django_db
def test_review_media_ordering():
    review = Review.objects.create(
        product=1,
        user=1,
        rating=5,
        review="This is a test review.",
        title="Test Review",
    )
    media1 = ReviewMedia.objects.create(review=review, type="IMAGE")
    media2 = ReviewMedia.objects.create(review=review, type="IMAGE")
    media3 = ReviewMedia.objects.create(review=review, type="IMAGE")

    assert list(review.media.all()) == [media1, media2, media3]
