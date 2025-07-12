# products/utils.py
import random
import string
import barcode
from barcode.writer import ImageWriter


def generate_barcode(product_name):
    # Generate a random 12-digit EAN13 barcode
    barcode_code = ''.join(random.choices(string.digits, k=12))

    # You can use any barcode generation logic here (like a barcode image generator)
    # For simplicity, we just return the barcode code and some dummy image URL
    barcode_image = "dummy_image_url"  # Replace this with actual barcode image generation logic

    return barcode_image, barcode_code


def generate_barcode_image(barcode_number):
    code = barcode.get('code128', barcode_number, writer=ImageWriter())
    return code.render()

