from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from bs4 import BeautifulSoup
import pandas as pd
import time
import sys
import signal
from datetime import datetime


#PEMBATALAN CTRL+C
def signal_handler(sig, frame):
    print("\nAPA ADA ERROR CUY KENAPA GAK DI LANJUT 😒 BEK BEWWW msbrewwc.")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

# Fungsi untuk mengubah tanggal ke format "1 January 2023"
def format_date(date_str):
    months = {
        '01': 'January', '02': 'February', '03': 'March', '04': 'April',
        '05': 'May', '06': 'June', '07': 'July', '08': 'August',
        '09': 'September', '10': 'October', '11': 'November', '12': 'December'
    }
    date_obj = datetime.strptime(date_str, '%Y-%m-%d')
    return f"{date_obj.day} {months[date_obj.strftime('%m')]} {date_obj.year}"

# Fungsi untuk memilih browser
def choose_browser():
    choice = input("Pilih browser yang akan digunakan (chrome/firefox): ").strip().lower()
    if choice == 'chrome':
        chrome_options = ChromeOptions()
        chrome_options.add_argument("--ignore-certificate-errors")
        chrome_options.add_argument("--allow-running-insecure-content")
        chrome_options.add_argument("--disable-web-security")
        chrome_options.add_argument("--ignore-ssl-errors")

        driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=chrome_options)
        return driver

    elif choice == 'firefox':
        firefox_options = FirefoxOptions()
        firefox_options.add_argument("--ignore-certificate-errors")
        driver = webdriver.Firefox(service=FirefoxService(GeckoDriverManager().install()), options=firefox_options)
        return driver

    else:
        print("Pilihan tidak valid, menggunakan Chrome secara default.")
        return webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))


# Fungsi untuk scraping berdasarkan halaman
def scrape_news(category, start_date, end_date, start_page, end_page):
    # Pilih browser
    driver = choose_browser()

    # Format tanggal untuk URL
    formatted_start_date = format_date(start_date)
    formatted_end_date = format_date(end_date)

    # URL dasar untuk scraping
    base_url = f"https://radarkediri.jawapos.com/indeks-berita?daterange={formatted_start_date}%20-%20{formatted_end_date}"

    data = []  # List untuk menyimpan hasil scraping

    # Looping melalui halaman yang ditentukan oleh pengguna
    for page in range(start_page, end_page + 1):
        full_url = f"{base_url}&page={page}"
        print(f"Mengakses halaman: {full_url}")

        # Buka URL
        driver.get(full_url)
        driver.implicitly_wait(10)

        # Tunggu halaman termuat
        time.sleep(2)

        # Ambil konten halaman
        page_source = driver.page_source

        # Parse HTML menggunakan BeautifulSoup
        soup = BeautifulSoup(page_source, "html.parser")

        # Loop melalui setiap elemen berita yang ditemukan berdasarkan class tertentu
        articles = soup.find_all('div', class_='latest__item')

        if not articles:
            print(f"Tidak ada artikel yang ditemukan di halaman {page}.")
            break

        for article in articles:
            try:
                # Kategori berita (diambil dari teks di dalam tag <h4> dengan class "latest__subtitle")
                category_tag = article.find('h4', class_='latest__subtitle')
                article_category = category_tag.get_text(strip=True) if category_tag else "Tidak ada kategori"

                # Hanya menyimpan berita jika kategori sesuai
                if category.lower() in article_category.lower():
                    # Judul berita
                    title_tag = article.find('h2', class_='latest__title')
                    title = title_tag.get_text(strip=True) if title_tag else "Tidak ada judul"

                    # Link berita
                    link_tag = title_tag.find('a', class_='latest__link') if title_tag else None
                    link = link_tag['href'] if link_tag else "Tidak ada link"

                    # Tanggal dan waktu berita
                    date_tag = article.find('date', class_='latest__date')
                    date_time = date_tag.get_text(strip=True) if date_tag else "Tidak ada tanggal"

                    # Menambahkan data ke list
                    data.append({
                        "Tanggal Berita": date_time,
                        "Judul Berita": title,
                        "Alamat URL": link,
                        "Kategori": article_category
                    })

            except Exception as e:
                print(f"Terjadi kesalahan: {e}")

        print(f"Scraping halaman {page} selesai.")

    # Tutup browser setelah selesai
    driver.quit()

    return data

# Fungsi untuk menyimpan data ke Excel
def save_to_excel(data):
    # Tanya nama file kepada pengguna
    filename = input("Masukkan nama file (contoh: hasil_no1): ").strip() + ".xlsx"
    save_path = "Hasil_Scraper/" + filename
    
    # Simpan ke Excel
    df = pd.DataFrame(data)
    df.to_excel(save_path, index=False)

    print(f"Scraping selesai! Data telah disimpan di file {save_path}")

# Input dari pengguna untuk kategori, tanggal, dan rentang halaman
tanggal_mulai = input("Masukkan tanggal mulai (format: YYYY-MM-DD): ").strip()
tanggal_akhir = input("Masukkan tanggal akhir (format: YYYY-MM-DD): ").strip()
start_page = int(input("Masukkan halaman mulai: ").strip())
end_page = int(input("Masukkan halaman akhir: ").strip())

# Kategori secara manual, seperti 'nganjuk', 'kediri'
kategori = input("Masukkan kategori berita (contoh: nganjuk, kediri): ").strip()

# Scrape berdasarkan input
data = scrape_news(kategori, tanggal_mulai, tanggal_akhir, start_page, end_page)

# Simpan hasil ke dalam Excel
save_to_excel(data)
