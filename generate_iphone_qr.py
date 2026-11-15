import os
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

desktop_path = r"C:\Users\TOSHIBA\Desktop"
qr_image_path = os.path.join(desktop_path, "iPhone_Install_QRCode.png")

url = "http://172.168.49.101:5000"

try:
    from PIL import Image, ImageDraw, ImageFont
    
    # Create canvas
    img = Image.new('RGB', (600, 600), color=(15, 12, 29))
    d = ImageDraw.Draw(img)
    
    # Draw border box
    d.rectangle([(20, 20), (580, 580)], outline=(192, 132, 252), width=4)
    
    # Text Header
    d.text((60, 40), "FBPOSTER ENTERPRISE - IPHONE APP", fill=(250, 204, 21))
    d.text((60, 80), "Quet Ma QR Này Bang Camera iPhone De Mo Web App:", fill=(255, 255, 255))
    d.text((60, 120), url, fill=(56, 189, 248))
    
    # Try using qrcode module if available, otherwise draw URL box
    try:
        import qrcode
        qr = qrcode.QRCode(version=1, box_size=10, border=2)
        qr.add_data(url)
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color="black", back_color="white")
        qr_img = qr_img.resize((350, 350))
        img.paste(qr_img, (125, 170))
    except ImportError:
        # Visual fallback QR placeholder box
        d.rectangle([(125, 170), (475, 520)], fill=(255, 255, 255), outline=(147, 51, 234), width=3)
        d.text((150, 320), "AP MO SAFARI TRENI PHONE & NGO:", fill=(0, 0, 0))
        d.text((160, 360), url, fill=(37, 99, 235))
    
    img.save(qr_image_path)
    print(f"SUCCESS_QR: {qr_image_path}")

except Exception as e:
    print(f"ERROR: {e}")
