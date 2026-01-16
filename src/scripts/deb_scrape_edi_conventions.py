import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import json
import csv

def scrape_edi_conventions(url):
    """
    Scrape EDI conventions and their PDF links from USTRANSCOM page.
    
    Args:
        url: The webpage URL to scrape
    """
    print(f"Fetching page: {url}")
    
    # Get the webpage
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    # Disable SSL verification for this government site
    response = requests.get(url, headers=headers, verify=False)
    response.raise_for_status()
    
    # Suppress only the InsecureRequestWarning from urllib3
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    # Parse HTML
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Find all links that point to PDFs
    edi_conventions = []
    
    links = soup.find_all('a', href=True)
    
    for link in links:
        href = link['href']
        if href.lower().endswith('.pdf'):
            # Get the link text (convention name)
            text = link.get_text(strip=True)
            
            # Convert relative URLs to absolute
            full_url = urljoin(url, href)
            
            # Store the convention info
            edi_conventions.append({
                'convention_name': text,
                'pdf_url': full_url
            })
    
    print(f"\nFound {len(edi_conventions)} EDI convention(s) with PDF links:\n")
    
    # Display the results
    for i, conv in enumerate(edi_conventions, 1):
        print(f"{i}. {conv['convention_name']}")
        print(f"   URL: {conv['pdf_url']}\n")
    
    # Save to JSON file
    with open('edi_conventions.json', 'w', encoding='utf-8') as f:
        json.dump(edi_conventions, f, indent=2, ensure_ascii=False)
    print("✓ Saved to: edi_conventions.json")
    
    # Save to CSV file
    with open('edi_conventions.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['convention_name', 'pdf_url'])
        writer.writeheader()
        writer.writerows(edi_conventions)
    print("✓ Saved to: edi_conventions.csv")
    
    # Save to text file
    with open('edi_conventions.txt', 'w', encoding='utf-8') as f:
        for conv in edi_conventions:
            f.write(f"{conv['convention_name']}\n")
            f.write(f"{conv['pdf_url']}\n\n")
    print("✓ Saved to: edi_conventions.txt")
    
    return edi_conventions

if __name__ == "__main__":
    # USTRANSCOM URL
    url = "https://www.ustranscom.mil/cmd/associated/dteb/dod-transportation.cfm"
    
    try:
        conventions = scrape_edi_conventions(url)
        
        print(f"\n{'='*60}")
        print(f"Total EDI conventions extracted: {len(conventions)}")
        print(f"{'='*60}")
        
    except requests.exceptions.RequestException as e:
        print(f"Error accessing webpage: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")
