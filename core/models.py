from django.db import models


class TimeStampMixin(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created at")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated at")

    class Meta:
        abstract = True


class StyleMixin(models.Model):
    color = models.CharField(null=False,
                             blank=True,
                             max_length=6,
                             default="4caf50",
                             verbose_name="Color",
                             help_text="Color in HEX format")
    icon = models.CharField(null=True,
                            blank=True,
                            max_length=1,
                            verbose_name="Emoji icon")

    class Meta:
        abstract = True
