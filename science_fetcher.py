"""
Science News Fetcher - Science, Space, Biology, Physics, Research
"""

import feedparser
from datetime import datetime

class ScienceFetcher:
    
    def fetch_science_daily(self, limit=10):
        """Fetch from Science Daily"""
        try:
            feed = feedparser.parse("https://www.sciencedaily.com/rss/all.xml")
            articles = []
            for entry in feed.entries[:limit]:
                articles.append({
                    'title': entry.title,
                    'description': entry.description[:500] if hasattr(entry, 'description') else entry.title,
                    'source': 'Science Daily',
                    'url': entry.link,
                    'published': entry.get('published', datetime.now().isoformat()),
                    'source_type': 'science',
                    'category': 'science'
                })
            print(f"  Science Daily: {len(articles)} articles")
            return articles
        except Exception as e:
            print(f"  Science Daily error: {e}")
            return []
    
    def fetch_nature_news(self, limit=10):
        """Fetch from Nature"""
        try:
            feed = feedparser.parse("https://www.nature.com/nature.rss")
            articles = []
            for entry in feed.entries[:limit]:
                articles.append({
                    'title': entry.title,
                    'description': entry.description[:500] if hasattr(entry, 'description') else entry.title,
                    'source': 'Nature',
                    'url': entry.link,
                    'published': entry.get('published', datetime.now().isoformat()),
                    'source_type': 'science',
                    'category': 'science'
                })
            print(f"  Nature: {len(articles)} articles")
            return articles
        except Exception as e:
            print(f"  Nature error: {e}")
            return []
    
    def fetch_new_scientist(self, limit=10):
        """Fetch from New Scientist"""
        try:
            feed = feedparser.parse("https://www.newscientist.com/feed/home")
            articles = []
            for entry in feed.entries[:limit]:
                articles.append({
                    'title': entry.title,
                    'description': entry.description[:500] if hasattr(entry, 'description') else entry.title,
                    'source': 'New Scientist',
                    'url': entry.link,
                    'published': entry.get('published', datetime.now().isoformat()),
                    'source_type': 'science',
                    'category': 'science'
                })
            print(f"  New Scientist: {len(articles)} articles")
            return articles
        except Exception as e:
            print(f"  New Scientist error: {e}")
            return []
    
    def fetch_space_news(self, limit=10):
        """Fetch from Space.com"""
        try:
            feed = feedparser.parse("https://www.space.com/feeds/all")
            articles = []
            for entry in feed.entries[:limit]:
                articles.append({
                    'title': entry.title,
                    'description': entry.description[:500] if hasattr(entry, 'description') else entry.title,
                    'source': 'Space.com',
                    'url': entry.link,
                    'published': entry.get('published', datetime.now().isoformat()),
                    'source_type': 'science',
                    'category': 'science'
                })
            print(f"  Space.com: {len(articles)} articles")
            return articles
        except Exception as e:
            print(f"  Space.com error: {e}")
            return []
    
    def fetch_live_science(self, limit=10):
        """Fetch from Live Science"""
        try:
            feed = feedparser.parse("https://www.livescience.com/feeds/all")
            articles = []
            for entry in feed.entries[:limit]:
                articles.append({
                    'title': entry.title,
                    'description': entry.description[:500] if hasattr(entry, 'description') else entry.title,
                    'source': 'Live Science',
                    'url': entry.link,
                    'published': entry.get('published', datetime.now().isoformat()),
                    'source_type': 'science',
                    'category': 'science'
                })
            print(f"  Live Science: {len(articles)} articles")
            return articles
        except Exception as e:
            print(f"  Live Science error: {e}")
            return []
    
    def fetch_arxiv_ai(self, limit=10):
        """Fetch AI papers from arXiv"""
        try:
            feed = feedparser.parse("http://export.arxiv.org/rss/cs.AI")
            articles = []
            for entry in feed.entries[:limit]:
                articles.append({
                    'title': entry.title,
                    'description': entry.description[:500] if hasattr(entry, 'description') else entry.title,
                    'source': 'arXiv AI Research',
                    'url': entry.link,
                    'published': entry.get('published', datetime.now().isoformat()),
                    'source_type': 'research',
                    'category': 'ai'
                })
            print(f"  arXiv AI: {len(articles)} papers")
            return articles
        except Exception as e:
            print(f"  arXiv error: {e}")
            return []
    
    def fetch_mit_ai(self, limit=10):
        """Fetch MIT AI News"""
        try:
            feed = feedparser.parse("https://news.mit.edu/topic/artificial-intelligence2/feed")
            articles = []
            for entry in feed.entries[:limit]:
                articles.append({
                    'title': entry.title,
                    'description': entry.description[:500] if hasattr(entry, 'description') else entry.title,
                    'source': 'MIT AI News',
                    'url': entry.link,
                    'published': entry.get('published', datetime.now().isoformat()),
                    'source_type': 'ai_research',
                    'category': 'ai'
                })
            print(f"  MIT AI News: {len(articles)} articles")
            return articles
        except Exception as e:
            print(f"  MIT error: {e}")
            return []
    
    def fetch_all_science(self, limit_per_source=8):
        """Fetch from all science sources"""
        all_articles = []
        print("\n🔬 Fetching Science & AI Research News...")
        
        science_daily = self.fetch_science_daily(limit_per_source)
        all_articles.extend(science_daily)
        
        nature = self.fetch_nature_news(limit_per_source)
        all_articles.extend(nature)
        
        new_scientist = self.fetch_new_scientist(limit_per_source)
        all_articles.extend(new_scientist)
        
        space = self.fetch_space_news(limit_per_source)
        all_articles.extend(space)
        
        live_science = self.fetch_live_science(limit_per_source)
        all_articles.extend(live_science)
        
        arxiv = self.fetch_arxiv_ai(limit_per_source)
        all_articles.extend(arxiv)
        
        mit_ai = self.fetch_mit_ai(limit_per_source)
        all_articles.extend(mit_ai)
        
        print(f"\n📊 TOTAL Science/AI articles: {len(all_articles)}")
        return all_articles

