"""
GamblingAdDetector - Alpha-1.5 by Awiones
https://github.com/awiones
"""

__version__ = "Alpha-1.5"


import re
import unicodedata
from collections import Counter
import string
import itertools
from typing import Dict, List, Tuple, Set, Optional, Union, Any


class GamblingAdDetector:
    """
    Advanced gambling advertisement detector that identifies various patterns
    commonly found in gambling spam across different languages and formats.
    Includes enhanced detection for randomly generated names and obfuscation techniques.

    Version: Alpha-1.5 by Awiones
    https://github.com/awiones
    """
    
    def __init__(self):
        # Core gambling keywords (significantly expanded)
        self.keywords = set()
        # Domain TLDs commonly used in gambling sites (expanded)
        self.suspicious_tlds = set()
        # Common name patterns used in gambling sites
        self.name_patterns = []
        # Suspicious character repetition (e.g., "$$$$")
        self.suspicious_chars = set()
        # Common number patterns in gambling site names
        self.common_numbers = set()
        # Common obfuscation techniques
        self.obfuscation_chars = {}
        # Threshold for scoring system
        self.threshold = 0.6
        # Compile regex patterns for better performance
        self._compile_patterns()
        
    def _compile_patterns(self):
        """Compile regex patterns for better performance"""
        # Pattern: keyword + 3/4 digit number (e.g., toto8080, gacor666)
        self.keyword_number_pattern = re.compile(
            r'({})\d{{2,6}}'.format('|'.join(self.keywords)), 
            re.IGNORECASE
        )
        
        # Pattern: number + keyword (e.g., 888bet, 77slot)
        self.number_keyword_pattern = re.compile(
            r'\d{{2,6}}({})'.format('|'.join(self.keywords)),
            re.IGNORECASE
        )
        
        # Pattern: domain-like with suspicious TLD
        tld_pattern = '|'.join(self.suspicious_tlds)
        self.domain_pattern = re.compile(
            r'\b[\w-]+\.({})\b'.format(tld_pattern),
            re.IGNORECASE
        )
        
        # Pattern: WhatsApp/Telegram contact patterns
        self.contact_pattern = re.compile(
            r'(wa|whatsapp|telegram|tg|line|signal|chat|wechat|kakao|viber|fb|facebook|ig|instagram|dm|pm|sms|text|call|hubungi|kontak|contact)(.{0,5})?[:.]?(.{0,5})?\+?\d{8,15}',
            re.IGNORECASE
        )
        
        # Pattern: Percentage offers (e.g., "100% bonus")
        self.percentage_pattern = re.compile(
            r'\d{1,3}\s?%\s?(bonus|deposit|kemenangan|win|hadiah|cashback|diskon|potongan|rebate|komisi|rollingan|turnover|welcome|new|member)',
            re.IGNORECASE
        )
        
        # Pattern: Money symbols with numbers
        self.money_pattern = re.compile(
            r'(rp\.?|idr|usd|\$|€|£|¥|₹|₽|₩|₫|฿|₱|₴|₸|₼|₾|₺|₦|₡|₲|₴|₸|₼|₾|₺|₦|₡|₲)\s?\d[\d\.,]*\s?(juta|ribu|rb|k|m|b|t|million|billion|trillion|thousand)?',
            re.IGNORECASE
        )
        
        # Pattern: Repetitive characters (e.g., "$$$$", "!!!!!")
        self.repetitive_pattern = re.compile(r'(.)\1{3,}')
        
        # Pattern: Common gambling site name patterns
        name_pattern_parts = []
        for prefix, infix, suffix in self.name_patterns:
            if prefix and infix and suffix:
                name_pattern_parts.append(f"{prefix}[\\w-]*{infix}[\\w-]*{suffix}")
            elif prefix and infix:
                name_pattern_parts.append(f"{prefix}[\\w-]*{infix}")
            elif infix and suffix:
                name_pattern_parts.append(f"{infix}[\\w-]*{suffix}")
            elif prefix and suffix:
                name_pattern_parts.append(f"{prefix}[\\w-]*{suffix}")
            elif prefix:
                name_pattern_parts.append(f"{prefix}[\\w-]+")
            elif infix:
                name_pattern_parts.append(f"[\\w-]*{infix}[\\w-]*")
            elif suffix:
                name_pattern_parts.append(f"[\\w-]+{suffix}")
        
        self.name_pattern = re.compile(
            r'\b({})\b'.format('|'.join(name_pattern_parts)),
            re.IGNORECASE
        )
        
        # Pattern: Common number patterns in gambling sites
        self.number_pattern = re.compile(
            r'\b({})\b'.format('|'.join(self.common_numbers)),
            re.IGNORECASE
        )
        
        # Pattern: URL shorteners commonly used in gambling ads
        self.url_shortener_pattern = re.compile(
            r'\b(bit\.ly|tinyurl\.com|goo\.gl|t\.co|is\.gd|cli\.gs|ow\.ly|adfly|adf\.ly|shorturl\.at|cutt\.ly|tiny\.cc|tinyurl|rebrand\.ly|buff\.ly|snip\.ly|bl\.ink|short\.io)\b',
            re.IGNORECASE
        )
        
        # Pattern: Link text patterns
        self.link_text_pattern = re.compile(
            r'\b(klik|click|tap|tekan|pencet|kunjungi|visit|akses|access|buka|open|masuk|enter|join|gabung|daftar|register|link|url|website|situs|alternatif|alternative|resmi|official|terbaru|newest|terkini|updated)\b',
            re.IGNORECASE
        )
        
        # Pattern: Time availability patterns
        self.time_pattern = re.compile(
            r'\b(24\s?jam|24\s?hour|24\s?h|24\/7|nonstop|non\s?stop|online24jam|jam24|h24|selalu\s?online|always\s?online|setiap\s?hari|setiap\s?saat|kapan\s?saja|kapan\s?pun)\b',
            re.IGNORECASE
        )
        
        # Pattern: Support contact patterns
        self.support_pattern = re.compile(
            r'\b(cs|customer\s?service|customer\s?support|layanan\s?pelanggan|bantuan|help|support|livechat|live\s?chat|admin|operator|staff|pelayanan|layanan|contact|kontak)\b',
            re.IGNORECASE
        )
        
        # Pattern: Promotional language patterns
        self.promo_pattern = re.compile(
            r'\b(promo|promosi|bonus|diskon|discount|cashback|rebate|rollingan|turnover|komisi|referral|affiliate|member|vip|welcome|newmember|new\s?member|harian|daily|mingguan|weekly|bulanan|monthly|gratis|free|extra)\b',
            re.IGNORECASE
        )
        
        # Pattern: Trust signal patterns
        self.trust_pattern = re.compile(
            r'\b(terpercaya|trusted|aman|safe|secure|resmi|official|terbaik|best|recommended|direkomendasikan|terbukti|proven|terjamin|guaranteed|legal|lisensi|license|verified|terverifikasi|fair|adil)\b',
            re.IGNORECASE
        )
        
        # Pattern: Urgency patterns
        self.urgency_pattern = re.compile(
            r'\b(segera|hurry|cepat|quick|langsung|direct|sekarang|now|jangan|don\'t|tunggu|wait|buruan|hurry|terbatas|limited|special|spesial|khusus|exclusive|eksklusif)\b',
            re.IGNORECASE
        )
        
        # Pattern: Common provider names
        self.provider_pattern = re.compile(
            r'\b(pragmatic|habanero|spadegaming|microgaming|playtech|pgsoft|joker|netent|playngo|redtiger|evolution|idnlive|idnpoker|idnslot|idnsport|bti|sbobet|cmd368|opus|saba|wbet|allbet|dreamgaming|sexygaming|biggaming|asiagaming|ebet|ezugi|gameplay|cq9|jdb|jili|kagaming|live22|playstar|skywind|spade|toptrend|virtualtech|yggdrasil)\b',
            re.IGNORECASE
        )
        
        # Pattern: Obfuscated text (using special characters to replace letters)
        obfuscation_pattern_parts = []
        for char, replacements in self.obfuscation_chars.items():
            for replacement in replacements:
                obfuscation_pattern_parts.append(f"{replacement}")

        if obfuscation_pattern_parts:
            self.obfuscation_pattern = re.compile(
                r'[{}]'.format(''.join(obfuscation_pattern_parts)),
                re.IGNORECASE
            )
        else:
            self.obfuscation_pattern = None
        
    def normalize_text(self, text: str) -> str:
        """
        Normalize text by removing spaces, converting to lowercase,
        and normalizing Unicode characters.
        """
        # Remove spaces and join characters
        text = ''.join(text.split())
        # Convert to normal form (NFKC) to handle fullwidth and stylized fonts
        text = unicodedata.normalize('NFKC', text)
        return text.lower()
    
    def extract_words(self, text: str) -> List[str]:
        """
        Extract all "words" from text, handling various separators.
        """
        # Remove non-letter/number except spaces
        cleaned = re.sub(r'[^\w\s]', ' ', text)
        # Split by spaces and filter empty strings
        return [word for word in cleaned.split() if word]
    
    def get_ascii_equivalent(self, text: str) -> str:
        """
        Convert Unicode characters to their closest ASCII equivalents.
        """
        # Convert each char to closest ASCII if possible
        ascii_text = ''.join(
            c for c in unicodedata.normalize('NFKD', text)
            if not unicodedata.combining(c)
        )
        return ascii_text
    

    def deobfuscate_text(self, text: str) -> str:
        """
        Attempt to deobfuscate text by replacing common character substitutions.
        """
        deobfuscated = text.lower()
        
        # Replace common character substitutions
        char_map = {
            '4': 'a', '@': 'a', '8': 'b', '(': 'c', '3': 'e', '€': 'e',
            '6': 'g', '9': 'g', '1': 'i', '!': 'i', '|': 'i', '0': 'o',
            '5': 's', '$': 's', '7': 't', '+': 't', '2': 'z', 'ß': 'b',
            'µ': 'u', '¥': 'y',
            # Additional character substitutions
            '₽': 'p', '₱': 'p', '₹': 'r', '₳': 'a', '₴': 's',
            '₭': 'k', '₦': 'n', '₩': 'w', '₮': 't', '₲': 'g',
            '₵': 'c', '₸': 't', '₼': 'm', '₾': 'l', '℃': 'c',
            '℉': 'f', '℗': 'p', '℠': 'sm', '℡': 'tel', '™': 'tm',
            '℧': 'u', '℮': 'e', 'ℰ': 'e', 'ℱ': 'f', 'ℳ': 'm',
            'ℴ': 'o', '⅓': '1/3', '⅔': '2/3', '⅕': '1/5',
            # Stylized letters
            '𝐚': 'a', '𝐛': 'b', '𝐜': 'c', '𝐝': 'd', '𝐞': 'e',
            '𝐟': 'f', '𝐠': 'g', '𝐡': 'h', '𝐢': 'i', '𝐣': 'j',
            '𝐤': 'k', '𝐥': 'l', '𝐦': 'm', '𝐧': 'n', '𝐨': 'o',
            '𝐩': 'p', '𝐪': 'q', '𝐫': 'r', '𝐬': 's', '𝐭': 't',
            '𝐮': 'u', '𝐯': 'v', '𝐰': 'w', '𝐱': 'x', '𝐲': 'y', '𝐳': 'z',
            # Bold letters
            '𝗮': 'a', '𝗯': 'b', '𝗰': 'c', '𝗱': 'd', '𝗲': 'e',
            '𝗳': 'f', '𝗴': 'g', '𝗵': 'h', '𝗶': 'i', '𝗷': 'j',
            '𝗸': 'k', '𝗹': 'l', '𝗺': 'm', '𝗻': 'n', '𝗼': 'o',
            '𝗽': 'p', '𝗾': 'q', '𝗿': 'r', '𝘀': 's', '𝘁': 't',
            '𝘂': 'u', '𝘃': 'v', '𝘄': 'w', '𝘅': 'x', '𝘆': 'y', '𝘇': 'z',
            # Italic letters
            '𝘢': 'a', '𝘣': 'b', '𝘤': 'c', '𝘥': 'd', '𝘦': 'e',
            '𝘧': 'f', '𝘨': 'g', '𝘩': 'h', '𝘪': 'i', '𝘫': 'j',
            '𝘬': 'k', '𝘭': 'l', '𝘮': 'm', '𝘯': 'n', '𝘰': 'o',
            '𝘱': 'p', '𝘲': 'q', '𝘳': 'r', '𝘴': 's', '𝘵': 't',
            '𝘶': 'u', '𝘷': 'v', '𝘸': 'w', '𝘹': 'x', '𝘺': 'y', '𝘻': 'z',
            # Script letters
            '𝓪': 'a', '𝓫': 'b', '𝓬': 'c', '𝓭': 'd', '𝓮': 'e',
            '𝓯': 'f', '𝓰': 'g', '𝓱': 'h', '𝓲': 'i', '𝓳': 'j',
            '𝓴': 'k', '𝓵': 'l', '𝓶': 'm', '𝓷': 'n', '𝓸': 'o',
            '𝓹': 'p', '𝓺': 'q', '𝓻': 'r', '𝓼': 's', '𝓽': 't',
            '𝓾': 'u', '𝓿': 'v', '𝔀': 'w', '𝔁': 'x', '𝔂': 'y', '𝔃': 'z',
            # Fullwidth characters
            'ａ': 'a', 'ｂ': 'b', 'ｃ': 'c', 'ｄ': 'd', 'ｅ': 'e',
            'ｆ': 'f', 'ｇ': 'g', 'ｈ': 'h', 'ｉ': 'i', 'ｊ': 'j',
            'ｋ': 'k', 'ｌ': 'l', 'ｍ': 'm', 'ｎ': 'n', 'ｏ': 'o',
            'ｐ': 'p', 'ｑ': 'q', 'ｒ': 'r', 'ｓ': 's', 'ｔ': 't',
            'ｕ': 'u', 'ｖ': 'v', 'ｗ': 'w', 'ｘ': 'x', 'ｙ': 'y', 'ｚ': 'z',
            # Circled letters
            'ⓐ': 'a', 'ⓑ': 'b', 'ⓒ': 'c', 'ⓓ': 'd', 'ⓔ': 'e',
            'ⓕ': 'f', 'ⓖ': 'g', 'ⓗ': 'h', 'ⓘ': 'i', 'ⓙ': 'j',
            'ⓚ': 'k', 'ⓛ': 'l', 'ⓜ': 'm', 'ⓝ': 'n', 'ⓞ': 'o',
            'ⓟ': 'p', 'ⓠ': 'q', 'ⓡ': 'r', 'ⓢ': 's', 'ⓣ': 't',
            'ⓤ': 'u', 'ⓥ': 'v', 'ⓦ': 'w', 'ⓧ': 'x', 'ⓨ': 'y', 'ⓩ': 'z',
            # Common number substitutions in gambling ads
            '⓵': '1', '⓶': '2', '⓷': '3', '⓸': '4', '⓹': '5',
            '⓺': '6', '⓻': '7', '⓼': '8', '⓽': '9', '⓾': '10',
            '①': '1', '②': '2', '③': '3', '④': '4', '⑤': '5',
            '⑥': '6', '⑦': '7', '⑧': '8', '⑨': '9', '⑩': '10',
            # Accented characters
            'á': 'a', 'à': 'a', 'â': 'a', 'ä': 'a', 'ã': 'a', 'å': 'a',
            'é': 'e', 'è': 'e', 'ê': 'e', 'ë': 'e',
            'í': 'i', 'ì': 'i', 'î': 'i', 'ï': 'i',
            'ó': 'o', 'ò': 'o', 'ô': 'o', 'ö': 'o', 'õ': 'o',
            'ú': 'u', 'ù': 'u', 'û': 'u', 'ü': 'u',
            'ý': 'y', 'ÿ': 'y',
            'ç': 'c', 'ñ': 'n',
            # Common gambling site name obfuscations
            '₮○₮○': 'toto', '₲₳₵○Ɽ': 'gacor', '$ŁØ₮': 'slot', 'ĴɄĐł': 'judi',
            'Ç₳$łⱤØ': 'casino', 'Ɉ₳ÇҜ₱Ø₮': 'jackpot', 'ⱮⱯӾ₩łⱤ': 'maxwin',
            'Ɽ₮₱': 'rtp', '₱ØŁ₳': 'pola', '$₱łⱤ': 'spin', 'ƀɆ₮': 'bet',
            'ƀØŁ₳': 'bola', '₱ØҜɆⱤ': 'poker', 'ŁØ₮₮ɆⱤɎ': 'lottery',
            '₮Ø₲ɆŁ': 'togel', 'VɆ₲₳$': 'vegas'
        }
        
        # Apply character substitutions
        for obfuscated, clear in char_map.items():
            deobfuscated = deobfuscated.replace(obfuscated, clear)
        
        # Handle zero-width spaces and other invisible characters
        invisible_chars = ['\u200b', '\u200c', '\u200d', '\u2060', '\u2061', '\u2062', '\u2063', '\u2064', '\ufeff']
        for char in invisible_chars:
            deobfuscated = deobfuscated.replace(char, '')
        
        # Normalize spacing (remove excessive spaces)
        deobfuscated = re.sub(r'\s+', ' ', deobfuscated)
        
        # Handle deliberate spacing between letters (e.g., "T O T O")
        # First check for patterns like "X Y Z" where X, Y, Z are single letters
        spaced_word_pattern = re.compile(r'\b([a-z])\s+([a-z])\s+([a-z])\s+([a-z])\b')
        while spaced_word_pattern.search(deobfuscated):
            deobfuscated = spaced_word_pattern.sub(r'\1\2\3\4', deobfuscated)
        
        # Handle shorter patterns
        spaced_word_pattern = re.compile(r'\b([a-z])\s+([a-z])\s+([a-z])\b')
        while spaced_word_pattern.search(deobfuscated):
            deobfuscated = spaced_word_pattern.sub(r'\1\2\3', deobfuscated)
        
        # Handle two-letter patterns
        spaced_word_pattern = re.compile(r'\b([a-z])\s+([a-z])\b')
        while spaced_word_pattern.search(deobfuscated):
            deobfuscated = spaced_word_pattern.sub(r'\1\2', deobfuscated)
        
        # Handle digit spacing in common patterns (e.g., "8 0 8 0")
        spaced_digits_pattern = re.compile(r'\b(\d)\s+(\d)\s+(\d)\s+(\d)\b')
        while spaced_digits_pattern.search(deobfuscated):
            deobfuscated = spaced_digits_pattern.sub(r'\1\2\3\4', deobfuscated)
        
        # Handle shorter digit patterns
        spaced_digits_pattern = re.compile(r'\b(\d)\s+(\d)\s+(\d)\b')
        while spaced_digits_pattern.search(deobfuscated):
            deobfuscated = spaced_digits_pattern.sub(r'\1\2\3', deobfuscated)
        
        # Handle two-digit patterns
        spaced_digits_pattern = re.compile(r'\b(\d)\s+(\d)\b')
        while spaced_digits_pattern.search(deobfuscated):
            deobfuscated = spaced_digits_pattern.sub(r'\1\2', deobfuscated)
        
        # Handle mixed letter-digit patterns (e.g., "T O T O 8 8")
        mixed_pattern = re.compile(r'\b([a-z])\s+([a-z])\s+([a-z])\s+([a-z])\s+(\d)\s+(\d)\b')
        while mixed_pattern.search(deobfuscated):
            deobfuscated = mixed_pattern.sub(r'\1\2\3\4\5\6', deobfuscated)
        
        # Handle common gambling site name variations with dots or dashes
        site_pattern = re.compile(r'\b(t[o0]t[o0]|g[a4]c[o0]r|sl[o0]t|jud[i1]|c[a4]s[i1]n[o0]|j[a4]ckp[o0]t|m[a4]xw[i1]n|rtp|p[o0]l[a4]|sp[i1]n|b[e3]t|b[o0]l[a4])[-_.]([\w\d]{3,5})\b')
        deobfuscated = site_pattern.sub(r'\1\2', deobfuscated)
        
        # Handle common gambling site name variations with numbers
        site_num_pattern = re.compile(r'\b(t[o0]t[o0]|g[a4]c[o0]r|sl[o0]t|jud[i1]|c[a4]s[i1]n[o0]|j[a4]ckp[o0]t|m[a4]xw[i1]n)[-_.]?(\d{3,4})\b')
        deobfuscated = site_num_pattern.sub(r'\1\2', deobfuscated)
        
        # Handle common gambling terms with deliberate misspellings
        misspellings = {
            'totoo': 'toto', 'totto': 'toto', 't0t0': 'toto', 't0to': 'toto', 'tot0': 'toto',
            'gacorr': 'gacor', 'gac0r': 'gacor', 'gacoor': 'gacor', 'gakor': 'gacor',
            'slott': 'slot', 'sl0t': 'slot', 'sloot': 'slot', 'slt': 'slot',
            'judii': 'judi', 'jud1': 'judi', 'juudi': 'judi', 'jdi': 'judi',
            'casinoo': 'casino', 'cas1no': 'casino', 'casin0': 'casino', 'kasino': 'casino',
            'jackpott': 'jackpot', 'jackp0t': 'jackpot', 'jakpot': 'jackpot',
            'maxwinn': 'maxwin', 'maxw1n': 'maxwin', 'maxw1nn': 'maxwin',
            'rtpp': 'rtp', 'r.t.p': 'rtp', 'r-t-p': 'rtp',
            'polaa': 'pola', 'p0la': 'pola', 'poola': 'pola',
            'spinn': 'spin', 'sp1n': 'spin', 'spiin': 'spin',
            'bett': 'bet', 'b3t': 'bet', 'beet': 'bet',
            'bolaa': 'bola', 'b0la': 'bola', 'boola': 'bola'
        }
        
        for misspelled, correct in misspellings.items():
            deobfuscated = re.sub(r'\b' + misspelled + r'\b', correct, deobfuscated)
        
        return deobfuscated
