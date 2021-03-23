import requests, csv

def getWallet(googleSheetKey: str = '1KHC1z4eO7CSekLK0ZaypIzrO5c5pVCq8Gx-hxL-sUaM') -> list: 
    """Gets wallet from google public spreadsheet
    Args
    - googleSheetKey (str): key placed on the url of the spreadsheet
    Returns
    - (list<dict>): each item represents a position on the wallet and the dict keys are: date, securitie and quantity
    """
    googleSheetUrl = f"https://docs.google.com/spreadsheet/ccc?key={googleSheetKey}&output=csv"
    r = requests.get(googleSheetUrl) 
    assert r.status_code == 200 
    decodedContent = r.content.decode('utf-8') 
    reader = csv.DictReader(decodedContent.splitlines(), delimiter=',')
    return [row for row in reader]
