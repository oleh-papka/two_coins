from django.db import models


class TimeStampMixin(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created at")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated at")

    class Meta:
        abstract = True


class ColorChoice(models.TextChoices):
    TRANSPARENT = "bg-body", "Transparent"
    PRIMARY_SUBTLE = "bg-primary-subtle", "Acid green light"
    GREEN = "bg-success", "Green"
    GREEN_SUBTLE = "bg-success-subtle", "Green subtle"
    RED = "bg-danger", "Red"
    RED_SUBTLE = "bg-danger-subtle", "Red subtle"
    YELLOW = "bg-warning", "Yellow"
    YELLOW_SUBTLE = "bg-warning-subtle", "Yellow subtle"
    BLUE = "bg-info", "Blue"
    BLUE_SUBTLE = "bg-info-subtle", "Blue subtle"
    GRAY = "bg-light", "Gray"
    BLACK = "bg-dark-subtle", "Black"


class StyleMixin(models.Model):
    color = models.CharField(null=False,
                             blank=True,
                             max_length=25,
                             default=ColorChoice.TRANSPARENT,
                             choices=ColorChoice,
                             verbose_name="Color")
    icon = models.CharField(null=True,
                            blank=True,
                            max_length=10,
                            verbose_name="Emoji icon")

    class Meta:
        abstract = True
