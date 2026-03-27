"""
Image captioning module using Salesforce BLIP model.
"""
from transformers import BlipProcessor, BlipForConditionalGeneration
from PIL import Image
import torch

class ImageCaptioner:
    def __init__(self, model_name="Salesforce/blip-image-captioning-base"):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"🖼️ Initializing Image Captioner on {self.device}...")
        try:
            self.processor = BlipProcessor.from_pretrained(model_name)
            self.model = BlipForConditionalGeneration.from_pretrained(model_name).to(self.device)
            self.ready = True
        except Exception as e:
            print(f"Error loading image captioning model: {e}")
            self.ready = False

    def generate_caption(self, image):
        """
        Generate a short description for the given PIL Image.
        """
        if not self.ready:
            return "Image processing unavailable."
        
        try:
            if image.mode != "RGB":
                image = image.convert("RGB")
            
            inputs = self.processor(image, return_tensors="pt").to(self.device)
            
            out = self.model.generate(**inputs, max_new_tokens=50)
            caption = self.processor.decode(out[0], skip_special_tokens=True)
            return caption
        except Exception as e:
            print(f"Error captioning image: {e}")
            return "Error generating caption."
