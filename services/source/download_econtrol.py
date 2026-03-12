import requests
from config import BASEPATH 
from loguru import logger 


def download_el_mn(): 
    url = "https://www.e-control.at/documents/1785851/8165594/el_dataset_mn.csv"
    output_file = BASEPATH + "/services/data_raw/e_control/el_dataset_mn.csv"

    response = requests.get(url)

    if response.status_code == 200:
        with open(output_file, "wb") as f:
            f.write(response.content)
        logger.info("Econtrol download successful")
    else:
        logger.warn("Econtrol download failed: %s", response.status_code)