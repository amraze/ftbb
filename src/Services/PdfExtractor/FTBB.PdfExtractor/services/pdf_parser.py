"""
PDF Parser service module
Handles PDF parsing for basketball box scores
"""
import pdfplumber
import re
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

# OCR imports (optional - graceful fallback if not installed)
OCR_AVAILABLE = False
OCR_METHOD = None

# Try PyMuPDF first (easier on Windows - no poppler needed)
try:
    import fitz  # PyMuPDF
    OCR_AVAILABLE = True
    OCR_METHOD = 'pymupdf'
except ImportError:
    pass

# Fallback to pdf2image + pytesseract
if not OCR_AVAILABLE:
    try:
        from pdf2image import convert_from_path
        import pytesseract
        OCR_AVAILABLE = True
        OCR_METHOD = 'pdf2image'
    except ImportError:
        pass


class SimplifiedBasketballParser:
    """Simplified parser for basketball box score PDFs - extracts only teams and players"""
    
    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
        self.used_ocr = False
        self.data = {
            "teams": []
        }
    
    def _extract_text_with_ocr(self) -> str:
        if not OCR_AVAILABLE:
            raise ImportError("OCR not available. Install: pip install pymupdf pytesseract")
        
        if OCR_METHOD == 'pymupdf':
            return self._ocr_with_pymupdf()
        else:
            return self._ocr_with_pdf2image()
    
    def _ocr_with_pymupdf(self) -> str:
        """OCR using PyMuPDF - works on Windows without poppler"""
        import fitz
        
        # Check if pytesseract is available for OCR
        try:
            import pytesseract
            has_tesseract = True
        except ImportError:
            has_tesseract = False
        
        doc = fitz.open(self.pdf_path)
        page = doc[0]  # Only process first page
        
        # First try to get text directly
        text = page.get_text()
        
        # If text is insufficient, try OCR
        if len(text.strip()) < 100 and has_tesseract:
            mat = fitz.Matrix(3, 3)  # 3x zoom for better OCR
            pix = page.get_pixmap(matrix=mat)
            
            from PIL import Image
            import io
            img_data = pix.tobytes("png")
            image = Image.open(io.BytesIO(img_data))
            
            try:
                text = pytesseract.image_to_string(image, lang='fra+eng', config='--oem 3 --psm 6')
            except:
                text = pytesseract.image_to_string(image, lang='eng', config='--oem 3 --psm 6')
        
        doc.close()
        return text
    
    def _ocr_with_pdf2image(self) -> str:
        """OCR using pdf2image + pytesseract - requires poppler on Windows"""
        from pdf2image import convert_from_path
        import pytesseract
        
        images = convert_from_path(self.pdf_path, dpi=300, first_page=1, last_page=1)
        
        custom_config = r'--oem 3 --psm 6'
        try:
            text = pytesseract.image_to_string(images[0], lang='fra+eng', config=custom_config)
        except:
            text = pytesseract.image_to_string(images[0], lang='eng', config=custom_config)
        
        return text
    
    def _is_text_sufficient(self, text: str) -> bool:
        """Check if extracted text is sufficient for parsing"""
        if not text or len(text.strip()) < 100:
            return False
        
        indicators = [
            r'\d{1,2}:\d{2}',  # Time format
            r'\d+/\d+',        # Made/Attempts format
            r'\d{2,3}\s*[-–]\s*\d{2,3}',  # Score format
        ]
        
        found = sum(1 for pattern in indicators if re.search(pattern, text))
        return found >= 2
    
    def _clean_ocr_text(self, text: str) -> str:
        text = re.sub(r'\|+', ' ', text)
        text = re.sub(r'\[(?!\d)', ' ', text)
        text = re.sub(r'(?<!\d)\]', ' ', text)
        text = re.sub(r'[ \t]+', ' ', text)
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        return text
    
    def parse(self) -> Dict[str, Any]:
        """Main parsing method"""
        text = ""
        
        try:
            with pdfplumber.open(self.pdf_path) as pdf:
                first_page = pdf.pages[0]
                text = first_page.extract_text() or ""
        except Exception as e:
            logger.warning(f"pdfplumber extraction failed: {e}")
            text = ""
        
        if not self._is_text_sufficient(text):
            if OCR_AVAILABLE:
                try:
                    text = self._extract_text_with_ocr()
                    self.used_ocr = True
                    text = self._clean_ocr_text(text)
                except Exception as e:
                    logger.warning(f"OCR extraction failed: {e}")
                    if not text:
                        raise ValueError("Could not extract text from PDF")
            else:
                if not text:
                    raise ValueError("Could not extract text from PDF. Install OCR dependencies: pip install pytesseract pdf2image")
        
        # Extract team data
        self._extract_teams(text)
        
        return self.data
    
    def _extract_teams(self, text: str):
        """Extract teams and players using simplified parsing"""
        lines = text.split('\n')
        team_sections = []
        
        # Find team sections - look for team name pattern with abbreviation
        for i, line in enumerate(lines):
            # Pattern: TEAM NAME (ABBR)
            match = re.search(r'^([A-Z][A-Z\s]{3,})\s*\(([A-Z]{2,5})\)', line)
            if match:
                team_name = match.group(1).strip()
                team_abbr = match.group(2).strip()
                
                # Verify this looks like a team name (not a person's name)
                words = team_name.split()
                if len(words) >= 2:
                    # Check if there's player data nearby (within 10 lines)
                    has_player_data = False
                    for j in range(i, min(i + 10, len(lines))):
                        if re.match(r'^\*?\d{1,2}\s+[A-Z]', lines[j]):
                            has_player_data = True
                            break
                    
                    if has_player_data:
                        # Avoid duplicates
                        if not any(t['name'] == team_name for t in team_sections):
                            team_sections.append({
                                'name': team_name,
                                'abbreviation': team_abbr,
                                'start_line': i
                            })
        
        # Parse each team found
        for idx, team_info in enumerate(team_sections):
            # Determine end line (start of next team or end of document)
            end_line = team_sections[idx + 1]['start_line'] if idx + 1 < len(team_sections) else len(lines)
            
            players = self._extract_players(lines, team_info['start_line'], end_line)
            
            self.data["teams"].append({
                "name": team_info['name'],
                "abbreviation": team_info['abbreviation'],
                "players": players
            })
    
    def _extract_players(self, lines: List[str], start: int, end: int) -> List[Dict]:
        """Extract only player numbers and names"""
        players = []
        
        # Skip patterns
        skip_patterns = [
            'Coach:', 'Entraîneur:', 'FieldGoals', 'Tirs Tot.', 'M/A', 'R/T',
            'No', 'Name', 'Nom', 'Min', 'Assistant', 'Field Goals', 'Points',
            'Rebounds', 'Fouls', 'Rebonds', 'Fautes', 'MA%', 'MA %', 'OR DR'
        ]
        
        # Totals patterns
        totals_patterns = ['Totals', 'Totaux', 'Team/Coach', 'Equipe/Coach', 'TeamiCoach']
        
        # DNP patterns
        dnp_patterns = ['DNP', 'NPJ']
        
        for i in range(start, min(end, len(lines))):
            line = lines[i]
            
            # Skip non-player lines
            if not line:
                continue
            if any(pattern in line for pattern in skip_patterns):
                continue
            if any(line.strip().startswith(pattern) for pattern in totals_patterns):
                break
            if line.count('-') > 10 or line.count('=') > 10:
                continue
            
            # Try to extract player - OCR pattern
            player_match = re.match(r'^\s*\*?(\d{1,2})[_\s]+([A-Z][A-Z\s]+?)(?:\s+\d{1,2}:\d{2}|$)', line)
            
            if not player_match:
                # Alternative OCR pattern
                player_match = re.match(r'^\s*\*?(\d{1,2})\s*[\[_]?\s*([A-Z][A-Z\s]+?)(?:\s+\d{1,2}:\d{2}|$)', line)
            
            if player_match:
                number = player_match.group(1)
                name = player_match.group(2).strip()
                
                # Clean up captain marker and extra spaces
                name = name.replace('(C)', '').replace('(c)', '').replace('*', '').strip()
                
                # Skip if name is too short (likely parsing error)
                if len(name) > 2:
                    players.append({
                        "number": number,
                        "name": name
                    })
                continue
            
            # Standard parsing for clean PDFs
            tokens = line.split()
            if len(tokens) == 0:
                continue
            
            first_token = tokens[0].replace('*', '').replace('_', '')
            
            # Check if it's a valid player number (0-99)
            if not first_token.isdigit():
                continue
            
            try:
                player_num = int(first_token)
                if player_num > 99:
                    continue
            except ValueError:
                continue
            
            # Find where the name ends (look for time format or stats)
            name_end_idx = 1
            for j in range(1, len(tokens)):
                # Stop at time format (MM:SS)
                if ':' in tokens[j]:
                    break
                # Stop at DNP
                if tokens[j] in dnp_patterns:
                    break
                # Stop at made/attempts pattern
                if '/' in tokens[j] and re.match(r'\d+/\d+', tokens[j]):
                    break
                name_end_idx = j + 1
            
            # Extract name
            name_tokens = tokens[1:name_end_idx]
            player_name = ' '.join(name_tokens)
            
            # Clean up captain marker
            player_name = player_name.replace('(C)', '').replace('(c)', '').replace('*', '').strip()
            
            # Skip if name is too short or looks invalid
            if len(player_name) > 2:
                players.append({
                    "number": first_token,
                    "name": player_name
                })
        
        return players
