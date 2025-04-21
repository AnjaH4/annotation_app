from django.core.management.base import BaseCommand, CommandError
from surveyapp.models import Image
import os

# class Command(BaseCommand): #to spremeni
#     help = 'Fills database with relevant images'

#     def _input_imgs(self):
#         for i in range(1,101):
#             if not Image.objects.filter(image_id="image"+str(i), filename="person("+str(i)+").jpg").exists():
#                 image = Image(image_id="image"+str(i),
#                               filename="person("+str(i)+").jpg")
#                 image.save()
#         print(Image.objects.all())


#     def handle(self, *args, **options):
#         self._input_imgs()


class Command(BaseCommand):
    help = "Fills database with image file paths from sbi_fake and sbi_real"

    def _input_imgs(self):
        base_path = "surveyapp/static/img/SBIs"
        fake_dir = os.path.join(base_path, "sbi_fake/frames")
        real_dir = os.path.join(base_path, "sbi_real/frames")

        images_to_create = []

        # Iterate over subdirectories (frame folders)
        for frame_folder in sorted(os.listdir(fake_dir)):
            fake_path = os.path.join(fake_dir, frame_folder)
            real_path = os.path.join(real_dir, frame_folder)

            if not os.path.isdir(fake_path) or not os.path.isdir(real_path):
                continue  # Skip if it's not a directory

            fake_files = sorted(os.listdir(fake_path))
            real_files = sorted(os.listdir(real_path))

            for fake_file in fake_files:
                if fake_file in real_files:  # Ensure corresponding real file exists
                    img_id = f"{frame_folder}/{fake_file}"  # Unique ID based on folder structure
                    fake_rel_path = f"img/SBIs/sbi_fake/frames/{frame_folder}/{fake_file}"
                    real_rel_path = f"img/SBIs/sbi_real/frames/{frame_folder}/{fake_file}"

                    # Only add if it doesn't already exist
                    if not Image.objects.filter(image_id=img_id).exists():
                        images_to_create.append(
                            Image(
                                image_id=img_id, 
                                fake_path=fake_rel_path, 
                                real_path=real_rel_path,
                                times_seen=0  # Initialize times_seen to 0
                            )
                        )

        # Bulk insert for efficiency
        if images_to_create:
            Image.objects.bulk_create(images_to_create)
            self.stdout.write(self.style.SUCCESS(f"Added {len(images_to_create)} new images."))
        else:
            self.stdout.write(self.style.WARNING("No new images to add."))

    def handle(self, *args, **options):
        self._input_imgs()

