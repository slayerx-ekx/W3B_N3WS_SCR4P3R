import sys
import signal
import time
from datetime import datetime
import pandas as pd
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from bs4 import BeautifulSoup

# Signal handler for CTRL+C
def signal_handler(sig, frame):
    print("\nAPA ADA ERROR CUY KENAPA GAK DI LANJUT 😒 BEK BEWWW msbrewwc.")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

# Function to format date
def format_date(date_str):
    months = {
        '01': 'January', '02': 'February', '03': 'March', '04': 'April',
        '05': 'May', '06': 'June', '07': 'July', '08': 'August',
        '09': 'September', '10': 'October', '11': 'November', '12': 'December'
    }
    date_obj = datetime.strptime(date_str, '%Y-%m-%d')
    return f"{date_obj.day} {months[date_obj.strftime('%m')]} {date_obj.year}"

# Function to choose browser
def choose_browser():
    print("Pilih browser yang akan digunakan:")
    print("1. Chrome")
    print("2. Firefox")
    print("3. Edge")
    choice = input("Masukkan pilihan (1/2/3): ").strip()
    
    if choice == "1":
        print("Menggunakan Chrome...")
        chrome_options = ChromeOptions()
        chrome_options.add_argument("--ignore-certificate-errors")
        chrome_options.add_argument("--allow-running-insecure-content")
        chrome_options.add_argument("--disable-web-security")
        chrome_options.add_argument("--ignore-ssl-errors")
        return webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=chrome_options)
    elif choice == "2":
        print("Menggunakan Firefox...")
        firefox_options = FirefoxOptions()
        firefox_options.add_argument("--ignore-certificate-errors")
        return webdriver.Firefox(service=FirefoxService(GeckoDriverManager().install()), options=firefox_options)
    elif choice == "3":
        print("Menggunakan Edge...")
        return webdriver.Edge(service=EdgeService(EdgeChromiumDriverManager().install()))
    else:
        print("Pilihan tidak valid! Menggunakan Chrome secara default.")
        return webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))

# Function to scroll to bottom
def scroll_to_bottom(driver, scroll_pause_time=2):
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(scroll_pause_time)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            print("Sudah mencapai bagian bawah halaman.")
            break
        last_height = new_height

# Function to scrape Jawa Pos news
def scrape_jawapos_news(category, start_date, end_date, start_page, end_page, driver):
    formatted_start_date = format_date(start_date)
    formatted_end_date = format_date(end_date)
    base_url = f"https://radarkediri.jawapos.com/indeks-berita?daterange={formatted_start_date}%20-%20{formatted_end_date}"
    data = []

    for page in range(start_page, end_page + 1):
        full_url = f"{base_url}&page={page}"
        print(f"Mengakses halaman: {full_url}")
        driver.get(full_url)
        driver.implicitly_wait(10)
        time.sleep(2)
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, "html.parser")
        articles = soup.find_all('div', class_='latest__item')

        if not articles:
            print(f"Tidak ada artikel yang ditemukan di halaman {page}.")
            break

        for article in articles:
            try:
                category_tag = article.find('h4', class_='latest__subtitle')
                article_category = category_tag.get_text(strip=True) if category_tag else "Tidak ada kategori"
                if category.lower() in article_category.lower():
                    title_tag = article.find('h2', class_='latest__title')
                    title = title_tag.get_text(strip=True) if title_tag else "Tidak ada judul"
                    link_tag = title_tag.find('a', class_='latest__link') if title_tag else None
                    link = link_tag['href'] if link_tag else "Tidak ada link"
                    date_tag = article.find('date', class_='latest__date')
                    date_time = date_tag.get_text(strip=True) if date_tag else "Tidak ada tanggal"
                    data.append({
                        "Tanggal Berita": date_time,
                        "Judul Berita": title,
                        "Alamat URL": link,
                        "Kategori": article_category
                    })
            except Exception as e:
                print(f"Terjadi kesalahan: {e}")
        print(f"Scraping halaman {page} selesai.")
    return data

# Function to scrape Tribun news
def scrape_tribun_news(url, driver):
    driver.get(url)
    time.sleep(3)
    scroll_to_bottom(driver)
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, "html.parser")
    data = []
    articles = soup.find_all('li', class_='p1520 art-list pos_rel')
    for article in articles:
        try:
            title_tag = article.find('a', class_='f20 ln24 fbo txt-oev-2')
            title = title_tag.get_text(strip=True) if title_tag else "Tidak ada judul"
            link = title_tag['href'] if title_tag else "Tidak ada link"
            time_tag = article.find('time', class_='foot timeago')
            date_time = time_tag['title'] if time_tag else "Tidak ada tanggal"
            data.append({
                "Tanggal Berita": date_time,
                "Judul Berita": title,
                "Link Berita": link
            })
        except Exception as e:
            print(f"Terjadi kesalahan saat mengambil data artikel: {e}")
    return data

# Function to save data to Excel
def save_to_excel(data):
    filename = input("Masukkan nama file (contoh: hasil_no1): ").strip() + ".xlsx"
    save_path = "Hasil_Scraper/" + filename
    df = pd.DataFrame(data)
    df.to_excel(save_path, index=False)
    print(f"Scraping selesai! Data telah disimpan di file {save_path}")

# Function to display banner
def display_banner():
    banner = """
    ██╗    ██╗██████╗ ██████╗         ███╗   ██╗██████╗ ██╗    ██╗███████╗        ███████╗ ██████╗██████╗ ██╗  ██╗██████╗ ██████╗ ██████╗ 
    ██║    ██║╚════██╗██╔══██╗        ████╗  ██║╚════██╗██║    ██║██╔════╝        ██╔════╝██╔════╝██╔══██╗██║  ██║██╔══██╗╚════██╗██╔══██╗
    ██║ █╗ ██║ █████╔╝██████╔╝        ██╔██╗ ██║ █████╔╝██║ █╗ ██║███████╗        ███████╗██║     ██████╔╝███████║██████╔╝ █████╔╝██████╔╝
    ██║███╗██║ ╚═══██╗██╔══██╗        ██║╚██╗██║ ╚═══██╗██║███╗██║╚════██║        ╚════██║██║     ██╔══██╗╚════██║██╔═══╝  ╚═══██╗██╔══██╗
    ╚███╔███╔╝██████╔╝██████╔╝███████╗██║ ╚████║██████╔╝╚███╔███╔╝███████║███████╗███████║╚██████╗██║  ██║     ██║██║     ██████╔╝██║  ██║
     ╚══╝╚══╝ ╚═════╝ ╚═════╝ ╚══════╝╚═╝  ╚═══╝╚═════╝  ╚══╝╚══╝ ╚══════╝╚══════╝╚══════╝ ╚═════╝╚═╝  ╚═╝     ╚═╝╚═╝     ╚═════╝ ╚═╝  ╚═╝
    """
    print(banner)

# Function to display Tribun options
def display_tribun_options():
    line = "+" + "-" * 22 + "+" + "-" * 22 + "+"
    
    print("=" * 50)
    print("| Kategori Website Tribun Jatim                     |")
    print("=" * 50)
    
    # PEMILU
    print(line)
    print(f"| {'PEMILU':<21} |{'':<21}|")
    print(line)
    print(f"| {'1. Pemili-Legislatif':<21} |{'':<21}|")
    print(f"| {'2. Pilpres':<21} |{'':<21}|")
    print(f"| {'3. Pilkada':<21} |{'':<21}|")
    print(line)
    
    # TRAVEL
    print(f"| {'TRAVEL':<21} |{'':<21}|")
    print(line)
    print(f"| {'4. Akomodasi':<21} |{'5. Shopping':<21} |")
    print(f"| {'6. Kuliner':<21} |{'7. Ticketing':<21} |")
    print(f"| {'8. Destinasi':<21} |{'':<21}|")
    print(line)

    # WILAYAH
    print(f"| {'WILAYAH':<21} |{'':<21}|")
    print(line)
    print(f"| {'9. Jatim':<21} |{'10. Gresik':<21} |")
    print(f"| {'11. Surabaya':<21} |{'12. Jember':<21} |")
    print(f"| {'13. Malang':<21} |{'14. Blitar':<21} |")
    print(f"| {'15. Banyuwangi':<21} |{'16. Kediri':<21} |")
    print(f"| {'17. Trenggalek':<21} |{'18. Madiun':<21} |")
    print(f"| {'19. Bojonegoro':<21} |{'20. Madura':<21} |")
    print(f"| {'21. Batu':<21} |{'22. Nganjuk':<21} |")
    print(f"| {'23. Mojokerto':<21} |{'24. Probolinggo':<21} |")
    print(f"| {'25. Pasuruan':<21} |{'':<21}|")
    print(line)
    
    # LAIN LAIN
    print(f"| {'LAIN LAIN':<21} |{'':<21}|")
    print(line)
    print(f"| {'26. Bisnis':<21} |{'27. Otomotif':<21} |")
    print(f"| {'28. Sport':<21} |{'29. Lifestyle':<21} |")
    print(f"| {'30. Pemilu':<21} |{'31. Seleb':<21} |")
    print(f"| {'32. Techno':<21} |{'33. Bola-Jatim':<21} |")
    print(f"| {'34. Kesehatan':<21} |{'35. News':<21} |")
    print(line)
    
    print("=" * 50)

# Main function
def main():
    display_banner()
    print("\nPilih website yang ingin di-scrape:")
    print("1. Tribun Jatim")
    print("2. Jawa Pos")
    
    website_choice = input("Masukkan pilihan (1/2): ").strip()
    
    # Inisialisasi driver di awal sebelum memulai scraping
    driver = choose_browser()
    
    
    if website_choice == "1":
        display_tribun_options()
        choice = input("Masukkan pilihan (Example : 1 / 2 / 3 / etc): ")
        options = {
            #PEMILU
            "1": "https://jatim.tribunnews.com/mata-lokal-memilih/pemilu-legislatif",
            "2": "https://jatim.tribunnews.com/mata-lokal-memilih/pilpres",
            "3": "https://jatim.tribunnews.com/mata-lokal-memilih/pilkada",
            #TRAVEL
            "4": "https://jatim.tribunnews.com/travel/akomodasi",
            "5": "https://jatim.tribunnews.com/travel/shopping",
            "6": "https://jatim.tribunnews.com/travel/kuliner",
            "7": "https://jatim.tribunnews.com/travel/ticketing",
            "8": "https://jatim.tribunnews.com/travel/destinasi",
            #WILAYAH
            "9": "https://jatim.tribunnews.com/jatim",
            "10": "https://jatim.tribunnews.com/gresik",
            "11": "https://jatim.tribunnews.com/surabaya",
            "12": "https://jatim.tribunnews.com/jember",
            "13": "https://jatim.tribunnews.com/malang",
            "14": "https://jatim.tribunnews.com/blitar",
            "15": "https://jatim.tribunnews.com/banyuwangi",
            "16": "https://jatim.tribunnews.com/kediri",
            "17": "https://jatim.tribunnews.com/trenggalek",
            "18": "https://jatim.tribunnews.com/madiun",
            "19": "https://jatim.tribunnews.com/bojonegoro",
            "20": "https://jatim.tribunnews.com/madura",
            "21": "https://jatim.tribunnews.com/batu",
            "22": "https://jatim.tribunnews.com/nganjuk",
            "23": "https://jatim.tribunnews.com/mojokerto",
            "24": "https://jatim.tribunnews.com/probolinggo",
            "25": "https://jatim.tribunnews.com/pasuruan",
            #LAIN-LAIN
            "26": "https://jatim.tribunnews.com/bisnis",
            "27": "https://jatim.tribunnews.com/otomotif",
            "28": "https://jatim.tribunnews.com/sport",
            "29": "https://jatim.tribunnews.com/lifestyle",
            "30": "https://jatim.tribunnews.com/pemilu",
            "31": "https://jatim.tribunnews.com/seleb",
            "32": "https://jatim.tribunnews.com/techno",
            "33": "https://jatim.tribunnews.com/bola-jatim",
            "34": "https://jatim.tribunnews.com/kesehatan",
            "35": "https://jatim.tribunnews.com/news"
        }
        url = options.get(choice, None)
        if url:
            data = scrape_tribun_news(url, driver)
            save_to_excel(data)
        else:
            print("Pilihan tidak valid!")
    elif website_choice == "2":
        category = input("Masukkan kategori berita: ").strip()
        start_date = input("Masukkan tanggal mulai (YYYY-MM-DD): ").strip()
        end_date = input("Masukkan tanggal akhir (YYYY-MM-DD): ").strip()
        start_page = int(input("Masukkan halaman mulai: ").strip())
        end_page = int(input("Masukkan halaman akhir: ").strip())
        data = scrape_jawapos_news(category, start_date, end_date, start_page, end_page, driver)
        save_to_excel(data)
    else:
        print("Pilihan tidak valid!")

    
    driver.quit()

if __name__ == "__main__":
    main()
