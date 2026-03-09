import requests
from bs4 import BeautifulSoup
import csv
from datetime import datetime

def get_product_prices():
    url = "https://www.scrapingcourse.com/ecommerce/"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    print("Fetching product prices...")
    response = requests.get(url, headers=headers)
    
    print(f"Status: {response.status_code}")
    
    if response.status_code != 200:
        print("Failed to fetch page")
        return []
    
    soup = BeautifulSoup(response.content, 'html5lib')
    
    products = []
    
    # Find all product containers
    product_cards = soup.find_all('li', class_='product')
    
    print(f"Found {len(product_cards)} products")
    
    for product in product_cards:
        try:
            # Get product name
            name_elem = product.find('h2', class_='woocommerce-loop-product__title')
            name = name_elem.get_text(strip=True) if name_elem else "N/A"
            
            # Get price
            price_elem = product.find('span', class_='woocommerce-Price-amount')
            price = price_elem.get_text(strip=True) if price_elem else "N/A"
            
            # Get product link
            link_elem = product.find('a', href=True)
            link = link_elem['href'] if link_elem else "N/A"
            
            # Get image
            img_elem = product.find('img')
            image = img_elem.get('src', '') if img_elem else ""
            
            # Add timestamp for tracking
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            products.append({
                'Name': name,
                'Price': price,
                'URL': link,
                'Image': image,
                'Date_Tracked': timestamp
            })
            
            print(f"  {name[:40]}... | {price}")
            
        except Exception as e:
            print(f"  Error: {e}")
            continue
    
    return products

def save_prices(products):
    if not products:
        print("No products to save")
        return
    
    filename = f"prices_{datetime.now().strftime('%Y%m%d')}.csv"
    
    with open(filename, 'w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=['Name', 'Price', 'URL', 'Image', 'Date_Tracked'])
        writer.writeheader()
        writer.writerows(products)
    
    print(f"\nSaved {len(products)} products to {filename}!")

# Run the tracker
products = get_product_prices()
save_prices(products)

print("\n" + "="*50)
print("PRICE TRACKER COMPLETE")
print("="*50)