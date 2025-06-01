#!/usr/bin/env python3
"""
Simplified Keyword-to-URL Mapper
Maps keywords to URLs using word-based matching with weighted scoring.
Each keyword gets assigned to exactly one URL (the highest scoring match).
"""

import csv
import logging
import re
import argparse
import sys
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from urllib.parse import urlparse
from tqdm import tqdm
from collections import defaultdict


class SimpleKeywordMapper:
    """Maps keywords to URLs using simplified word-based scoring."""
    
    def __init__(self, log_level: str = "INFO"):
        """Initialize the mapper with logging configuration."""
        self.setup_logging(log_level)
        self.keywords = []
        self.urls_data = []
        self.final_mappings = {}
        
    def setup_logging(self, log_level: str) -> None:
        """Set up logging configuration."""
        logging.basicConfig(
            level=getattr(logging, log_level.upper()),
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('keyword_mapper.log'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def load_keywords(self, filepath: str) -> None:
        """Load keywords from a text file."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                # Clean keywords properly - remove carriage returns and empty lines
                self.keywords = [line.strip().replace('\r', '') for line in f if line.strip()]
            self.logger.info(f"Loaded {len(self.keywords)} keywords from {filepath}")
        except FileNotFoundError:
            self.logger.error(f"Keywords file not found: {filepath}")
            raise
        except Exception as e:
            self.logger.error(f"Error loading keywords: {e}")
            raise
            
    def load_screaming_frog_data(self, filepath: str) -> None:
        """Load Screaming Frog CSV export data."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                # Try to detect delimiter
                sample = f.read(1024)
                f.seek(0)
                
                delimiter = ','
                if '\t' in sample and sample.count('\t') > sample.count(','):
                    delimiter = '\t'
                
                reader = csv.DictReader(f, delimiter=delimiter)
                self.urls_data = list(reader)
                
            self.logger.info(f"Loaded {len(self.urls_data)} URLs from {filepath}")
            
        except FileNotFoundError:
            self.logger.error(f"Screaming Frog file not found: {filepath}")
            raise
        except Exception as e:
            self.logger.error(f"Error loading Screaming Frog data: {e}")
            raise
    
    def normalize_text(self, text: str) -> str:
        """Normalize text for matching."""
        if not text:
            return ""
        
        # Convert to lowercase and clean up
        text = str(text).lower()
        
        # Replace common separators with spaces
        text = re.sub(r'[/_\-\|&]+', ' ', text)
        
        # Remove special characters but keep letters, numbers, and spaces
        text = re.sub(r'[^\w\s]', ' ', text)
        
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text.strip())
        
        return text
    
    def extract_url_components(self, url: str) -> str:
        """Extract searchable components from URL."""
        if not url:
            return ""
            
        try:
            parsed = urlparse(url)
            # Get domain and path components
            domain_parts = parsed.netloc.replace('www.', '').replace('.com', '').replace('.', ' ')
            path_parts = parsed.path.replace('/', ' ').replace('-', ' ').replace('_', ' ')
            
            return self.normalize_text(f"{domain_parts} {path_parts}")
        except:
            return ""
    
    def calculate_match_score(self, keyword: str, row: Dict) -> float:
        """Calculate match score between keyword and URL content."""
        keyword_normalized = self.normalize_text(keyword)
        keyword_words = keyword_normalized.split()
        
        if not keyword_words:
            return 0.0
        
        # Extract content with error handling
        try:
            url = ''
            for addr_key in ['Address', '\ufeffAddress', '"Address"', 'address', 'URL']:
                if addr_key in row and row[addr_key]:
                    url = str(row[addr_key]).strip()
                    break
            title = self.normalize_text(row.get('Title 1', ''))
            h1 = self.normalize_text(row.get('H1-1', ''))
            h2 = self.normalize_text(row.get('H2-1', ''))
            meta_desc = self.normalize_text(row.get('Meta Description 1', ''))
            meta_keywords = self.normalize_text(row.get('Meta Keywords 1', ''))
            url_components = self.extract_url_components(url)
        except Exception as e:
            self.logger.warning(f"Error extracting content for {row.get('Address', 'unknown')}: {e}")
            return 0.0
        
        # Define content fields with weights
        content_fields = [
            (title, 5.0),              # Title is most important
            (h1, 4.0),                 # H1 is very important  
            (url_components, 3.0),     # URL structure is important
            (meta_desc, 2.0),          # Meta description is helpful
            (h2, 1.5),                 # H2 is somewhat helpful
            (meta_keywords, 2.5),      # Meta keywords are helpful
        ]
        
        total_score = 0.0
        match_details = []
        
        for content, weight in content_fields:
            if not content:
                continue
                
            # Count how many keyword words appear in this content
            word_matches = sum(1 for word in keyword_words if word in content)
            
            if word_matches > 0:
                # Calculate field score based on word match percentage
                field_score = (word_matches / len(keyword_words)) * 10.0
                weighted_score = field_score * weight
                total_score += weighted_score
                
                match_details.append(f"{word_matches}/{len(keyword_words)} words in content (score: {weighted_score:.1f})")
        
        if total_score > 0:
            self.logger.debug(f"Keyword '{keyword}' -> {url} (score: {total_score:.2f})")
            self.logger.debug(f"  Matches: {'; '.join(match_details)}")
        
        return total_score
    
    def find_best_matches(self) -> None:
        """Find the best URL match for each keyword."""
        self.logger.info("Finding best matches for each keyword...")
        
        self.final_mappings = {}
        
        for keyword in tqdm(self.keywords, desc="Processing keywords"):
            best_score = 0.0
            best_match = None
            
            for row in self.urls_data:
                score = self.calculate_match_score(keyword, row)
                
                if score > best_score:
                    best_score = score
                    
                    # Handle BOM character in Address column name
                    url = ''
                    for addr_key in ['Address', '\ufeffAddress', '"Address"', 'address', 'URL']:
                        if addr_key in row and row[addr_key]:
                            url = str(row[addr_key]).strip()
                            break
                    
                    best_match = {
                        'url': url,
                        'score': score,
                        'title': row.get('Title 1', ''),
                        'h1': row.get('H1-1', ''),
                        'meta_description': row.get('Meta Description 1', ''),
                        'row_data': row
                    }
                    if not url:
                        self.logger.warning(f"Empty URL found for keyword '{keyword}' in row: {row.get('Title 1', 'No title')}")
            
                if best_match and best_score >= 5.0:  # Minimum threshold
                    self.final_mappings[keyword] = best_match
                    self.logger.debug(f"Matched: '{keyword}' -> {best_match['url']} (score: {best_score:.2f})")
                else:
                    self.final_mappings[keyword] = None
                    self.logger.debug(f"No good match for: '{keyword}' (best score: {best_score:.2f})")
        
        matched_count = sum(1 for mapping in self.final_mappings.values() if mapping)
        self.logger.info(f"Completed. {matched_count}/{len(self.keywords)} keywords matched.")
    
    def save_results(self, output_file: str) -> None:
        """Save results to CSV."""
        try:
            with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = [
                    'keyword', 'matched_url', 'match_score', 'page_title', 'h1_heading', 
                    'meta_description', 'match_quality'
                ]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                
                for keyword in self.keywords:
                    mapping = self.final_mappings.get(keyword)
                    
                    if mapping:
                        # Validate URL
                        url = mapping.get('url', '')
                        if not url:
                            self.logger.warning(f"Empty URL for keyword '{keyword}' - using placeholder")
                            url = "URL_ERROR"
                        
                        # Determine match quality
                        score = mapping['score']
                        if score >= 40:
                            quality = "Excellent"
                        elif score >= 25:
                            quality = "Good"  
                        elif score >= 15:
                            quality = "Fair"
                        else:
                            quality = "Weak"
                        
                        row_data = {
                            'keyword': keyword,
                            'matched_url': url,
                            'match_score': f"{score:.2f}",
                            'page_title': (mapping.get('title', '') or '')[:150],
                            'h1_heading': (mapping.get('h1', '') or '')[:100],
                            'meta_description': (mapping.get('meta_description', '') or '')[:200],
                            'match_quality': quality
                        }
                    else:
                        row_data = {
                            'keyword': keyword,
                            'matched_url': 'NO_MATCH',
                            'match_score': '0.00',
                            'page_title': '',
                            'h1_heading': '',
                            'meta_description': '',
                            'match_quality': 'None'
                        }
                    
                    writer.writerow(row_data)
                    
            self.logger.info(f"Results saved to {output_file}")
            
        except Exception as e:
            self.logger.error(f"Error saving results: {e}")
            raise
    
    def print_summary(self) -> None:
        """Print summary statistics."""
        total_keywords = len(self.keywords)
        matched_keywords = sum(1 for mapping in self.final_mappings.values() if mapping)
        
        # Count URLs with multiple keywords
        url_keyword_count = defaultdict(list)
        for keyword, mapping in self.final_mappings.items():
            if mapping:
                url_keyword_count[mapping['url']].append(keyword)
        
        # Score distribution
        scores = [mapping['score'] for mapping in self.final_mappings.values() if mapping]
        avg_score = sum(scores) / len(scores) if scores else 0
        
        print("\n" + "="*70)
        print("KEYWORD MAPPING RESULTS")
        print("="*70)
        print(f"Total Keywords: {total_keywords}")
        print(f"Matched Keywords: {matched_keywords}")
        print(f"Unmatched Keywords: {total_keywords - matched_keywords}")
        print(f"Match Rate: {(matched_keywords / total_keywords * 100):.1f}%")
        print(f"Unique URLs Matched: {len(url_keyword_count)}")
        print(f"Average Match Score: {avg_score:.2f}")
        if scores:
            print(f"Score Range: {min(scores):.2f} - {max(scores):.2f}")
        
        # Show top matches
        if matched_keywords > 0:
            print(f"\nTOP 10 MATCHES:")
            scored_mappings = [(k, v) for k, v in self.final_mappings.items() if v]
            scored_mappings.sort(key=lambda x: x[1]['score'], reverse=True)
            
            for i, (keyword, mapping) in enumerate(scored_mappings[:10], 1):
                url = mapping.get('url', '')
                if url and '/' in url:
                    url_name = url.split('/')[-1] or url.split('/')[-2] or url
                else:
                    url_name = url or 'unknown'
                print(f"{i:2d}. '{keyword}' → {url_name} (score: {mapping['score']:.1f})")
        
        # Show URLs with multiple keywords
        multi_keyword_urls = {url: keywords for url, keywords in url_keyword_count.items() if len(keywords) > 1}
        if multi_keyword_urls:
            print(f"\nURLs WITH MULTIPLE KEYWORDS ({len(multi_keyword_urls)}):")
            for url, keywords in sorted(multi_keyword_urls.items(), key=lambda x: len(x[1]), reverse=True)[:5]:
                if url and '/' in url:
                    url_name = url.split('/')[-1] or url.split('/')[-2] or url
                else:
                    url_name = url or 'unknown'
                print(f"  {url_name}: {len(keywords)} keywords")
                for keyword in keywords[:3]:  # Show first 3
                    print(f"    - {keyword}")
                if len(keywords) > 3:
                    print(f"    ... and {len(keywords) - 3} more")
        
        print("="*70)


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Simple keyword-to-URL mapping")
    parser.add_argument("--keywords-file", 
                       default="keywords.txt",
                       help="Path to keywords file")
    parser.add_argument("--screaming-frog-file", 
                       default="internal_all.csv",
                       help="Path to Screaming Frog export")
    parser.add_argument("--output-file", 
                       default="keyword_mappings_final.csv",
                       help="Output CSV file")
    parser.add_argument("--log-level", 
                       choices=["DEBUG", "INFO", "WARNING", "ERROR"],
                       default="INFO",
                       help="Logging level")
    
    args = parser.parse_args()
    
    mapper = SimpleKeywordMapper(log_level=args.log_level)
    
    try:
        mapper.load_keywords(args.keywords_file)
        mapper.load_screaming_frog_data(args.screaming_frog_file)
        mapper.find_best_matches()
        mapper.save_results(args.output_file)
        mapper.print_summary()
        
    except Exception as e:
        mapper.logger.error(f"Script failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()