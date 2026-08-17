import httpx
from django import forms
from django.core.files.base import ContentFile
from django.utils.text import slugify

from images.models import Image


class ImageCreateForm(forms.ModelForm):
    class Meta:
        model = Image
        fields = ("title", "url", "description")
        widgets = {
            "url": forms.HiddenInput,
        }

    def clean_url(self):
        url: str = self.cleaned_data["url"]
        valid_extensions = ["jpg", "jpeg", "png", "svg"]
        extension = url.rsplit(".", 1)[1].lower()
        if extension not in valid_extensions:
            raise forms.ValidationError("The given URL does not match valid image extensions.")
        return url

    def save(self, force_insert=False, force_update=False, commit=True):
        image: Image = super().save(commit=False)
        image_url: str = self.cleaned_data["url"]
        image_name: str = f"{slugify(image.title)}.{image_url.rsplit('.', 1)[1].lower()}"
        try:
            response = httpx.get(image_url)
        except httpx.HTTPError:
            raise forms.ValidationError("Failed to fetch the image from the given URL.")
        else:
            image.image.save(image_name, ContentFile(response.content), save=False)
            if commit:
                image.save()
            return image