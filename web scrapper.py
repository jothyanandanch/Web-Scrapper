import requests
from bs4 import BeautifulSoup

def connect_to_website(url):
    #Handles the website connection and returns HTML content
    response = requests.get(url)
    print("Response status:", response)
    
    if response.status_code == 200:
        print("The Request is Successful!\n")
        return response.text
    else:
        print("Something Went Wrong! Status code:", response.status_code, "\n")
        return None

def create_soup(html_content):
    #Creates BeautifulSoup object from HTML content
    if not html_content:
        return None
    return BeautifulSoup(html_content, 'html.parser')

def extract_headers(soup):
    #Extracts and prints title and headline
    if soup.title:
        print(f"Title: {soup.title.string}\n")
    else:
        print("No Title found\n")
    
    headline = soup.find('h1')
    if headline:
        print(f"The Headline: {headline.get_text().strip()}\n")


def is_junk(element):
    if not hasattr(element, 'attrs'):
        return False

    junk_indicators = {
        'class': ['ad', 'poll', 'recommend', 'video', 'social', 'widget', 'taboola'],
        'id': ['ad-', 'widget-', 'footer', 'sidebar'],
        'role': ['advertisement', 'recommendation']
    }

    for attr, patterns in junk_indicators.items():
        attr_value = ' '.join(element.get(attr, '')) if isinstance(element.get(attr, ''), list) else element.get(attr, '')
        if any(pattern in attr_value.lower() for pattern in patterns):
            return True

    return element.name in ['script', 'style', 'iframe', 'noscript'] or element.find_parent(class_=lambda x: x and 'ad' in x.lower())

def extract_paragraphs(soup):
    #Extracts clean article paragraphs using .children approach
    articlecontent = soup.find('div', class_='_s30J')
    if not articlecontent:
        print("No article content found\n")
        return

    clean_paragraphs = []
    current_paragraph = ""
    
    for child in articlecontent.children:
        # Skip processing if it's a junk element
        if hasattr(child, 'name') and is_junk(child):
            continue
        
        # Handle separator spans
        if hasattr(child, 'name') and child.name == 'span' and 'br' in child.get('class', []):
            if current_paragraph:
                clean_paragraphs.append(current_paragraph.strip())
                current_paragraph = ""
            continue
        
        # Extract text based on element type
        if isinstance(child, str):
            text = child.strip()
        else:
            text = child.get_text(' ', strip=True)
        
        # Accumulate meaningful text
        if text and len(text) > 30 and not any(word in text.lower() for word in ['subscribe', 'read more', 'follow us']):
            current_paragraph += " " + text if current_paragraph else text
    
    # Add the last paragraph if exists
    if current_paragraph:
        clean_paragraphs.append(current_paragraph.strip())

    # Print the cleaned paragraphs
    print(f"\nFound {len(clean_paragraphs)} meaningful paragraphs:")
    for i, para in enumerate(clean_paragraphs, 1):
        print(f"\nParagraph {i}:")
        print(para)

def scrape_website(url):
    #Main scraping function
    html_data = connect_to_website(url)
    if not html_data:
        return
    
    soup = create_soup(html_data)
    extract_headers(soup)
    extract_paragraphs(soup)

if __name__ == "__main__":
    url = 'https://timesofindia.indiatimes.com/world/middle-east/tensions-soar-why-did-israel-strike-iran-what-makes-the-timing-crucial-explained/articleshow/121818858.cms'
    scrape_website(url)