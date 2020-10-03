import requests


def library_lol_scraper(response_body: str) -> tuple:
    download_link = response_body.xpath('/html/body/table/tbody/tr/td[2]/h2/a')

    file_content = requests.get(download_link, allow_redirects=True)
    file_name = file_body.headers.get('content-disposition')

    return file_name, file_body


def libgen_lc_scraper(response_body: str) -> tuple:
    download_link = response_body.xpath('/html/body/table/tbody/tr[1]/td[2]/a')
    
    file_content = requests.get(download_link, allow_redirects=True)
    file_name = file_content.headers.get('content-disposition')

    return file_name, file_content


def bookfi_net_scraper(response_body: str) -> tuple:
    download_link = response_body.xpath('/html/body/table/tbody/tr[2]/td/center/div/div[2]/div/div[2]/div/div[1]/div[2]/div[1]/a[1]')
    
    file_content = requests.get(download_link, allow_redirects=True)
    file_name = file_content.headers.get('content-disposition')

    return file_name, file_content
