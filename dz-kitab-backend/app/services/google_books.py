# app/services/google_books.py

import httpx
from typing import Optional, Dict, Any
from fastapi import HTTPException, status

GOOGLE_BOOKS_API_URL = "https://www.googleapis.com/books/v1/volumes"


async def fetch_book_by_isbn(isbn: str) -> Optional[Dict[str, Any]]:
    """
    Fetch book information from Google Books API using ISBN
    
    Args:
        isbn: ISBN-10 or ISBN-13 of the book
        
    Returns:
        Dictionary containing book information or None if not found
    """
    try:
        # Clean the ISBN (remove dashes and spaces)
        clean_isbn = isbn.replace("-", "").replace(" ", "")
        
        # Query Google Books API
        async with httpx.AsyncClient() as client:
            response = await client.get(
                GOOGLE_BOOKS_API_URL,
                params={"q": f"isbn:{clean_isbn}"},
                timeout=10.0
            )
            response.raise_for_status()
            data = response.json()
        
        # Check if we got results
        if data.get("totalItems", 0) == 0:
            return None
        
        # Extract book information from the first result
        book_data = data["items"][0]["volumeInfo"]
        
        # Extract image links (prefer thumbnail, fallback to smallThumbnail)
        image_links = book_data.get("imageLinks", {})
        cover_image = (
            image_links.get("thumbnail") or 
            image_links.get("smallThumbnail") or 
            None
        )
        
        # If we have a cover image, upgrade to higher resolution
        if cover_image:
            cover_image = cover_image.replace("zoom=1", "zoom=2")
            # Remove edge curl effect
            cover_image = cover_image.replace("&edge=curl", "")
        
        # Structure the response
        book_info = {
            "isbn": clean_isbn,
            "title": book_data.get("title", ""),
            "subtitle": book_data.get("subtitle"),
            "authors": book_data.get("authors", []),
            "publisher": book_data.get("publisher"),
            "published_date": book_data.get("publishedDate"),
            "description": book_data.get("description"),
            "page_count": book_data.get("pageCount"),
            "categories": book_data.get("categories", []),
            "language": book_data.get("language", "fr"),
            "cover_image_url": cover_image,
            "preview_link": book_data.get("previewLink"),
            "info_link": book_data.get("infoLink"),
        }
        
        return book_info
        
    except httpx.HTTPError as e:
        print(f"❌ HTTP error while fetching book: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Impossible de contacter l'API Google Books"
        )
    except Exception as e:
        print(f"❌ Error fetching book by ISBN: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la récupération des données du livre: {str(e)}"
        )


async def search_books(query: str, max_results: int = 10) -> list:
    """
    Search for books using a general query
    
    Args:
        query: Search query (title, author, etc.)
        max_results: Maximum number of results to return
        
    Returns:
        List of books matching the query
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                GOOGLE_BOOKS_API_URL,
                params={
                    "q": query,
                    "maxResults": min(max_results, 40),  # Google Books API max is 40
                },
                timeout=10.0
            )
            response.raise_for_status()
            data = response.json()
        
        if data.get("totalItems", 0) == 0:
            return []
        
        books = []
        for item in data.get("items", []):
            volume_info = item.get("volumeInfo", {})
            image_links = volume_info.get("imageLinks", {})
            cover_image = image_links.get("thumbnail") or image_links.get("smallThumbnail")
            
            if cover_image:
                cover_image = cover_image.replace("zoom=1", "zoom=2").replace("&edge=curl", "")
            
            books.append({
                "title": volume_info.get("title", ""),
                "authors": volume_info.get("authors", []),
                "publisher": volume_info.get("publisher"),
                "published_date": volume_info.get("publishedDate"),
                "cover_image_url": cover_image,
                "isbn": extract_isbn(volume_info.get("industryIdentifiers", [])),
            })
        
        return books
        
    except Exception as e:
        print(f"❌ Error searching books: {e}")
        return []


def extract_isbn(identifiers: list) -> Optional[str]:
    """Extract ISBN from industry identifiers"""
    for identifier in identifiers:
        if identifier.get("type") in ["ISBN_13", "ISBN_10"]:
            return identifier.get("identifier")
    return None