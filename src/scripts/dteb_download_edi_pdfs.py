import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from pathlib import Path
import time
import urllib3

# Suppress SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def scrape_and_download_pdfs(url, output_dir):
    """
    Scrape a webpage and download all PDF files.
    
    Args:
        url: The webpage URL to scrape
        output_dir: Directory name to save PDFs
    """
    print(f"Fetching page: {url}")
    print("="*60)
    
    # Get the webpage
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    # Disable SSL verification for government sites
    response = requests.get(url, headers=headers, verify=False, timeout=30)
    response.raise_for_status()
    
    # Parse HTML
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Find all links that point to PDFs
    pdf_files = []
    
    links = soup.find_all('a', href=True)
    
    for link in links:
        href = link['href']
        if href.lower().endswith('.pdf'):
            # Get the link text (convention name/description)
            text = link.get_text(strip=True)
            
            # Build the full URL
            if href.startswith('/'):
                # Extract domain from original URL
                from urllib.parse import urlparse
                parsed = urlparse(url)
                pdf_url = f"{parsed.scheme}://{parsed.netloc}{href}"
            elif href.startswith('http'):
                pdf_url = href
            else:
                pdf_url = urljoin(url, href)
            
            # Extract filename from URL
            filename = Path(href).name
            
            pdf_files.append({
                'name': text if text else filename,
                'url': pdf_url,
                'filename': filename
            })
    
    print(f"Found {len(pdf_files)} PDF file(s) to download\n")
    
    if not pdf_files:
        print("No PDF files found on this page.")
        return []
    
    # Create download directory
    download_dir = Path(output_dir)
    download_dir.mkdir(exist_ok=True)
    
    # Download each PDF
    successful = 0
    failed = 0
    
    for i, pdf in enumerate(pdf_files, 1):
        print(f"[{i}/{len(pdf_files)}] {pdf['name']}")
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
    
    return pdf_files

if __name__ == "__main__":
    # USTRANSCOM URL
    ustranscom_url = "https://www.ustranscom.mil/cmd/associated/dteb/dod-transportation.cfm"
    
    # DLA URL (commented out - uncomment to download DLA PDFs)
    # dla_url = "https://www.dla.mil/Defense-Data-Standards/Resources/Implementation-Conventions/"
    
    try:
        print("\n*** Downloading USTRANSCOM EDI Convention PDFs ***\n")
        ustranscom_pdfs = scrape_and_download_pdfs(ustranscom_url, "ustranscom_edi_pdfs")
        
        # Uncomment below to also download DLA PDFs
        # print("\n\n*** Downloading DLA EDI Convention PDFs ***\n")
        # dla_pdfs = scrape_and_download_pdfs(dla_url, "dla_edi_pdfs")
        
    except requests.exceptions.RequestException as e:
        print(f"Error accessing webpage: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")
        import traceback
        traceback.print_exc()
