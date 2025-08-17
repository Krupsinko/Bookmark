import httpx
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

async def scrape_title(url) -> str:
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, timeout=10.0)
            response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        title_tag = soup.find("title").text
        return title_tag
    except (httpx.HTTPError, Exception) as exception:
        print(exception)
        return ""
    
    
async def scrape_favicon(url):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, timeout=5.0)
            response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        
        icons = []
        
        for link in soup.find_all("link"):
            rel = link.get("rel")
            if not rel:
                continue
            if any(x in rel for x in["icon", "shortcut icon", "apple-touch-icon"]):
                href = link.get("href")
                if href:
                    size = link.get("sizes", "")
                    full_url = urljoin(url, href)
                    icons.append((full_url, size))
        
        if icons == []: #fallback - If there is no link tags with favicon URL
            parsed = urlparse(url)
            fallback = f"{parsed.scheme}://{parsed.netloc}/favicon.ico"
            icons.append(fallback)
            if icons == []:
                return ""
        
        icons_with_size = [(icon, size) for icon, size in icons if size.split("x")[0].isdigit()]
        if icons_with_size:
            highest_resolution = max(icons_with_size, key=lambda x: int(x[1].split("x")[0]))
            return highest_resolution[0]
        
    except (httpx.HTTPError, Exception) as exception:
        print(exception)
        return []