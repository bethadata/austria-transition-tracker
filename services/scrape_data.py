from source import download_eurostat, download_econtrol

def scrape_all(): 
    download_eurostat.download_all()
    download_econtrol.download_el_mn()

if __name__ == "__main__": 
    scrape_all()


