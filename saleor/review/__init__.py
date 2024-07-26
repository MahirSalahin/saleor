class ReviewMediaTypes:
    IMAGE = "IMAGE"
    VIDEO = "VIDEO"

    CHOICES = [
        (IMAGE, "An uploaded image or an URL to an image"),
        (VIDEO, "A URL to an external video"),
    ]


# class ReviewEvents:
#     CREATED = "created"
#     UPDATED = "updated"
#     DELETED = "deleted"
#     APPROVED = "approved"
#     REJECTED = "rejected"

#     CHOICES = [
#         (CREATED, "The review was created"),
#         (UPDATED, "The review was updated"),
#         (DELETED, "The review was deleted"),
#         (APPROVED, "The review was approved"),
#         (REJECTED, "The review was rejected"),
#     ]
