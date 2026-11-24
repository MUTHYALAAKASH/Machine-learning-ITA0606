import subprocess
import os
import tempfile
from PIL import Image

def extract_text_from_image(image_bytes: bytes) -> str:
    """
    Extracts text from an image using Windows 10/11 native OCR engine via PowerShell.
    Works 100% offline with zero external pip dependencies.
    """
    # Save image to temporary file
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
        tmp_path = tmp.name
        tmp.write(image_bytes)

    try:
        # PowerShell script using Windows.Media.Ocr
        ps_script = f"""
        [Windows.Media.Ocr.OcrEngine, Windows.Foundation.UniversalApiContract, ContentType = WindowsRuntime] | Out-Null
        [Windows.Graphics.Imaging.BitmapDecoder, Windows.Foundation.UniversalApiContract, ContentType = WindowsRuntime] | Out-Null
        [Windows.Storage.StorageFile, Windows.Storage, ContentType = WindowsRuntime] | Out-Null

        $file = [Windows.Storage.StorageFile]::GetFileFromPathAsync('{tmp_path}').GetAwaiter().GetResult()
        $stream = $file.OpenAsync([Windows.Storage.FileAccessMode]::Read).GetAwaiter().GetResult()
        $decoder = [Windows.Graphics.Imaging.BitmapDecoder]::CreateAsync($stream).GetAwaiter().GetResult()
        $bitmap = $decoder.GetSoftwareBitmapAsync().GetAwaiter().GetResult()

        $engine = [Windows.Media.Ocr.OcrEngine]::TryCreateFromUserProfileLanguages()
        $result = $engine.RecognizeAsync($bitmap).GetAwaiter().GetResult()
        Write-Output $result.Text
        """
        res = subprocess.run(
            ["powershell", "-NoProfile", "-Command", ps_script],
            capture_output=True,
            text=True,
            timeout=10
        )
        if res.returncode == 0:
            return res.stdout.strip()
        else:
            return ""
    except Exception as e:
        print(f"OCR Error: {e}")
        return ""
    finally:
        if os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
            except:
                pass

if __name__ == "__main__":
    from PIL import Image, ImageDraw
    img = Image.new("RGB", (400, 100), color="white")
    d = ImageDraw.Draw(img)
    d.text((10, 10), "URGENT Work From Home $50/hr Telegram @jobscam", fill="black")
    import io
    b = io.BytesIO()
    img.save(b, format="PNG")
    text = extract_text_from_image(b.getvalue())
    print("OCR Result:", repr(text))
