from gradio_client import Client

client = Client("mnraynor90/facefusionfastapi", download_files=True)

source_url = "https://res.cloudinary.com/dddye9wli/image/upload/v1750115036/uploads/selfies/selfie5_qzodk1.jpg"
target_url = "https://res.cloudinary.com/dddye9wli/image/upload/v1749921243/Pocahontas_ys39zg.png"

try:
    print("🔄 Calling /process_images with test URLs...")
    result = client.predict(
        source_url=source_url,
        target_url=target_url,
        api_name="/process_images"
    )
    print("\n✅ SUCCESS!")
    print(result)

except Exception as e:
    print("\n❌ ERROR:")
    print(str(e))
