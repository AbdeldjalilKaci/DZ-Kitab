# app/services/isbn_scraper.py

import httpx
from bs4 import BeautifulSoup
from typing import Optional, Dict, Any
from fastapi import HTTPException, status
import re

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
}

async def fetch_book_from_openlibrary(isbn: str) -> Optional[Dict[str, Any]]:
    """Fetch book info from Open Library API (Open Source alternative)"""
    try:
        url = f"https://openlibrary.org/api/books?bibkeys=ISBN:{isbn}&format=json&jscmd=data"
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=HEADERS, timeout=10.0)
            if response.status_code != 200:
                return None
            data = response.json()
            
        key = f"ISBN:{isbn}"
        if key not in data:
            return None
        
        book_data = data[key]
        
        return {
            "isbn": isbn,
            "title": book_data.get("title", ""),
            "subtitle": book_data.get("subtitle"),
            "authors": [a.get("name") for a in book_data.get("authors", [])],
            "publisher": book_data.get("publishers", [{}])[0].get("name") if book_data.get("publishers") else None,
            "published_date": book_data.get("publish_date"),
            "description": book_data.get("notes") or book_data.get("title"),
            "page_count": book_data.get("number_of_pages"),
            "categories": [s.get("name") for s in book_data.get("subjects", [])[:3]],
            "language": "fr", # OpenLibrary usually has multi-lang, defaulting to fr for consistency
            "cover_image_url": book_data.get("cover", {}).get("large") or book_data.get("cover", {}).get("medium"),
            "preview_link": book_data.get("url"),
            "info_link": book_data.get("url"),
        }
    except Exception as e:
        print(f"⚠️ Error fetching from OpenLibrary: {e}")
        return None

async def scrape_book_from_babelio(isbn: str) -> Optional[Dict[str, Any]]:
    """Scrape book info from Babelio (French book community)"""
    try:
        # Babelio often uses ISBN13 in search
        search_url = f"https://www.babelio.com/resrecherche.php?search={isbn}"
        async with httpx.AsyncClient() as client:
            response = await client.get(search_url, headers=HEADERS, timeout=10.0, follow_redirects=True)
            if response.status_code != 200:
                return None
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # If we are on a result page instead of a book page, we need to click the first result
            # But usually searching by ISBN redirects to the book page
            
            title_tag = soup.select_one('h1[itemprop="name"]')
            if not title_tag:
                return None
            
            author_tag = soup.select_one('span[itemprop="author"] a')
            desc_tag = soup.select_one('div#un_resume')
            img_tag = soup.select_one('img[itemprop="image"]')
            
            # Extract more details from page
            details_text = soup.get_text()
            page_match = re.search(r'(\d+)\s+pages', details_text)
            publisher_match = re.search(r'Editeur\s+:\s+([^\n]+)', details_text)
            
            return {
                "isbn": isbn,
                "title": title_tag.get_text(strip=True),
                "authors": [author_tag.get_text(strip=True)] if author_tag else ["Auteur Inconnu"],
                "description": desc_tag.get_text(strip=True) if desc_tag else None,
                "cover_image_url": img_tag['src'] if img_tag else None,
                "page_count": int(page_match.group(1)) if page_match else None,
                "publisher": publisher_match.group(1).strip() if publisher_match else None,
                "language": "fr",
                "categories": ["Livre"],
                "published_date": None # Hard to extract reliably without more complex regex
            }
    except Exception as e:
        print(f"⚠️ Error scraping from Babelio: {e}")
        return None

async def fetch_book_by_isbn_scraping(isbn: str) -> Optional[Dict[str, Any]]:
    """
    Combined ISBN lookup using API and Web Scraping
    This replaces the Google Books API service.
    """
    # 1. Try OpenLibrary (Reliable API)
    book_info = await fetch_book_from_openlibrary(isbn)
    if book_info:
        return book_info
    
    # 2. Try Babelio (Web Scraping)
    book_info = await scrape_book_from_babelio(isbn)
    if book_info:
        return book_info
    
    return None
