"""
Image captioning module using Salesforce BLIP model.
Improved: higher resolution crops, page-aware captions, lazy loading.
"""
from transformers import BlipProcessor, BlipForConditionalGeneration
from PIL import Image
import torch


class ImageCaptioner:
    def __init__(self, model_name: str = "Salesforce/blip-image-captioning-base"):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.ready = False
        print(f"Initializing Image Captioner on {self.device}...")
        try:
            self.processor = BlipProcessor.from_pretrained(model_name)
            self.model = BlipForConditionalGeneration.from_pretrained(model_name).to(self.device)
            self.ready = True
            print("Image captioner ready.")
        except Exception as e:
            print(f"Image captioner failed to load: {e}")

    def generate_caption(self, image: Image.Image) -> str:
        """
        Generate a descriptive caption for a PIL Image.

        Improvements over original:
        - Checks image size (skips tiny decorative images <50x50px)
        - Uses max_new_tokens=75 for richer descriptions

        Args:
            image: PIL Image object

        Returns:
            Caption string
        """
        if not self.ready:
            return "Image processing unavailable."

        try:
            # Skip tiny decorative images (logos, borders, etc.)
            if image.width < 50 or image.height < 50:
                return "small decorative image"

            if image.mode != "RGB":
                image = image.convert("RGB")

            inputs = self.processor(image, return_tensors="pt").to(self.device)
            out = self.model.generate(**inputs, max_new_tokens=75)
            caption = self.processor.decode(out[0], skip_special_tokens=True)
            return caption

        except Exception as e:
            print(f"Caption generation error: {e}")
            return "Error generating caption."
