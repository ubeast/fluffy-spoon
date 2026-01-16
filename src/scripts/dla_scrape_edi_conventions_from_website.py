import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import json
import csv
import urllib3

# Suppress SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def scrape_dla_edi_conventions(url):
    """
    Scrape DLA EDI Implementation Conventions from the table.
    
    Args:
        url: The DLA webpage URL to scrape
    """
    print(f"Fetching page: {url}")
    
    # Get the webpage
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    # Disable SSL verification for government sites
    response = requests.get(url, headers=headers, verify=False)
    response.raise_for_status()
    
    # Parse HTML
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Find the table with EDI conventions
    edi_conventions = []
    
    # Find all table rows (the data is in a table)
    table_rows = soup.find_all('tr')
    
    for row in table_rows:
        cells = row.find_all('td')
        
        # Skip header rows or empty rows
        if len(cells) < 5:
            continue
        
        # Extract data from cells
        # Typical structure: IC Detail | X12 Version | Recent ADC | Title | DLMS X12 IC | DLMS XML Schema
        ic_detail = cells[1].get_text(strip=True) if len(cells) > 1 else ""
        x12_version = cells[2].get_text(strip=True) if len(cells) > 2 else ""
        title = cells[4].get_text(strip=True) if len(cells) > 4 else ""
        
        # Find PDF link in the DLMS X12 IC column
        pdf_link_cell = cells[5] if len(cells) > 5 else None
        pdf_url = ""
        pdf_date = ""
        
        if pdf_link_cell:
            pdf_anchor = pdf_link_cell.find('a', href=True)
            if pdf_anchor and pdf_anchor['href'].lower().endswith('.pdf'):
                # Build the full URL - DLA uses absolute paths starting with /Portals
                href = pdf_anchor['href']
                if href.startswith('/'):
                    pdf_url = 'https://www.dla.mil' + href
                elif href.startswith('http'):
                    pdf_url = href
                else:
                    pdf_url = urljoin(url, href)
                pdf_date = pdf_anchor.get_text(strip=True)
        
        # Find XML link in the DLMS XML Schema column
        xml_link_cell = cells[6] if len(cells) > 6 else None
        xml_url = ""
        
        if xml_link_cell:
            xml_anchor = xml_link_cell.find('a', href=True)
            if xml_anchor:
                href = xml_anchor['href']
                # XML links might be on intelshare or dla.mil
                if href.startswith('http'):
                    xml_url = href
                elif href.startswith('/'):
                    xml_url = 'https://www.dla.mil' + href
                else:
                    xml_url = urljoin(url, href)
        
        # Only add if we have valid data
        if ic_detail and title:
            edi_conventions.append({
                'ic_detail': ic_detail,
                'x12_version': x12_version,
                'title': title,
                'pdf_url': pdf_url,
                'pdf_date': pdf_date,
                'xml_url': xml_url
            })
    
    print(f"\nFound {len(edi_conventions)} EDI convention(s):\n")
    
    # Display the results
    for i, conv in enumerate(edi_conventions, 1):
        print(f"{i}. {conv['ic_detail']} - {conv['title']}")
        print(f"   X12 Version: {conv['x12_version']}")
        print(f"   PDF: {conv['pdf_url']}")
        if conv['xml_url']:
            if 'intelshare.intelink.gov' in conv['xml_url']:
                print(f"   XML: {conv['xml_url']} [REQUIRES INTELINK ACCESS]")
            else:
                print(f"   XML: {conv['xml_url']}")
        print()
    
    # Save to JSON file
    json_file = 'dla_edi_conventions.json'
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(edi_conventions, f, indent=2, ensure_ascii=False)
    print(f"✓ Saved to: {json_file}")
    
    # Save to CSV file
    csv_file = 'dla_edi_conventions.csv'
    with open(csv_file, 'w', newline='', encoding='utf-8') as f:
        fieldnames = ['ic_detail', 'x12_version', 'title', 'pdf_url', 'pdf_date', 'xml_url']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(edi_conventions)
    print(f"✓ Saved to: {csv_file}")
    
    # Save to text file
    txt_file = 'dla_edi_conventions.txt'
    with open(txt_file, 'w', encoding='utf-8') as f:
        for conv in edi_conventions:
            f.write(f"IC: {conv['ic_detail']} - {conv['title']}\n")
            f.write(f"X12 Version: {conv['x12_version']}\n")
            f.write(f"PDF URL: {conv['pdf_url']}\n")
            if conv['xml_url']:
                f.write(f"XML URL: {conv['xml_url']}\n")
            f.write("\n")
    print(f"✓ Saved to: {txt_file}")
    
    return edi_conventions

if __name__ == "__main__":
    # DLA Implementation Conventions URL
    dla_url = "https://www.dla.mil/Defense-Data-Standards/Resources/Implementation-Conventions/"
    
    try:
        conventions = scrape_dla_edi_conventions(dla_url)
        
        print(f"{'='*60}")
        print(f"Total EDI conventions extracted: {len(conventions)}")
        print(f"{'='*60}")
        print("\nNOTE: XML files on intelshare.intelink.gov require:")
        print("  - Valid security clearance")
        print("  - Access to Intelink network")
        print("  - Government authentication credentials")
        print("\nPDF files on dla.mil are publicly accessible.")
        print(f"{'='*60}")
        
    except requests.exceptions.RequestException as e:
        print(f"Error accessing webpage: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")
        import traceback
        traceback.print_exc()
