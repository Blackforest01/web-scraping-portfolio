import requests
from bs4 import BeautifulSoup
import csv
from datetime import datetime
import time
import schedule
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Configuration (you'll fill this in)
EMAIL_SENDER = "your_email@gmail.com"
EMAIL_PASSWORD = "your_app_password"
EMAIL_RECEIVER = "client_email@example.com"
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

def get_current_prices():
    """Scrape current prices"""
    url = "https://www.scrapingcourse.com/ecommerce/"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html5lib')
    
    products = {}
    
    product_cards = soup.find_all('li', class_='product')
    
    for product in product_cards:
        try:
            name_elem = product.find('h2', class_='woocommerce-loop-product__title')
            name = name_elem.get_text(strip=True) if name_elem else "Unknown"
            
            price_elem = product.find('span', class_='woocommerce-Price-amount')
            price_text = price_elem.get_text(strip=True) if price_elem else "$0"
            
            # Convert price to number
            price = float(price_text.replace('$', '').replace(',', ''))
            
            products[name] = price
            
        except:
            continue
    
    return products

def load_previous_prices():
    """Load yesterday's prices from file"""
    try:
        with open('price_history.csv', 'r') as file:
            reader = csv.DictReader(file)
            prices = {}
            for row in reader:
                if row['Date'] == datetime.now().strftime('%Y-%m-%d'):
                    prices[row['Product']] = float(row['Price'])
            return prices
    except:
        return {}

def save_prices(products):
    """Save prices to history file"""
    date = datetime.now().strftime('%Y-%m-%d')
    
    with open('price_history.csv', 'a', newline='') as file:
        writer = csv.writer(file)
        for name, price in products.items():
            writer.writerow([date, name, price])

def check_price_drops(current, previous):
    """Find products with price drops"""
    drops = []
    
    for product, current_price in current.items():
        if product in previous:
            old_price = previous[product]
            if current_price < old_price:
                drop_percent = ((old_price - current_price) / old_price) * 100
                drops.append({
                    'product': product,
                    'old_price': old_price,
                    'new_price': current_price,
                    'drop_percent': round(drop_percent, 2)
                })
    
    return drops

def send_email_alert(drops):
    """Send email with price drop alerts"""
    if not drops:
        print("No price drops to report")
        return
    
    # Create email
    msg = MIMEMultipart()
    msg['From'] = EMAIL_SENDER
    msg['To'] = EMAIL_RECEIVER
    msg['Subject'] = f"Price Drop Alert - {len(drops)} Products"
    
    # Email body
    body = "Price drops detected:\n\n"
    for drop in drops:
        body += f"📉 {drop['product']}\n"
        body += f"   Old: ${drop['old_price']:.2f}\n"
        body += f"   New: ${drop['new_price']:.2f}\n"
        body += f"   Drop: {drop['drop_percent']}%\n\n"
    
    msg.attach(MIMEText(body, 'plain'))
    
    # Send email (disabled for demo - would need real credentials)
    print("\n" + "="*50)
    print("EMAIL ALERT (Demo Mode)")
    print("="*50)
    print(body)
    print("="*50)
    print("In production, this would send an email to the client")
    print("="*50)
    
    # Uncomment when you have real email credentials:
    # server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
    # server.starttls()
    # server.login(EMAIL_SENDER, EMAIL_PASSWORD)
    # server.send_message(msg)
    # server.quit()

def daily_check():
    """Main function that runs daily"""
    print(f"\n{'='*50}")
    print(f"Running price check at {datetime.now()}")
    print(f"{'='*50}")
    
    # Get current prices
    current_prices = get_current_prices()
    print(f"Found {len(current_prices)} products")
    
    # Load previous prices
    previous_prices = load_previous_prices()
    
    # Check for drops
    drops = check_price_drops(current_prices, previous_prices)
    
    if drops:
        print(f"\n🚨 {len(drops)} price drops found!")
        send_email_alert(drops)
    else:
        print("\n✅ No price drops today")
    
    # Save current prices for tomorrow
    save_prices(current_prices)
    
    print(f"\nCheck complete. Next check in 24 hours.")

def run_once():
    """Run check once (for testing)"""
    daily_check()

def run_scheduled():
    """Run check daily at 9 AM"""
    schedule.every().day.at("09:00").do(daily_check)
    
    print("Price monitor started. Checking daily at 9:00 AM...")
    print("Press Ctrl+C to stop")
    
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute

# Choose how to run:
if __name__ == "__main__":
    # Option 1: Run once for testing
    run_once()
    
    # Option 2: Run daily (uncomment when ready)
    # run_scheduled()