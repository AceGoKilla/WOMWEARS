import json
import shutil
import os
import subprocess
from datetime import datetime

PRODUCTS_FILE = "products.json"
TEMPLATE_FILE = "template.html"
OUTPUT_FILE = "index.html"
PUBLIC_DIR = "public"

def load_products():
    if os.path.exists(PRODUCTS_FILE):
        with open(PRODUCTS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_products(products):
    with open(PRODUCTS_FILE, "w", encoding="utf-8") as f:
        json.dump(products, f, indent=2, ensure_ascii=False)

def add_product(image_url, video_url, product_link):
    products = load_products()
    products.append({
        "image": image_url,
        "video": video_url,
        "link": product_link,
        "timestamp": datetime.now().isoformat()
    })
    save_products(products)

def generate_html():
    products = load_products()
    product_cards = ""
    for product in reversed(products):  # Новые товары сверху
        product_cards += f"""
        <div class="product">
            <a href="{product['link']}" target="_blank">
                <img src="{product['image']}" alt="{product.get('title', 'Product')}" width="200">
            </a>
        </div>
        """

    with open(TEMPLATE_FILE, "r", encoding="utf-8") as f:
        template = f.read()

    html = template.replace("{{PRODUCTS}}", product_cards)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(html)

def deploy_to_netlify():
    try:
        subprocess.run(["netlify", "deploy", "--dir=public", "--prod"], check=True)
        print("✅ Успешный деплой на Netlify")
    except subprocess.CalledProcessError as e:
        print("❌ Ошибка при деплое на Netlify:", e)

def update_site():
    generate_html()
    os.makedirs(PUBLIC_DIR, exist_ok=True)
    shutil.copy("index.html", os.path.join(PUBLIC_DIR, "index.html"))
    deploy_to_netlify()
