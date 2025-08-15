import httpx
import asyncio
import os
import traceback
from typing import List, Optional, Dict, Set
from sqlalchemy.orm import Session
from database.models import Article, NewsSource
from datetime import datetime, timedelta
import json
import feedparser
from dateutil import parser
from utils.cache import cache
import logging
import re
from collections import defaultdict
import hashlib
from concurrent.futures import ThreadPoolExecutor
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnhancedNewsService:
    def __init__(self):
        self.news_api_key = os.getenv("NEWS_API_KEY")
        self.gnews_api_key = os.getenv("GNEWS_API_KEY")
        self.mediastack_key = os.getenv("MEDIASTACK_API_KEY")
        self.currents_api_key = os.getenv("CURRENTS_API_KEY")
        
        # Performance tracking
        self.feed_performance = defaultdict(list)
        self.failed_feeds = set()
        
        # Topic classification keywords
        self.topic_keywords = {
            'technology': [
                'tech', 'technology', 'ai', 'artificial intelligence', 'machine learning', 'blockchain',
                'cryptocurrency', 'bitcoin', 'software', 'hardware', 'computer', 'internet', 'digital',
                'startup', 'innovation', 'app', 'mobile', 'smartphone', 'gadget', 'robot', 'automation',
                'cloud', 'data', 'cyber', 'security', 'programming', 'coding', 'developer', 'silicon valley',
                'google', 'microsoft', 'apple', 'amazon', 'facebook', 'meta', 'tesla', 'spacex'
            ],
            'business': [
                'business', 'economy', 'economic', 'finance', 'financial', 'market', 'stock', 'investment',
                'banking', 'trade', 'commerce', 'industry', 'corporate', 'company', 'revenue', 'profit',
                'earnings', 'merger', 'acquisition', 'ipo', 'shares', 'dividend', 'inflation', 'gdp',
                'employment', 'jobs', 'unemployment', 'salary', 'wage', 'startup', 'entrepreneur',
                'venture capital', 'funding', 'valuation', 'nasdaq', 'dow jones', 'sensex', 'nifty',
                'tariff', 'tariffs', 'export', 'import', 'manufacturing', 'industrial', 'steel',
                'semiconductor', 'chips', 'supply chain', 'quarterly', 'annual', 'ceo', 'cfo',
                'board', 'bse', 'nse', 'rupee', 'dollar', 'currency', 'rbi', 'reserve bank',
                'interest rate', 'loan', 'credit', 'debt', 'fiscal', 'monetary', 'loss'
            ],
            'politics': [
                'politics', 'political', 'government', 'minister', 'prime minister', 'president', 'parliament',
                'congress', 'bjp', 'election', 'vote', 'voting', 'campaign', 'policy', 'law', 'legislation',
                'democracy', 'republic', 'constitution', 'supreme court', 'high court', 'judiciary',
                'cabinet', 'opposition', 'coalition', 'party', 'leader', 'governance', 'administration'
            ],
            'sports': [
                'sports', 'sport', 'cricket', 'football', 'soccer', 'tennis', 'basketball', 'hockey',
                'olympics', 'world cup', 'championship', 'tournament', 'match', 'game', 'player',
                'team', 'coach', 'stadium', 'league', 'ipl', 'fifa', 'uefa', 'nba', 'nfl', 'athlete',
                'medal', 'victory', 'defeat', 'score', 'goal', 'run', 'wicket', 'batting', 'bowling'
            ],
            'health': [
                'health', 'medical', 'medicine', 'doctor', 'hospital', 'patient', 'disease', 'virus',
                'vaccine', 'covid', 'pandemic', 'epidemic', 'treatment', 'therapy', 'drug', 'pharmaceutical',
                'healthcare', 'wellness', 'fitness', 'nutrition', 'diet', 'mental health', 'surgery',
                'research', 'clinical', 'diagnosis', 'symptom', 'cure', 'prevention', 'who', 'fda'
            ],
            'science': [
                'science', 'scientific', 'research', 'study', 'discovery', 'experiment', 'laboratory',
                'scientist', 'physics', 'chemistry', 'biology', 'astronomy', 'space', 'nasa', 'isro',
                'satellite', 'rocket', 'mars', 'moon', 'planet', 'universe', 'climate', 'environment',
                'ecology', 'conservation', 'renewable', 'solar', 'wind', 'energy', 'nuclear', 'quantum'
            ],
            'entertainment': [
                'entertainment', 'movie', 'film', 'cinema', 'bollywood', 'hollywood', 'actor', 'actress',
                'director', 'music', 'song', 'album', 'concert', 'show', 'television', 'tv', 'series',
                'celebrity', 'star', 'award', 'oscar', 'grammy', 'festival', 'theatre', 'dance', 'art',
                'culture', 'book', 'author', 'novel', 'literature', 'gaming', 'video game'
            ],
            'education': [
                'education', 'school', 'college', 'university', 'student', 'teacher', 'professor',
                'academic', 'curriculum', 'exam', 'test', 'degree', 'graduation', 'admission',
                'scholarship', 'learning', 'knowledge', 'skill', 'training', 'course', 'class',
                'iit', 'iim', 'nit', 'cbse', 'icse', 'ugc', 'aicte', 'research', 'phd', 'masters'
            ]
        }
        
        # Comprehensive RSS feeds with categorization
        self.rss_feeds = {
            'indian_national': [
                {"name": "Times of India", "url": "https://timesofindia.indiatimes.com/rss.cms", "source": "Times of India", "reliability": 0.9, "category": "general"},
                {"name": "The Hindu", "url": "https://www.thehindu.com/news/national/feeder/default.rss", "source": "The Hindu", "reliability": 0.95, "category": "general"},
                {"name": "Indian Express", "url": "https://indianexpress.com/feed", "source": "Indian Express", "reliability": 0.9, "category": "general"},
                {"name": "Hindustan Times", "url": "https://www.hindustantimes.com/feeds/rss/top-news/rssfeed.xml", "source": "Hindustan Times", "reliability": 0.85, "category": "general"},
                {"name": "NDTV", "url": "https://feeds.feedburner.com/ndtvnews-top-stories", "source": "NDTV", "reliability": 0.9, "category": "general"},
                {"name": "India Today", "url": "https://indiatoday.in/rss/1206578", "source": "India Today", "reliability": 0.85, "category": "general"},
                {"name": "News18", "url": "https://www.news18.com/rss/", "source": "News18", "reliability": 0.8, "category": "general"},
                {"name": "Republic World", "url": "https://www.republicworld.com/rss/latest-news.xml", "source": "Republic World", "reliability": 0.75, "category": "general"},
                {"name": "Zee News", "url": "http://zeenews.india.com/rss/india-national-news.xml", "source": "Zee News", "reliability": 0.7, "category": "general"},
                {"name": "Firstpost", "url": "https://www.firstpost.com/rss/", "source": "Firstpost", "reliability": 0.8, "category": "general"},
                {"name": "The Quint", "url": "https://www.thequint.com/rss", "source": "The Quint", "reliability": 0.85, "category": "general"},
                {"name": "Scroll.in", "url": "https://scroll.in/feeds/all.rss", "source": "Scroll.in", "reliability": 0.9, "category": "general"},
                {"name": "The Wire", "url": "https://thewire.in/feed", "source": "The Wire", "reliability": 0.85, "category": "general"},
                {"name": "National Herald", "url": "https://www.nationalheraldindia.com/rss", "source": "National Herald", "reliability": 0.75, "category": "general"},
                {"name": "Outlook India", "url": "https://www.outlookindia.com/rss/main", "source": "Outlook India", "reliability": 0.8, "category": "general"}
            ],
            'indian_business': [
                {"name": "Economic Times", "url": "https://economictimes.indiatimes.com/rssfeedstopstories.cms", "source": "Economic Times", "reliability": 0.95, "category": "business"},
                {"name": "Live Mint", "url": "https://www.livemint.com/rss/news", "source": "Live Mint", "reliability": 0.9, "category": "business"},
                {"name": "Business Standard", "url": "https://www.business-standard.com/rss", "source": "Business Standard", "reliability": 0.9, "category": "business"},
                {"name": "Moneycontrol", "url": "https://www.moneycontrol.com/rss/latestnews.xml", "source": "Moneycontrol", "reliability": 0.85, "category": "business"},
                {"name": "Financial Express", "url": "https://www.financialexpress.com/feed/", "source": "Financial Express", "reliability": 0.85, "category": "business"},
                {"name": "BloombergQuint", "url": "https://www.bloombergquint.com/feed", "source": "BloombergQuint", "reliability": 0.9, "category": "business"},
                {"name": "ET Now", "url": "https://www.etnow.in/rss", "source": "ET Now", "reliability": 0.8, "category": "business"},
                {"name": "Zee Business", "url": "https://www.zeebiz.com/rss/india-news.xml", "source": "Zee Business", "reliability": 0.75, "category": "business"}
            ],
            'indian_technology': [
                {"name": "ET Tech", "url": "https://tech.economictimes.indiatimes.com/rss/topstories", "source": "ET Tech", "reliability": 0.9, "category": "technology"},
                {"name": "TechCircle", "url": "https://www.techcircle.in/rss", "source": "TechCircle", "reliability": 0.85, "category": "technology"},
                {"name": "Inc42", "url": "https://inc42.com/feed/", "source": "Inc42", "reliability": 0.8, "category": "technology"},
                {"name": "YourStory", "url": "https://yourstory.com/feed", "source": "YourStory", "reliability": 0.8, "category": "technology"},
                {"name": "Gadgets 360", "url": "https://gadgets.ndtv.com/rss/news", "source": "Gadgets 360", "reliability": 0.85, "category": "technology"},
                {"name": "91mobiles", "url": "https://www.91mobiles.com/rss", "source": "91mobiles", "reliability": 0.75, "category": "technology"},
                {"name": "Digit", "url": "https://www.digit.in/rss", "source": "Digit", "reliability": 0.8, "category": "technology"},
                {"name": "Analytics India Magazine", "url": "https://analyticsindiamag.com/feed/", "source": "Analytics India Magazine", "reliability": 0.85, "category": "technology"}
            ],
            'indian_sports': [
                {"name": "Sportstar", "url": "https://sportstar.thehindu.com/rss/", "source": "Sportstar", "reliability": 0.9, "category": "sports"},
                {"name": "TOI Sports", "url": "https://timesofindia.indiatimes.com/rss/sports/rssfeedstopstories.cms", "source": "TOI Sports", "reliability": 0.85, "category": "sports"},
                {"name": "NDTV Sports", "url": "https://sports.ndtv.com/rss/news", "source": "NDTV Sports", "reliability": 0.85, "category": "sports"},
                {"name": "myKhel", "url": "https://www.mykhel.com/rss/cricket/feed.xml", "source": "myKhel", "reliability": 0.75, "category": "sports"},
                {"name": "Sportskeeda", "url": "https://www.sportskeeda.com/rss", "source": "Sportskeeda", "reliability": 0.8, "category": "sports"}
            ],
            'international_general': [
                {"name": "BBC World", "url": "https://feeds.bbci.co.uk/news/world/rss.xml", "source": "BBC", "reliability": 0.95, "category": "general"},
                {"name": "Reuters", "url": "http://feeds.reuters.com/reuters/topNews", "source": "Reuters", "reliability": 0.95, "category": "general"},
                {"name": "CNN International", "url": "http://rss.cnn.com/rss/edition.rss", "source": "CNN", "reliability": 0.9, "category": "general"},
                {"name": "Al Jazeera", "url": "https://www.aljazeera.com/xml/rss/all.xml", "source": "Al Jazeera", "reliability": 0.85, "category": "general"},
                {"name": "The Guardian", "url": "https://www.theguardian.com/world/rss", "source": "The Guardian", "reliability": 0.9, "category": "general"},
                {"name": "Associated Press", "url": "https://feeds.apnews.com/rss/apf-topnews", "source": "Associated Press", "reliability": 0.95, "category": "general"},
                {"name": "NPR", "url": "https://feeds.npr.org/1001/rss.xml", "source": "NPR", "reliability": 0.9, "category": "general"},
                {"name": "France24", "url": "https://www.france24.com/en/rss", "source": "France24", "reliability": 0.85, "category": "general"},
                {"name": "Deutsche Welle", "url": "http://rss.dw.com/rdf/rss-en-al", "source": "Deutsche Welle", "reliability": 0.85, "category": "general"}
            ],
            'international_technology': [
                {"name": "TechCrunch", "url": "https://techcrunch.com/feed/", "source": "TechCrunch", "reliability": 0.9, "category": "technology"},
                {"name": "Ars Technica", "url": "http://feeds.arstechnica.com/arstechnica/index", "source": "Ars Technica", "reliability": 0.9, "category": "technology"},
                {"name": "The Verge", "url": "https://www.theverge.com/rss/index.xml", "source": "The Verge", "reliability": 0.85, "category": "technology"},
                {"name": "Wired", "url": "https://www.wired.com/feed/rss", "source": "Wired", "reliability": 0.9, "category": "technology"},
                {"name": "Engadget", "url": "https://www.engadget.com/rss.xml", "source": "Engadget", "reliability": 0.8, "category": "technology"},
                {"name": "MIT Technology Review", "url": "https://www.technologyreview.com/feed/", "source": "MIT Technology Review", "reliability": 0.95, "category": "technology"},
                {"name": "VentureBeat", "url": "https://venturebeat.com/feed/", "source": "VentureBeat", "reliability": 0.85, "category": "technology"}
            ],
            'international_business': [
                {"name": "Bloomberg", "url": "https://feeds.bloomberg.com/markets/news.rss", "source": "Bloomberg", "reliability": 0.95, "category": "business"},
                {"name": "Financial Times", "url": "https://www.ft.com/rss/home", "source": "Financial Times", "reliability": 0.95, "category": "business"},
                {"name": "Wall Street Journal", "url": "https://feeds.a.dj.com/rss/RSSWorldNews.xml", "source": "Wall Street Journal", "reliability": 0.95, "category": "business"},
                {"name": "Forbes", "url": "https://www.forbes.com/real-time/feed2/", "source": "Forbes", "reliability": 0.85, "category": "business"},
                {"name": "MarketWatch", "url": "http://feeds.marketwatch.com/marketwatch/topstories/", "source": "MarketWatch", "reliability": 0.8, "category": "business"}
            ],
            'science_health': [
                {"name": "Nature News", "url": "http://feeds.nature.com/nature/rss/current", "source": "Nature", "reliability": 0.95, "category": "science"},
                {"name": "Science Daily", "url": "https://www.sciencedaily.com/rss/all.xml", "source": "Science Daily", "reliability": 0.9, "category": "science"},
                {"name": "NASA News", "url": "https://www.nasa.gov/rss/dyn/breaking_news.rss", "source": "NASA", "reliability": 0.95, "category": "science"},
                {"name": "WHO News", "url": "https://www.who.int/rss-feeds/news-english.xml", "source": "WHO", "reliability": 0.95, "category": "health"},
                {"name": "Medical News Today", "url": "https://www.medicalnewstoday.com/rss", "source": "Medical News Today", "reliability": 0.85, "category": "health"}
            ]
        }
        
        # Indian keywords for content classification
        self.indian_keywords = [
            'india', 'indian', 'delhi', 'mumbai', 'bangalore', 'chennai', 'kolkata', 'hyderabad',
            'pune', 'ahmedabad', 'surat', 'jaipur', 'lucknow', 'kanpur', 'nagpur', 'indore',
            'thane', 'bhopal', 'visakhapatnam', 'pimpri', 'patna', 'vadodara', 'ghaziabad',
            'ludhiana', 'agra', 'nashik', 'faridabad', 'meerut', 'rajkot', 'kalyan', 'vasai',
            'varanasi', 'srinagar', 'aurangabad', 'dhanbad', 'amritsar', 'navi mumbai',
            'allahabad', 'ranchi', 'howrah', 'coimbatore', 'jabalpur', 'gwalior', 'vijayawada',
            'jodhpur', 'madurai', 'raipur', 'kota', 'guwahati', 'chandigarh', 'solapur',
            'hubli', 'tiruchirappalli', 'bareilly', 'mysore', 'tiruppur', 'gurgaon', 'aligarh',
            'jalandhar', 'bhubaneswar', 'salem', 'warangal', 'guntur', 'bhiwandi', 'saharanpur',
            'gorakhpur', 'bikaner', 'amravati', 'noida', 'jamshedpur', 'bhilai', 'cuttack',
            'firozabad', 'kochi', 'nellore', 'bhavnagar', 'dehradun', 'durgapur', 'asansol',
            'rourkela', 'nanded', 'kolhapur', 'ajmer', 'akola', 'gulbarga', 'jamnagar',
            'ujjain', 'loni', 'siliguri', 'jhansi', 'ulhasnagar', 'jammu', 'sangli',
            'mangalore', 'erode', 'belgaum', 'ambattur', 'tirunelveli', 'malegaon', 'gaya',
            'jalgaon', 'udaipur', 'maheshtala', 'davanagere', 'kozhikode', 'kurnool',
            'rajpur sonarpur', 'rajahmundry', 'bokaro', 'south dumdum', 'bellary',
            'patiala', 'gopalpur', 'agartala', 'bhagalpur', 'muzaffarnagar', 'bhatpara',
            'panihati', 'latur', 'dhule', 'rohtak', 'korba', 'bhilwara', 'berhampur',
            'muzaffarpur', 'ahmednagar', 'mathura', 'kollam', 'avadi', 'kadapa', 'kamarhati',
            'sambalpur', 'bilaspur', 'shahjahanpur', 'satara', 'bijapur', 'rampur',
            'shivamogga', 'chandrapur', 'junagadh', 'thrissur', 'alwar', 'bardhaman',
            'kulti', 'kakinada', 'nizamabad', 'parbhani', 'tumkur', 'khammam', 'ozhukarai',
            'bihar sharif', 'panipat', 'darbhanga', 'bally', 'aizawl', 'dewas', 'ichalkaranji',
            'karnal', 'bathinda', 'jalna', 'eluru', 'kirari suleman nagar', 'barabanki',
            'purnia', 'satna', 'mau', 'sonipat', 'farrukhabad', 'sagar', 'rourkela',
            'durg', 'imphal', 'ratlam', 'hapur', 'arrah', 'anantapur', 'karimnagar',
            'etawah', 'ambernath', 'north dumdum', 'bharatpur', 'begusarai', 'new delhi',
            'gandhinagar', 'baranagar', 'tiruvottiyur', 'puducherry', 'sikar', 'thoothukudi',
            'rewa', 'mirzapur', 'raichur', 'pali', 'ramagundam', 'silchar', 'orai',
            'nandyal', 'morena', 'bhiwani', 'porbandar', 'palakkad', 'anand', 'puruliya',
            'baharampur', 'barmer', 'ambala', 'shivpuri', 'fatehpur', 'hindupur',
            'gonda', 'moga', 'abohar', 'kharagpur', 'naihati', 'sambalpur', 'hoshiarpur',
            'sasaram', 'hajipur', 'bhusawal', 'raiganj', 'machilipatnam', 'ongole',
            'deoghar', 'chapra', 'haldia', 'khandwa', 'morbi', 'mahbubnagar',
            'bharuch', 'berhampore', 'madhyamgram', 'bhind', 'malda', 'vellore',
            'jaunpur', 'kadapa', 'tirupati', 'karaikudi', 'rajnandgaon', 'yavatmal',
            'sri ganganagar', 'wardha', 'mango', 'thanjavur', 'dibrugarh', 'santipur',
            'kalyan-dombivali', 'vasai-virar', 'mira-bhayandar', 'thiruvananthapuram',
            'bhiwandi-nizampur', 'ahmednagar', 'haridwar', 'gwalior', 'pathankot',
            'chanda', 'baramula', 'adilabad', 'angul', 'chittoor', 'karimnagar',
            'ramagundam', 'miryalaguda', 'tadipatri', 'proddatur', 'machilipatnam',
            'bhimavaram', 'tadepalligudem', 'tenali', 'chilakaluripet', 'narasaraopet',
            'kavali', 'palacole', 'gudivada', 'sullurpeta', 'rayachoti', 'srikalahasti',
            'bapatla', 'rajam', 'bobbili', 'narasapuram', 'nuzvid', 'markapur',
            'ponnur', 'kandukur', 'vinukonda', 'repalle', 'kovvur', 'sattenapalle',
            'jaggaiahpet', 'tuni', 'amalapuram', 'bheemunipatnam', 'narasannapeta',
            'rajampet', 'kadiri', 'jammalamadugu', 'peddapuram', 'punganur',
            'naidupet', 'nagari', 'yemmiganur', 'dharmavaram', 'balayya sastry layout',
            'renigunta', 'madanapalle', 'venkatagiri', 'chandragiri', 'srikalahasti',
            'puttur', 'palamaner', 'kuppam', 'ramachandrapuram', 'palakollu',
            'bhimadole', 'tanuku', 'denduluru', 'narsapuram', 'tadepalligudem',
            'bhimavaram', 'narasaraopet', 'sattenapalle', 'chilakaluripet',
            'bapatla', 'repalle', 'tenali', 'guntur', 'mangalagiri', 'vijayawada',
            'machilipatnam', 'gudivada', 'nuzvid', 'mylavaram', 'tiruvuru',
            'nandigama', 'jaggayyapeta', 'vuyyuru', 'hanuman junction',
            'avanigadda', 'pedana', 'bantumilli', 'challapalli', 'mopidevi',
            'nagayalanka', 'ghantasala', 'kruthivennu', 'pedaparupudi',
            'movva', 'nidadavole', 'unguturu', 'kaikaluru', 'mudinepalli',
            'gudlavalleru', 'rippanpet', 'koduru', 'chatrai', 'kankipadu',
            'vissannapet', 'vatsavai', 'gampalagudem', 'pedakakani',
            'penamaluru', 'kanchikacherla', 'thotlavalluru', 'mandavalli',
            'ibrahimpatnam', 'gannavaram', 'mylavaram', 'agiripalli',
            'buckinghampet', 'reddigudem', 'kondapalli', 'nandigama',
            'tiruvuru', 'vuyyuru', 'hanuman junction', 'avanigadda',
            'pedana', 'bantumilli', 'challapalli', 'mopidevi', 'nagayalanka',
            'ghantasala', 'kruthivennu', 'pedaparupudi', 'movva', 'nidadavole',
            'unguturu', 'kaikaluru', 'mudinepalli', 'gudlavalleru', 'rippanpet',
            'koduru', 'chatrai', 'kankipadu', 'vissannapet', 'vatsavai',
            'gampalagudem', 'pedakakani', 'penamaluru', 'kanchikacherla',
            'thotlavalluru', 'mandavalli', 'ibrahimpatnam', 'gannavaram',
            'mylavaram', 'agiripalli', 'buckinghampet', 'reddigudem',
            'kondapalli', 'bjp', 'congress', 'aap', 'tmc', 'dmk', 'aiadmk',
            'bsp', 'sp', 'rjd', 'jdu', 'shiv sena', 'ncp', 'cpi', 'cpm',
            'modi', 'rahul gandhi', 'amit shah', 'mamata banerjee',
            'arvind kejriwal', 'nitish kumar', 'lalu prasad', 'mayawati',
            'akhilesh yadav', 'uddhav thackeray', 'sharad pawar',
            'lok sabha', 'rajya sabha', 'parliament', 'assembly',
            'election commission', 'supreme court', 'high court',
            'reserve bank', 'rbi', 'sebi', 'cbi', 'ed', 'income tax',
            'gst', 'aadhar', 'pan', 'epf', 'esi', 'nrega', 'jan dhan',
            'ayushman bharat', 'swachh bharat', 'digital india',
            'make in india', 'skill india', 'startup india',
            'stand up india', 'mudra', 'pradhan mantri', 'chief minister',
            'governor', 'president', 'vice president', 'speaker',
            'deputy speaker', 'leader of opposition', 'cabinet minister',
            'state minister', 'mla', 'mp', 'mcd', 'panchayat', 'sarpanch',
            'collector', 'dm', 'sp', 'dsp', 'ias', 'ips', 'ifs', 'irs',
            'upsc', 'ssc', 'railway', 'isro', 'drdo', 'ongc', 'ntpc',
            'bhel', 'sail', 'coal india', 'oil india', 'gail', 'iocl',
            'bpcl', 'hpcl', 'ril', 'tata', 'birla', 'ambani', 'adani',
            'wipro', 'infosys', 'tcs', 'hcl', 'tech mahindra',
            'mahindra', 'bajaj', 'hero', 'maruti', 'hyundai',
            'honda', 'toyota', 'ford', 'volkswagen', 'bmw',
            'mercedes', 'audi', 'jaguar', 'land rover',
            'bollywood', 'tollywood', 'kollywood', 'mollywood',
            'sandalwood', 'pollywood', 'bhojpuri', 'marathi',
            'gujarati', 'punjabi', 'tamil', 'telugu', 'kannada',
            'malayalam', 'bengali', 'assamese', 'odia', 'hindi',
            'english', 'urdu', 'sanskrit', 'pali', 'prakrit',
            'vedic', 'upanishad', 'gita', 'ramayana', 'mahabharata',
            'puranas', 'vedas', 'hinduism', 'buddhism', 'jainism',
            'sikhism', 'islam', 'christianity', 'zoroastrianism',
            'judaism', 'bahai', 'temple', 'mosque', 'church',
            'gurudwara', 'monastery', 'ashram', 'math', 'akhara',
            'kumbh', 'diwali', 'holi', 'dussehra', 'navratri',
            'karva chauth', 'raksha bandhan', 'janmashtami',
            'ram navami', 'shivratri', 'ganesh chaturthi',
            'durga puja', 'kali puja', 'saraswati puja',
            'lakshmi puja', 'vishwakarma puja', 'jagannath rath yatra',
            'eid', 'muharram', 'christmas', 'good friday',
            'easter', 'guru nanak jayanti', 'guru gobind singh jayanti',
            'baisakhi', 'karva chauth', 'teej', 'onam', 'pongal',
            'makar sankranti', 'ugadi', 'gudi padwa', 'baisakhi',
            'poila boishakh', 'vishu', 'bihu', 'hornbill',
            'pushkar', 'ajmer', 'golden temple', 'vaishno devi',
            'tirupati', 'shirdi', 'rishikesh', 'haridwar',
            'varanasi', 'gaya', 'bodh gaya', 'sarnath',
            'kushinagar', 'lumbini', 'rajgir', 'nalanda',
            'vikramshila', 'takshashila', 'nagarjunakonda',
            'amaravati', 'sanchi', 'bharhut', 'mathura',
            'vrindavan', 'ayodhya', 'chitrakoot', 'prayagraj',
            'kashi', 'kedarnath', 'badrinath', 'gangotri',
            'yamunotri', 'char dham', 'amarnath', 'mata vaishno devi',
            'jwala devi', 'chintpurni', 'chamunda devi',
            'baglamukhi', 'kamleshwar', 'brajeshwari',
            'naina devi', 'mansa devi', 'chandi devi',
            'maya devi', 'kalka devi', 'shoolini devi',
            'jwalamukhi', 'kangra', 'kullu', 'manali',
            'shimla', 'dharamshala', 'mcleodganj', 'dalhousie',
            'kasauli', 'chail', 'kufri', 'narkanda',
            'sarahan', 'kalpa', 'chitkul', 'sangla',
            'tabo', 'kaza', 'keylong', 'leh', 'ladakh',
            'srinagar', 'gulmarg', 'pahalgam', 'sonamarg',
            'amarnath', 'vaishno devi', 'patnitop', 'bhaderwah',
            'kishtwar', 'doda', 'ramban', 'banihal',
            'qazigund', 'anantnag', 'pulwama', 'shopian',
            'kulgam', 'budgam', 'ganderbal', 'bandipora',
            'baramulla', 'kupwara', 'handwara', 'sopore',
            'uri', 'poonch', 'rajouri', 'jammu', 'kathua',
            'samba', 'udhampur', 'reasi', 'doda', 'kishtwar',
            'ramban', 'bhaderwah', 'batote', 'banihal',
            'qazigund', 'kokernag', 'verinag', 'achabal',
            'martand', 'avantipura', 'bijbehara', 'khanabal',
            'sangam', 'larnoo', 'breng', 'dooru', 'noorabad',
            'khovripora', 'yaripora', 'wanpoh', 'tral',
            'awantipora', 'pampore', 'kakapora', 'pulwama',
            'rajpora', 'shadimarg', 'tahab', 'ladhoo',
            'aripal', 'drangbal', 'pinglena', 'newa',
            'monghall', 'karimabad', 'lelhar', 'ratnipora',
            'rohmoo', 'murran', 'aglar', 'gudoora',
            'pastuna', 'heff', 'shirmal', 'drabgam',
            'samboora', 'bandzoo', 'koil', 'litter',
            'puchal', 'trichal', 'nehama', 'beerwah',
            'magam', 'charar', 'budgam', 'chadoora',
            'narbal', 'khansahib', 'beerwah', 'magam',
            'charar', 'budgam', 'chadoora', 'narbal',
            'khansahib', 'ganderbal', 'kangan', 'gund',
            'sonamarg', 'baltal', 'thajiwas', 'zojila',
            'drass', 'kargil', 'suru', 'zanskar',
            'padum', 'rangdum', 'parkachik', 'mulbekh',
            'lamayuru', 'alchi', 'likir', 'basgo',
            'nimmu', 'choglamsar', 'shey', 'thiksey',
            'hemis', 'chemrey', 'tak thok', 'sakti',
            'digar', 'khalsar', 'sumur', 'hundar',
            'diskit', 'hunder', 'turtuk', 'bogdang',
            'tyakshi', 'chalunka', 'panamik', 'ensa',
            'warshi', 'murgi', 'sasoma', 'partapur',
            'skampari', 'khardung', 'south pullu',
            'north pullu', 'tangtse', 'durbuk', 'lukung',
            'man', 'merak', 'chushul', 'demchok',
            'nyoma', 'loma', 'hanle', 'chumathang',
            'mahe', 'korzok', 'puga', 'tso kar',
            'tso moriri', 'karzok', 'puga', 'chumathang',
            'upshi', 'gya', 'miru', 'rumtse', 'pang',
            'debring', 'moore plains', 'tanglang la',
            'lachalung la', 'nakee la', 'taglang la',
            'baralacha la', 'rohtang', 'kunzum',
            'pin parvati', 'hampta', 'beas kund',
            'chandratal', 'suraj tal', 'deepak tal',
            'dhankar', 'tabo', 'kaza', 'mudh', 'hikkim',
            'komic', 'langza', 'comic', 'kibber',
            'gete', 'losar', 'keylong', 'jispa',
            'darcha', 'zingzing bar', 'sarchu', 'patseo',
            'whiskey nala', 'bharatpur', 'pang', 'debring',
            'moore plains', 'tanglang la', 'lachalung la',
            'nakee la', 'taglang la', 'baralacha la',
            'rohtang', 'kunzum', 'pin parvati', 'hampta',
            'beas kund', 'chandratal', 'suraj tal', 'deepak tal'
        ]

    async def classify_article_topic(self, title: str, content: str) -> str:
        """Classify article topic using improved keyword matching and content analysis"""
        title_lower = title.lower()
        content_lower = content.lower()
        text = f"{title_lower} {content_lower}"
        topic_scores = {}
        
        for topic, keywords in self.topic_keywords.items():
            score = 0
            keyword_matches = 0
            
            for keyword in keywords:
                keyword_lower = keyword.lower()
                
                # Exact phrase matching gets higher score
                if keyword_lower in title_lower:
                    score += 5  # Higher weight for title matches
                    keyword_matches += 1
                elif keyword_lower in content_lower:
                    score += 2  # Content matches
                    keyword_matches += 1
                
                # Word boundary matching for better accuracy
                import re
                if re.search(r'\b' + re.escape(keyword_lower) + r'\b', text):
                    score += 1
            
            # Bonus for multiple keyword matches
            if keyword_matches >= 2:
                score += keyword_matches * 2
            
            topic_scores[topic] = score
        
        # Return topic with highest score, with minimum threshold
        if topic_scores:
            best_topic = max(topic_scores, key=topic_scores.get)
            max_score = topic_scores[best_topic]
            
            # Require minimum score of 3 for classification
            if max_score >= 3:
                return best_topic
        
        return 'general'

    def is_indian_content(self, title: str, content: str, source: str = "") -> bool:
        """Determine if content is India-related"""
        text = f"{title} {content} {source}".lower()
        
        # Check for Indian keywords
        for keyword in self.indian_keywords:
            if keyword in text:
                return True
        
        return False

    async def fetch_rss_feed_with_timeout(self, feed: Dict, timeout: int = 10) -> List[dict]:
        """Fetch single RSS feed with timeout and error handling"""
        articles = []
        start_time = time.time()
        
        try:
            # Use asyncio timeout
            async with asyncio.timeout(timeout):
                # Parse RSS feed in thread pool to avoid blocking
                loop = asyncio.get_event_loop()
                with ThreadPoolExecutor(max_workers=1) as executor:
                    feed_data = await loop.run_in_executor(executor, feedparser.parse, feed['url'])
                
                if not feed_data.entries:
                    logger.warning(f"No entries found for feed {feed['name']}")
                    return articles
                
                for entry in feed_data.entries[:15]:  # Limit to 15 articles per feed
                    try:
                        # Parse date
                        published_at = ""
                        try:
                            if hasattr(entry, 'published'):
                                published_at = parser.parse(entry.published).isoformat()
                            elif hasattr(entry, 'updated'):
                                published_at = parser.parse(entry.updated).isoformat()
                            else:
                                published_at = datetime.now().isoformat()
                        except:
                            published_at = datetime.now().isoformat()
                        
                        title = getattr(entry, 'title', '').strip()
                        content = getattr(entry, 'summary', '').strip()
                        url = getattr(entry, 'link', '').strip()
                        
                        if not title or not url:
                            continue
                        
                        # Classify topic
                        topic = await self.classify_article_topic(title, content)
                        
                        # Check if Indian content
                        is_indian = self.is_indian_content(title, content, feed['source'])
                        
                        article = {
                            'id': None,  # RSS articles don't have database IDs
                            'title': title,
                            'description': content,
                            'content': content,
                            'url': url,
                            'published_at': published_at,
                            'source_name': f"RSS - {feed['source']}",
                            'source_bias_score': None,
                            'is_indian': is_indian,
                            'api_source': 'rss',
                            'topic': topic,
                            'summary': content[:200] + '...' if len(content) > 200 else content,  # Create summary from content
                            'feed_category': feed.get('category', 'general'),
                            'feed_reliability': feed.get('reliability', 0.8),
                            'image_url': getattr(entry, 'media_thumbnail', [{'url': ''}])[0].get('url', '') if hasattr(entry, 'media_thumbnail') else ''
                        }
                        
                        articles.append(article)
                        
                    except Exception as e:
                        logger.error(f"Error processing entry from {feed['name']}: {str(e)}")
                        continue
                
                # Track performance
                fetch_time = time.time() - start_time
                self.feed_performance[feed['name']].append(fetch_time)
                
                logger.info(f"✅ {feed['name']}: {len(articles)} articles in {fetch_time:.2f}s")
                
        except asyncio.TimeoutError:
            logger.error(f"❌ {feed['name']} timed out after {timeout}s")
            self.failed_feeds.add(feed['name'])
        except Exception as e:
            logger.error(f"❌ {feed['name']} failed: {str(e)}")
            self.failed_feeds.add(feed['name'])
        
        return articles

    async def fetch_all_rss_feeds(self, focus_indian: bool = True, topic_filter: Optional[str] = None) -> List[dict]:
        """Fetch from all RSS feeds concurrently with intelligent filtering"""
        all_articles = []
        tasks = []
        
        # Select feeds based on focus and topic
        selected_feeds = []
        
        if focus_indian:
            # Prioritize Indian feeds
            selected_feeds.extend(self.rss_feeds['indian_national'])
            selected_feeds.extend(self.rss_feeds['indian_business'])
            selected_feeds.extend(self.rss_feeds['indian_technology'])
            selected_feeds.extend(self.rss_feeds['indian_sports'])
            
            # Add some international feeds for diversity
            selected_feeds.extend(self.rss_feeds['international_general'][:5])
            selected_feeds.extend(self.rss_feeds['international_technology'][:3])
        else:
            # International focus
            selected_feeds.extend(self.rss_feeds['international_general'])
            selected_feeds.extend(self.rss_feeds['international_technology'])
            selected_feeds.extend(self.rss_feeds['international_business'])
            selected_feeds.extend(self.rss_feeds['science_health'])
            
            # Add some Indian feeds for diversity
            selected_feeds.extend(self.rss_feeds['indian_national'][:5])
        
        # Filter by topic if specified
        if topic_filter:
            topic_feeds = [feed for feed in selected_feeds if feed.get('category') == topic_filter]
            if topic_feeds:
                selected_feeds = topic_feeds
        
        # Remove failed feeds from recent attempts
        selected_feeds = [feed for feed in selected_feeds if feed['name'] not in self.failed_feeds]
        
        # Sort by reliability
        selected_feeds.sort(key=lambda x: x.get('reliability', 0.8), reverse=True)
        
        # Limit concurrent requests to avoid overwhelming servers
        semaphore = asyncio.Semaphore(10)
        
        async def fetch_with_semaphore(feed):
            async with semaphore:
                return await self.fetch_rss_feed_with_timeout(feed)
        
        # Create tasks for concurrent fetching
        tasks = [fetch_with_semaphore(feed) for feed in selected_feeds[:30]]  # Limit to 30 feeds
        
        logger.info(f"🚀 Fetching from {len(tasks)} RSS feeds...")
        
        # Execute all tasks concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        for result in results:
            if isinstance(result, Exception):
                logger.error(f"Feed fetch failed: {str(result)}")
                continue
            if isinstance(result, list):
                all_articles.extend(result)
        
        logger.info(f"📰 Total RSS articles fetched: {len(all_articles)}")
        
        return all_articles

    def remove_duplicates_advanced(self, articles: List[dict]) -> List[dict]:
        """Advanced duplicate removal using title similarity and URL matching"""
        unique_articles = []
        seen_urls = set()
        seen_titles = set()
        
        def normalize_title(title: str) -> str:
            """Normalize title for comparison"""
            # Remove special characters, convert to lowercase, remove extra spaces
            normalized = re.sub(r'[^\w\s]', '', title.lower())
            normalized = re.sub(r'\s+', ' ', normalized).strip()
            return normalized
        
        def title_similarity(title1: str, title2: str) -> float:
            """Calculate similarity between two titles"""
            words1 = set(normalize_title(title1).split())
            words2 = set(normalize_title(title2).split())
            
            if not words1 or not words2:
                return 0.0
            
            intersection = words1.intersection(words2)
            union = words1.union(words2)
            
            return len(intersection) / len(union) if union else 0.0
        
        for article in articles:
            url = article.get('url', '').strip()
            title = article.get('title', '').strip()
            
            if not title or not url:
                continue
            
            # Check URL duplicates
            if url in seen_urls:
                continue
            
            # Check title similarity
            is_duplicate = False
            normalized_title = normalize_title(title)
            
            for seen_title in seen_titles:
                if title_similarity(title, seen_title) > 0.8:  # 80% similarity threshold
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                seen_urls.add(url)
                seen_titles.add(title)
                unique_articles.append(article)
        
        logger.info(f"🔄 Removed {len(articles) - len(unique_articles)} duplicates")
        return unique_articles

    def filter_by_topic_intelligent(self, articles: List[dict], topic: str) -> List[dict]:
        """Intelligent topic filtering using multiple criteria"""
        if not topic or topic.lower() == 'general':
            return articles
        
        filtered_articles = []
        topic_lower = topic.lower()
        
        for article in articles:
            # Check classified topic
            if article.get('topic', '').lower() == topic_lower:
                filtered_articles.append(article)
                continue
            
            # Check feed category
            if article.get('feed_category', '').lower() == topic_lower:
                filtered_articles.append(article)
                continue
            
            # Check keywords in title and content
            title = article.get('title', '').lower()
            content = article.get('description', '').lower()
            
            if topic_lower in title or topic_lower in content:
                filtered_articles.append(article)
                continue
            
            # Check topic-specific keywords
            if topic_lower in self.topic_keywords:
                keywords = self.topic_keywords[topic_lower]
                text = f"{title} {content}"
                
                keyword_matches = sum(1 for keyword in keywords if keyword in text)
                if keyword_matches >= 2:  # At least 2 keyword matches
                    article['topic'] = topic_lower  # Update topic
                    filtered_articles.append(article)
        
        logger.info(f"🎯 Filtered {len(filtered_articles)} articles for topic '{topic}'")
        return filtered_articles

    def sort_articles_by_relevance(self, articles: List[dict], focus_indian: bool = True) -> List[dict]:
        """Sort articles by relevance score"""
        def calculate_relevance_score(article: dict) -> float:
            score = 0.0
            
            # Base score from feed reliability
            score += article.get('feed_reliability', 0.8) * 10
            
            # Indian content bonus if focus_indian is True
            if focus_indian and article.get('is_indian', False):
                score += 20
            
            # Recent articles get higher score
            try:
                pub_date = parser.parse(article.get('published_at', ''))
                hours_old = (datetime.now(pub_date.tzinfo) - pub_date).total_seconds() / 3600
                if hours_old < 6:  # Less than 6 hours old
                    score += 15
                elif hours_old < 24:  # Less than 24 hours old
                    score += 10
                elif hours_old < 72:  # Less than 3 days old
                    score += 5
            except:
                pass
            
            # Title length bonus (not too short, not too long)
            title_len = len(article.get('title', ''))
            if 30 <= title_len <= 100:
                score += 5
            
            # Content availability bonus
            if article.get('description', '').strip():
                score += 5
            
            return score
        
        # Sort by relevance score (descending)
        sorted_articles = sorted(articles, key=calculate_relevance_score, reverse=True)
        
        return sorted_articles

    @cache(prefix="enhanced_news", ttl=300)  # Cache for 5 minutes
    async def get_enhanced_news_feed(
        self, 
        db: Session, 
        topic: Optional[str] = None,
        source: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
        focus_indian: bool = True
    ) -> List[dict]:
        """Get enhanced news feed with intelligent filtering and optimization"""
        try:
            logger.info(f"🚀 Starting enhanced news feed fetch - Topic: {topic}, Focus Indian: {focus_indian}")
            
            all_articles = []
            
            # Fetch from RSS feeds (primary source)
            rss_articles = await self.fetch_all_rss_feeds(focus_indian=focus_indian, topic_filter=topic)
            all_articles.extend(rss_articles)
            
            # Fetch from database (secondary source)
            try:
                query = db.query(Article).join(NewsSource)
                if topic:
                    query = query.filter(Article.topic.ilike(f"%{topic}%"))
                if source:
                    query = query.filter(NewsSource.name.ilike(f"%{source}%"))
                
                db_articles = query.order_by(Article.published_at.desc()).limit(20).all()
                
                for article in db_articles:
                    all_articles.append({
                        "id": article.id,
                        "title": article.title,
                        "description": article.content,
                        "content": article.content,
                        "url": article.url,
                        "published_at": article.published_at.isoformat() if article.published_at else datetime.now().isoformat(),
                        "topic": article.topic or 'general',
                        "summary": article.summary,
                        "source_name": article.source.name if article.source else 'Unknown',
                        "source_bias_score": article.source.bias_score if article.source else None,
                        "is_indian": article.source.country == "in" if article.source else False,
                        "api_source": "database",
                        "feed_reliability": 0.9
                    })
                
                logger.info(f"📊 Database articles: {len(db_articles)}")
                
            except Exception as e:
                logger.error(f"❌ Database fetch failed: {str(e)}")
            
            # Remove duplicates
            unique_articles = self.remove_duplicates_advanced(all_articles)
            
            # Apply intelligent topic filtering
            if topic:
                unique_articles = self.filter_by_topic_intelligent(unique_articles, topic)
            
            # Sort by relevance
            sorted_articles = self.sort_articles_by_relevance(unique_articles, focus_indian)
            
            # Apply pagination
            paginated_articles = sorted_articles[offset:offset + limit]
            
            # Log performance statistics
            indian_count = sum(1 for article in paginated_articles if article.get('is_indian', False))
            international_count = len(paginated_articles) - indian_count
            
            logger.info(f"✅ Enhanced news feed complete:")
            logger.info(f"   📰 Total articles: {len(paginated_articles)}")
            logger.info(f"   🇮🇳 Indian articles: {indian_count}")
            logger.info(f"   🌍 International articles: {international_count}")
            logger.info(f"   🎯 Topic: {topic or 'All'}")
            logger.info(f"   ⚡ Failed feeds: {len(self.failed_feeds)}")
            
            return paginated_articles
            
        except Exception as e:
            logger.error(f"❌ Enhanced news feed failed: {str(e)}")
            logger.error(f"❌ Traceback: {traceback.format_exc()}")
            return []

    def get_performance_stats(self) -> Dict:
        """Get performance statistics for feeds"""
        stats = {
            'total_feeds': sum(len(feeds) for feeds in self.rss_feeds.values()),
            'failed_feeds': len(self.failed_feeds),
            'success_rate': 0.0,
            'average_fetch_time': 0.0,
            'feed_performance': {}
        }
        
        total_feeds = stats['total_feeds']
        if total_feeds > 0:
            stats['success_rate'] = ((total_feeds - stats['failed_feeds']) / total_feeds) * 100
        
        # Calculate average fetch times
        all_times = []
        for feed_name, times in self.feed_performance.items():
            if times:
                avg_time = sum(times) / len(times)
                stats['feed_performance'][feed_name] = {
                    'average_time': avg_time,
                    'total_requests': len(times),
                    'status': 'failed' if feed_name in self.failed_feeds else 'active'
                }
                all_times.extend(times)
        
        if all_times:
            stats['average_fetch_time'] = sum(all_times) / len(all_times)
        
        return stats

    def reset_failed_feeds(self):
        """Reset failed feeds list (for retry mechanism)"""
        self.failed_feeds.clear()
        logger.info("🔄 Failed feeds list reset")

# Global instance
enhanced_news_service = EnhancedNewsService()