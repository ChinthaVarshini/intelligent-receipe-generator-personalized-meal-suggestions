try:
    from torchvision import transforms
    import torch

    def preprocess_image(pil_img):
        transform = transforms.Compose([
            transforms.Resize((224,224)),
            transforms.ToTensor()
        ])
        return transform(pil_img).unsqueeze(0)

except Exception:
    # Lightweight fallback when torchvision/torch is not installed.
    # The production code expects a tensor for model input, but in
    # the current codebase `preprocess_image` is not used by request
    # handlers. Provide a safe, minimal implementation so the app
    # can start without installing heavy ML dependencies.
    from PIL import Image

    def preprocess_image(pil_img):
        # Resize to 224x224 and return the PIL image (fallback).
        try:
            return pil_img.resize((224, 224), Image.BILINEAR)
        except Exception:
            return pil_img
