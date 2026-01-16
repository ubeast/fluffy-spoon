import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from pathlib import Path
import time
import urllib3

# Suppress SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def scrape_and_download_dla_pdfs(url):
    """
    Scrape DLA EDI Implementation Conventions and download all PDF files.
    
    Args:
        url: The DLA webpage URL to scrape
    """
    print(f"Fetching page: {url}")
    print("="*60)
    
    # Get the webpage
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    # Disable SSL verification for government sites
    response = requests.get(url, headers=headers, verify=False)
    response.raise_for_status()
    
    # Parse HTML
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Find all PDF links
    pdf_files = []
    
    # Find all table rows
    table_rows = soup.find_all('tr')
    
    for row in table_rows:
        cells = row.find_all('td')
        
        # Skip header rows or empty rows
        if len(cells) < 5:
            continue
        
        # Extract IC detail and title
        ic_detail = cells[1].get_text(strip=True) if len(cells) > 1 else ""
        title = cells[4].get_text(strip=True) if len(cells) > 4 else ""
        
        # Find PDF link
        pdf_link_cell = cells[5] if len(cells) > 5 else None
        
        if pdf_link_cell:
            pdf_anchor = pdf_link_cell.find('a', href=True)
            if pdf_anchor and pdf_anchor['href'].lower().endswith('.pdf'):
                href = pdf_anchor['href']
                
                # Build the full URL
                if href.startswith('/'):
                    pdf_url = 'https://www.dla.mil' + href
                elif href.startswith('http'):
                    pdf_url = href
                else:
                    pdf_url = urljoin(url, href)
                
                # Extract filename from URL
                filename = Path(href).name
                
                pdf_files.append({
                    'ic_detail': ic_detail,
                    'title': title,
                    'url': pdf_url,
                    'filename': filename
                })
    
    print(f"Found {len(pdf_files)} PDF file(s) to download\n")
    
    if not pdf_files:
        print("No PDF files found on this page.")
        return
    
    # Create download directory
    download_dir = Path("dla_edi_pdfs")
    download_dir.mkdir(exist_ok=True)
    
    # Download each PDF
    successful = 0
    failed = 0
    
    for i, pdf in enumerate(pdf_files, 1):
        print(f"[{i}/{len(pdf_files)}] {pdf['ic_detail']} - {pdf['title']}")
        print(f"  URL: {pdf['url']}")
        
        try:
            # Download the PDF
            pdf_response = requests.get(pdf['url'], headers=headers, verify=False, timeout=30)
            pdf_response.raise_for_status()
            
            # Save the file
            output_path = download_dir / pdf['filename']
            with open(output_path, 'wb') as f:
                f.write(pdf_response.content)
            
            file_size = len(pdf_response.content) / 1024  # KB
            print(f"  ✓ Saved: {output_path} ({file_size:.1f} KB)")
            successful += 1
            
            # Be nice to the server
            time.sleep(0.5)
            
        except requests.exceptions.HTTPError as e:
            print(f"  ✗ HTTP Error: {e}")
            failed += 1
        except Exception as e:
            print(f"  ✗ Error: {e}")
            failed += 1
        
        print()
    
    # Summary
    print("="*60)
    print(f"Download Summary:")
    print(f"  Total files: {len(pdf_files)}")
    print(f"  Successful: {successful}")
    print(f"  Failed: {failed}")
    print(f"  Download directory: {download_dir.absolute()}")
    print("="*60)

if __name__ == "__main__":
    # DLA Implementation Conventions URL
    dla_url = "https://www.dla.mil/Defense-Data-Standards/Resources/Implementation-Conventions/"
    
    try:
        scrape_and_download_dla_pdfs(dla_url)
        
    except requests.exceptions.RequestException as e:
        print(f"Error accessing webpage: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")
        import traceback
        traceback.print_exc()
