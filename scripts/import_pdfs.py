#!/usr/bin/env python
"""
PDF Import Script for FastAPI Book Management

This script recursively traverses a specified folder, finds PDF files,
and creates book entries in the database using the CRUD API.

Features:
- Recursive folder traversal
- PDF file detection
- File size calculation
- Content hash generation (SHA-256)
- Database integration via CRUD API
- Progress tracking and error handling
- Duplicate detection
"""

import os
import sys
import hashlib
import argparse
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import asyncio
import aiohttp
import json
from urllib.parse import urljoin
import time

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# TODO import variable from .env file
from dotenv import load_dotenv
load_dotenv(str(Path(__file__).parent.parent / "src" / ".env"))
env_base_url = os.getenv('API_BASE_URL')
env_username = os.getenv('API_ADMIN_USERNAME')
env_password = os.getenv('API_ADMIN_PASSWORD')

print(f"env_base_url: {env_base_url}, env_username: {env_username}, env_password: {env_password}")

try:
    from app.schemas.book import BookCreate
    from app.core.config import settings
except ImportError as e:
    print(f"Error importing app modules: {e}")
    print("Make sure you're running this from the project root directory")
    sys.exit(1)


class PDFImporter:
    """Handles PDF file discovery and book creation via API."""
    
    def __init__(self, b_url, user_name, p_word):
        self.base_url = b_url.rstrip('/')
        self.username = user_name
        self.password = p_word
        self.session: Optional[aiohttp.ClientSession] = None
        self.access_token: Optional[str] = None
        self.books_cache: List[dict] = []
        self.stats = {
            'total_files': 0,
            'pdf_files': 0,
            'created_books': 0,
            'skipped_books': 0,
            'errors': 0
        }
    
    async def __aenter__(self):
        """Async context manager entry."""
        self.session = aiohttp.ClientSession()
        # Authenticate and get access token
        await self.authenticate()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()
    
    async def authenticate(self) -> bool:
        """Authenticate with the FastAPI server and get access token."""
        if not self.session:
            return False
        
        try:
            # Prepare login data
            login_data = {
                'username': self.username,
                'password': self.password,
                'grant_type': 'password'
            }
            
            # Login to get access token
            url = f"{self.base_url}/api/v1/login"
            
            async with self.session.post(url, data=login_data) as response:
                if response.status == 200:
                    token_data = await response.json()
                    self.access_token = token_data.get('access_token')
                    if self.access_token:
                        print(f"✅ Authenticated successfully as {self.username}")
                        return True
                    else:
                        print("❌ No access token received")
                        return False
                else:
                    error_text = await response.text()
                    print(f"❌ Authentication failed: {response.status} - {error_text}")
                    return False
                    
        except Exception as e:
            print(f"❌ Authentication error: {e}")
            return False
    
    def is_pdf_file(self, file_path: Path) -> bool:
        """Check if a file is a PDF based on extension."""
        return file_path.suffix.lower() == '.pdf'
    
    def get_file_info(self, file_path: Path) -> Dict:
        """Extract file information including size and content hash."""
        try:
            stat = file_path.stat()
            file_size = stat.st_size
            
            # Generate content hash (SHA-256)
            content_hash = self.generate_file_hash(file_path)
            
            return {
                'path': str(file_path),
                'name': file_path.name,
                'size': file_size,
                'hash': content_hash,
                'relative_path': str(file_path.relative_to(file_path.parents[-1]))
            }
        except Exception as e:
            print(f"Error getting file info for {file_path}: {e}")
            return None
    
    def generate_file_hash(self, file_path: Path) -> str:
        """Generate SHA-256 hash of file content."""

        hash_sha256 = hashlib.sha256()
        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_sha256.update(chunk)
            return hash_sha256.hexdigest()
        except Exception as e:
            print(f"Error generating hash for {file_path}: {e}")
            return ""
    
    def extract_book_metadata(self, file_path: Path) -> Dict:
        """Extract book metadata from filename and path."""
        filename = file_path.stem  # Remove extension
        
        # Try to extract title and author from filename
        # Common patterns: "Title - Author.pdf", "Author - Title.pdf", "Title.pdf"
        title = filename
        author = "Unknown Author"
        
        # Look for common separators
        separators = [' - ', ' by ', ' -by- ', '_by_', ' by ']
        for sep in separators:
            if sep in filename:
                parts = filename.split(sep, 1)
                if len(parts) == 2:
                    # Assume first part is title, second is author
                    title = parts[0].strip()
                    author = parts[1].strip()
                    break
        
        # Clean up title and author
        title = title.replace('_', ' ').replace('-', ' ').strip()
        author = author.replace('_', ' ').replace('-', ' ').strip()
        
        # If title is too long, truncate it
        if len(title) > 200:
            title = title[:197] + "..."
        
        # If author is too long, truncate it
        if len(author) > 100:
            author = author[:97] + "..."
        
        return {
            'title': title,
            'author': author
        }
    
    async def get_books_in_db(self) -> bool:
        """Get all books in the database."""
        if not self.session:
            return False
        
        try:
            # Use the public books endpoint to search
            url = f"{self.base_url}/api/v1/books"
            params = {'items_per_page': 100}  # Get more books to search through
            
            async with self.session.post(url, params=params) as response:
                #print(f"response: {response}")
                # if data is paginated, we need to get all the pages
                if response.status != 200:
                    print(f"Warning: Could not check for existing books (status: {response.status})")
                    return False

                if response.headers.get('Content-Type') != 'application/json':
                    print(f"Warning: Could not check for existing books (headers : {response.headers})")
                    return False
                
                data = await response.json()
                #print(f"\ndata: {data}\n")
                self.books_cache = data.get('data', [])
                #print(f"books: {books}")
                # get the next page
                print(f"data: {data.get('next')}")
                while data.get('has_more'):
                    params = {'items_per_page': 100, 'page': str(int(data.get('page')) + 1)}  # Get more books to search through
                    async with self.session.post(url, params=params) as response:
                        data = await response.json()
                        #print(f"data: {data}")
                        self.books_cache.extend(data.get('data', []))

                return True


        except Exception as e:
            print(f"Error getting books in database: {e}")
            return False
    
    async def check_book_exists(self, content_hash: str) -> bool:
        """Check if a book with the same content hash already exists."""
        if not self.books_cache:
            if not (await self.get_books_in_db()):
                print(f"Error getting books in database")
                return False

        print(f"books_cache length: {len(self.books_cache)} ")
        for book in self.books_cache:
            if book.get('content_hash') == content_hash:
                return True 
        return False

    # async def check_book_exists(self, content_hash: str) -> bool:
    #     """Check if a book with the same content hash already exists."""
    #     if not self.session:
    #         return False
        
    #     try:
    #         # Use the public books endpoint to search
    #         url = f"{self.base_url}/api/v1/books"
    #         params = {'items_per_page': 100}  # Get more books to search through
            
    #         async with self.session.post(url, params=params) as response:
    #             #print(f"response: {response}")
    #             # if data is paginated, we need to get all the pages
    #             if response.status != 200:
    #                 print(f"Warning: Could not check for existing books (status: {response.status})")
    #                 return False

    #             if response.headers.get('Content-Type') != 'application/json':
    #                 print(f"Warning: Could not check for existing books (headers : {response.headers})")
    #                 return False
                
    #             data = await response.json()
    #             #print(f"\ndata: {data}\n")
    #             books = data.get('data', [])
    #             #print(f"books: {books}")
    #             # get the next page
    #             print(f"data: {data.get('next')}")
    #             while data.get('has_more'):
    #                 params = {'items_per_page': 100, 'page': str(int(data.get('page')) + 1)}  # Get more books to search through
    #                 async with self.session.post(url, params=params) as response:
    #                     data = await response.json()
    #                     #print(f"data: {data}")
    #                     books.extend(data.get('data', []))


    #             print(f"books_length: {len(books)}")
    #             # Check if any book has the same content hash
    #             for book in books:
    #                 if book.get('content_hash') == content_hash:
    #                     return True

    #     except Exception as e:
    #         print(f"Error checking for existing book: {e}")
    #         return False
    
    async def create_book(self, file_info: Dict, metadata: Dict) -> bool:
        """Create a book in the database via API."""
        if not self.session:
            return False
        
        try:
            # Check if book already exists
            if await self.check_book_exists(file_info['hash']):
                print(f"⚠️  Book already exists (hash: {file_info['hash'][:8]}...): {file_info['name']}")
                self.stats['skipped_books'] += 1
                return True
            
            # Prepare book data
            book_data = {
                'title': metadata['title'],
                'author': metadata['author'],
                'description': f"PDF file: {file_info['name']}",
                'folder_path': file_info['relative_path'],
                'file_size_bytes': file_info['size'],
                'content_hash': file_info['hash']
            }
            
            # Create book via API
            url = f"{self.base_url}/api/v1/{self.username}/book"

            headers = {
                'Authorization': f'Bearer {self.access_token}'
            }
            #print(f"headers: {headers} and url: {url} and book_data: {book_data}")
            async with self.session.post(url, json=book_data, headers=headers) as response:
                if response.status == 201:
                    book = await response.json()
                    print(f"✅ Created book: {book['title']} by {book['author']} (ID: {book['id']})")
                    self.stats['created_books'] += 1
                    self.books_cache.append(book)
                    return True
                else:
                    error_text = await response.text()
                    print(f"❌ Failed to create book '{metadata['title']}': {response.status} - {error_text}")
                    self.stats['errors'] += 1
                    return False
                    
        except Exception as e:
            print(f"❌ Error creating book '{metadata['title']}': {e}")
            self.stats['errors'] += 1
            return False
    
    async def process_pdf_file(self, file_path: Path) -> None:
        """Process a single PDF file."""
        self.stats['total_files'] += 1
        
        if not self.is_pdf_file(file_path):
            return
        
        self.stats['pdf_files'] += 1
        print(f"📖 Processing PDF: {self.stats['pdf_files']}  - {file_path.name}")
        
        # Get file information
        file_info = self.get_file_info(file_path)
        if not file_info:
            self.stats['errors'] += 1
            return
        
        # Extract metadata
        metadata = self.extract_book_metadata(file_path)
        
        # Create book in database
        await self.create_book(file_info, metadata)
    
    async def scan_directory(self, directory: Path) -> None:
        """Recursively scan directory for PDF files."""
        print(f"🔍 Scanning directory: {directory}")
        
        try:
            for item in directory.iterdir():
                if item.is_file():
                    await self.process_pdf_file(item)
                elif item.is_dir():
                    # Skip hidden directories and common system directories
                    if not item.name.startswith('.') and item.name not in ['node_modules', '__pycache__', '.git']:
                        await self.scan_directory(item)
        except PermissionError:
            print(f"⚠️  Permission denied accessing: {directory}")
        except Exception as e:
            print(f"❌ Error scanning directory {directory}: {e}")
    
    def print_stats(self) -> None:
        """Print import statistics."""
        print("\n" + "="*50)
        print("📊 IMPORT STATISTICS")
        print("="*50)
        print(f"Total files scanned: {self.stats['total_files']}")
        print(f"PDF files found: {self.stats['pdf_files']}")
        print(f"Books created: {self.stats['created_books']}")
        print(f"Books skipped (duplicates): {self.stats['skipped_books']}")
        print(f"Errors: {self.stats['errors']}")
        print("="*50)


async def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description="Import PDF files from a directory into the FastAPI book database",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Import PDFs from current directory
  python scripts/import_pdfs.py .

  # Import PDFs from specific directory
  python scripts/import_pdfs.py /path/to/books

  # Use custom API endpoint and username
  python scripts/import_pdfs.py /path/to/books --api-url http://localhost:8000 --username admin

  # Dry run (don't create books, just scan)
  python scripts/import_pdfs.py /path/to/books --dry-run
        """
    )
    
    parser.add_argument(
        'directory',
        type=str,
        help='Directory to scan for PDF files'
    )
    
    parser.add_argument(
         '--api-url',
         type=str,
         default=env_base_url,
         help='FastAPI server URL (default: ' +  env_base_url + ')'
    )
    
    parser.add_argument(
         '--username',
         type=str,
         default=env_username,
         help='Username for book creation (default: ' + env_username + ')'
    )

    parser.add_argument(
         '--password',
         type=str,
         default=env_password,
         help='Password for book creation (default: ' + env_password + ')'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Scan files without creating books in database'
    )
    
    args = parser.parse_args()

    # Validate directory
    directory = Path(args.directory)
    print(f"directory: {directory}, args.api_url: {args.api_url}, args.username: {args.username}")
    print(f"pwd: {os.getcwd()}")
    if not directory.exists():
        print(f"❌ Error: Directory '{directory}' does not exist")
        sys.exit(1)
    
    if not directory.is_dir():
        print(f"❌ Error: '{directory}' is not a directory")
        sys.exit(1)
    
    print(f"🚀 PDF Import Script")
    print(f"📁 Directory: {directory.absolute()}")
    print(f"🌐 API URL: {args.api_url}")
    print(f"👤 Username: {args.username}")
    print(f"🔒 Password: {args.password}")
    print(f"🔍 Mode: {'Dry Run' if args.dry_run else 'Live Import'}")
    print("-" * 50)
    
    if args.dry_run:
        print("⚠️  DRY RUN MODE: No books will be created in the database")
        print("-" * 50)
    
    # Create importer
    async with PDFImporter(args.api_url, args.username, args.password) as importer:
        try:
            # Scan directory
            await importer.scan_directory(directory)
            
            # Print statistics
            importer.print_stats()
            
        except KeyboardInterrupt:
            print("\n⚠️  Import interrupted by user")
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            sys.exit(1)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⚠️  Script interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        sys.exit(1)
