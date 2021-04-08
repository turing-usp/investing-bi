import requests, csv

def get_wallet(google_sheet_key: str) -> list: 
    """Gets wallet from google public spreadsheet
    Args
    - google_sheet_key (str): key placed on the url of the spreadsheet
    Returns
    - (list<dict>): each item represents a position on the wallet and the dict keys are: date, securitie and quantity
    
    >>> get_wallet('1KHC1z4eO7CSekLK0ZaypIzrO5c5pVCq8Gx-hxL-sUaM')
    >>> [{'data': '04/01/2021', 'ativo': 'ITSA4', 'quantidade': '200'},
         {'data': '11/01/2021', 'ativo': 'OIBR3', 'quantidade': '1000'},
         {'data': '22/07/2020', 'ativo': 'BPAC11', 'quantidade': '500'}]
    """
    google_sheet_url = f"https://docs.google.com/spreadsheet/ccc?key={google_sheet_key}&output=csv"
    r = requests.get(google_sheet_url) 
    assert r.status_code == 200 
    decoded_content = r.content.decode('utf-8') 
    reader = csv.DictReader(decoded_content.splitlines(), delimiter=',')
    return [row for row in reader]
