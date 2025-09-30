import qrcode
import os
from pathlib import Path
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class QRCodeService:

    @staticmethod
    def get_qr_images_directory() -> Path:
        """Get the directory for storing QR Code images"""
        # create qr_images directory in project root
        qr_dir = Path(__file__).parent.parent.parent / "qr_images"
        qr_dir.mkdir(exist_ok=True) 
        return qr_dir
    
    @staticmethod
    def generate_profile_qr_image(
        user_code: str,
        qr_code_id: str,
        profile_url: str,
        display_name: Optional[str] = None
    ) -> str:
        """
        Generate a clean QR code image for design team to use in card production
        Returns: relative path to saved image
        """

        try:
            # Create QR code with minimal, clean settings to match frontend display
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,  # Low error correction for simpler pattern
                box_size=6,  # Smaller box size for cleaner look
                border=2     # Minimal border
            )
            qr.add_data(profile_url)
            qr.make(fit=True)

            # Create QR code image
            qr_img = qr.make_image(fill_color="black", back_color="white")

            # Save with descriptive filename for design POC
            qr_dir = QRCodeService.get_qr_images_directory()
            filename = f"qr_{user_code}.png"
            file_path = qr_dir / filename

            qr_img.save(file_path, "PNG")

            relative_path = f"qr_images/{filename}"
            logger.info(f"Generated QR image for design team: {relative_path}")
            return relative_path
        
        except Exception as e:
            logger.error(f"Failed to generate QR image for {user_code}: {str(e)}")
            raise e