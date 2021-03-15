import io
import os
from PIL import Image
from django.core.files.base import ContentFile

from ..document.models import ImageModel


# @app.task
def create_thumbnail_images(obj_ids, size=(150, 150)):
    objs = ImageModel.objects.filter(id__in=obj_ids)
    for obj in objs:
        image = Image.open(obj.file)
        image.thumbnail(size, Image.ANTIALIAS)
        thumb_name, thumb_extension = os.path.splitext(obj.file.name)
        thumb_extension = thumb_extension.lower()

        thumb_filename = thumb_name + f'_thumb_{size[0]}_{size[1]}' + thumb_extension

        if thumb_extension in ['.jpg', '.jpeg']:
            FTYPE = 'JPEG'
        elif thumb_extension == '.gif':
            FTYPE = 'GIF'
        elif thumb_extension == '.png':
            FTYPE = 'PNG'
        else:
            raise ValueError('invalid file format')

        temp_thumb = io.BytesIO()
        image.save(temp_thumb, FTYPE)
        temp_thumb.seek(0)

        obj.thumbnail_150.save(thumb_filename, ContentFile(temp_thumb.read()), save=False)
        temp_thumb.close()
        obj.save()

