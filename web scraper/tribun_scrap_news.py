from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.edge.service import Service as EdgeService
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from bs4 import BeautifulSoup
import pandas as pd
import os
import time
import signal
import sys

#LOHHHHH LOLE LOLE LOLE LOLE
def signal_handler(sig, frame):
    print("\nAPA ADA ERROR CUY KENAPA GAK DI LANJUT 😒 BEK BEWWW msbrewwc.")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

def scroll_to_bottom(driver, scroll_pause_time=2):
    """Scroll halaman sampai ke bawah beberapa kali untuk memuat semua berita."""
    last_height = driver.execute_script("return document.body.scrollHeight")
    
    while True:
        # Scroll ke bawah
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        # Tunggu agar halaman dapat memuat konten baru
        time.sleep(scroll_pause_time)

        # Hitung tinggi halaman setelah scroll
        new_height = driver.execute_script("return document.body.scrollHeight")

        # Jika tidak ada lagi penambahan konten (tinggi halaman tidak berubah), keluar dari loop
        if new_height == last_height:
            print("Sudah mencapai bagian bawah halaman.")
            break

        last_height = new_height

def choose_browser():
    print("Pilih browser yang ingin digunakan untuk scraping:")
    print("1. Chrome")
    print("2. Firefox")
    print("3. Edge")

    choice = input("Masukkan pilihan (1/2/3): ").strip()

    if choice == "1":
        print("Menggunakan Chrome...")
        driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
    elif choice == "2":
        print("Menggunakan Firefox...")
        driver = webdriver.Firefox(service=FirefoxService(GeckoDriverManager().install()))
    elif choice == "3":
        print("Menggunakan Edge...")
        driver = webdriver.Edge(service=EdgeService(EdgeChromiumDriverManager().install()))
    else:
        print("Pilihan tidak valid! Menggunakan Chrome secara default.")
        driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))

    return driver

#SCROLL TERUS UNTIL SHOW MORE BOTTON
"""
def scroll_to_bottom(driver, scroll_pause_time=2):
    last_height = driver.execute_script("return document.body.scrollHeight")
    last_data_sort = 0  # Simpan nilai terakhir dari 'data-sort', diinisialisasi dengan 0

    while True:
        # Scroll ke bagian bawah halaman
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(scroll_pause_time)

        # Ambil tinggi halaman setelah scroll
        new_height = driver.execute_script("return document.body.scrollHeight")

        # Jika tinggi halaman tidak berubah, berarti sudah mencapai bagian bawah
        if new_height == last_height:
            print("Sudah mencapai bagian bawah halaman.")

            try:
                # Cari tombol 'Show more' berdasarkan id atau class
                load_more_button = driver.find_element(By.ID, "ltldmr")
                
                # Tanya apakah mau memanggil loadmore() setelah scroll habis
                user_input = input("Tombol 'Show more' ditemukan. Apakah Anda ingin memanggil fungsi 'loadmore()' untuk memuat lebih banyak konten (y/n)? ")
                if user_input.lower() == 'y':
                    # Panggil fungsi loadmore untuk memuat konten lebih banyak
                    driver.execute_script("loadmore()")
                    print("Fungsi 'loadmore()' dipanggil untuk memuat lebih banyak konten.")
                    time.sleep(scroll_pause_time)  # Tunggu setelah loadmore() dipanggil untuk memuat konten baru
                    
                    # Ambil data-sort terbesar yang ada saat ini
                    new_data_sort = driver.execute_script(
                        var items = document.querySelectorAll("li.p1520.art-list.pos_rel");
                        var maxSort = Math.max.apply(null, Array.from(items).map(item => parseInt(item.getAttribute('data-sort') || 0)));
                        return maxSort;)

                    # Pastikan new_data_sort tidak bernilai None
                    if new_data_sort is not None and new_data_sort > last_data_sort:
                        print(f"Konten baru berhasil dimuat, data-sort meningkat dari {last_data_sort} ke {new_data_sort}.")
                        last_data_sort = new_data_sort
                    else:
                        print("Tidak ada konten baru yang dimuat setelah loadmore().")
                        break  # Jika tidak ada konten baru, keluar dari loop
                else:
                    print("Proses dihentikan sesuai permintaan.")
                    break
            except Exception as e:
                print(f"Tidak dapat memanggil 'loadmore()' atau terjadi kesalahan: {e}")
            
        # Jika tinggi halaman berubah, lanjutkan scroll
        if new_height != last_height:
            last_height = new_height
        else:
            break  # Berhenti jika halaman tidak lagi berubah
"""
            
def scrape_news(url, driver):
    #driver = webdriver.Firefox(service=FirefoxService(GeckoDriverManager().install()))  
    driver.get(url)
    time.sleep(3)
    scroll_to_bottom(driver)

    page_source = driver.page_source  # AMBIL KONTEN
    soup = BeautifulSoup(page_source, "html.parser")
    data = []

    articles = soup.find_all('li', class_='p1520 art-list pos_rel')  # CARI DATA
    for article in articles:
        try:
            # Cari elemen judul
            title_tag = article.find('a', class_='f20 ln24 fbo txt-oev-2')
            title = title_tag.get_text(strip=True) if title_tag else "Tidak ada judul"

            # Cari elemen link
            link = title_tag['href'] if title_tag else "Tidak ada link"

            # Cari elemen tanggal
            time_tag = article.find('time', class_='foot timeago')  
            date_time = time_tag['title'] if time_tag else "Tidak ada tanggal"

            # Tambahkan data ke list
            data.append({
                "Tanggal Berita": date_time,
                "Judul Berita": title,
                "Link Berita": link
            })

        except Exception as e:
            print(f"Terjadi kesalahan saat mengambil data artikel: {e}")

    driver.quit()

    return data

# SAVE DATA KE EXCEL
def save_to_excel(data, filename="nganjuk_news.xlsx"):
    save_folder = "Hasil_Scraper"
    if not os.path.exists(save_folder):
        os.makedirs(save_folder)

    save_path = os.path.join(save_folder, filename)

    df = pd.DataFrame(data)
    df.to_excel(save_path, index=False)

    print(f"Scraping selesai! Data telah disimpan di file {save_path}")

# AWALAN INTRO DLL
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
"""
def save_to_excel(data, filename):
    # Simulasi penyimpanan ke Excel
    print(f"Menyimpan data ke {filename}...")
"""
def display_options():
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

def main():
    display_banner()
    input("\nTekan Enter untuk melanjutkan...")

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

    display_options()

    choice = input("Masukkan pilihan (Example : 1 / 2 / 3 / etc): ")
    url = options.get(choice)

    if not url:
        print("Pilihan tidak valid!")
        return

    driver = choose_browser()

    data = scrape_news(url, driver)

    if data:
        filename = input("Masukkan nama file (contoh: hasil_no1): ").strip() + ".xlsx"
        save_path = "Hasil_Scraper/" + filename
        df = pd.DataFrame(data)
        df.to_excel(save_path, index=False)

        print(f"Scraping selesai! Data telah disimpan di file {save_path}")
    else:
        print("YAHHH GAK ADA DATA NIH MAAF YA HEHEH 😊.")

if __name__ == "__main__":
    main()
