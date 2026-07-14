import io
import pytest
from fastapi import UploadFile
from PIL import Image, ImageDraw
from app.services.parsing import extract_text_from_file


@pytest.mark.asyncio
async def test_ocr():
    img = Image.new("RGB", (400, 200), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    draw.text((10, 10), "Hello OCR World", fill=(0, 0, 0))

    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format="PNG")
    img_byte_arr.seek(0)

    mock_file = UploadFile(
        filename="test_image.png",
        file=img_byte_arr,
    )

    text = await extract_text_from_file(mock_file)

    # ✅ Normalize OCR output
    normalized_text = text.lower().replace(" ", "").replace("\n", "")

    assert "helloocrworld" in normalized_text
