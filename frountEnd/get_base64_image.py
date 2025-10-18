import base64

import requests


def get_base64_image(image_url):
    try:
        response = requests.get(image_url)
        if response.status_code == 200:
            return base64.b64encode(response.content).decode('utf-8')
    except Exception as e:
        print("خطا در بارگذاری تصویر:", e)
    return None