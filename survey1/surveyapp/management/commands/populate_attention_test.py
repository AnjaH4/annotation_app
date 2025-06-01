from django.core.management.base import BaseCommand, CommandError
from surveyapp.models import AttentionTestImage
import os



class Command(BaseCommand):
    help = "Fills AttentionTestImage table with image file paths from sbi_fake and sbi_real for attention test"

    def _input_imgs(self):
        base_path = "surveyapp/static/img/SBIs/attention_test"
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
                    fake_rel_path = f"img/SBIs/attention_test/sbi_fake/frames/{frame_folder}/{fake_file}"
                    real_rel_path = f"img/SBIs/attention_test/sbi_real/frames/{frame_folder}/{fake_file}"

                    # Only add if it doesn't already exist
                    if not AttentionTestImage.objects.filter(image_id=img_id).exists():
                        images_to_create.append(
                            AttentionTestImage(
                                image_id=img_id,
                                fake_path=fake_rel_path,
                                real_path=real_rel_path,
                                times_seen=0  # Initialize times_seen to 0
                            )
                        )

        # Bulk insert for efficiency
        if images_to_create:
            AttentionTestImage.objects.bulk_create(images_to_create)
            self.stdout.write(self.style.SUCCESS(f"Added {len(images_to_create)} new images."))
        else:
            self.stdout.write(self.style.WARNING("No new images to add."))

    def handle(self, *args, **options):
        self._input_imgs()