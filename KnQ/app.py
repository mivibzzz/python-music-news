from flask import Flask, render_template, jsonify, request
import feedparser
import threading
import time
from datetime import datetime

app = Flask(__name__)

RSS_FEEDS = {
    "Rap / Hip Hop": [
        "https://www.hotnewhiphop.com/rss/news.xml",
        "https://www.xxlmag.com/feed/",
        "https://www.thefader.com/rss/news"
    ],
    "R&B": [
        "https://ratedrnb.com/feed/",
        "https://www.soulbounce.com/feed/"
    ],
    "Afrobeats": [
        "https://www.okayafrica.com/rss/",
        "https://notjustok.com/feed/"
    ],
    "Reggae / Dancehall": [
        "https://www.dancehallmag.com/feed",
        "https://unitedreggae.com/rss/"
    ]
}

# Cache for feed data
feed_cache = {}
cache_timestamp = {}

def fetch_feed_data(url):
    """Fetch and parse RSS feed data"""
    try:
        feed = feedparser.parse(url)
        articles = []
        for entry in feed.entries[:10]:
            articles.append({
                'title': entry.get('title', 'No Title'),
                'link': entry.get('link', '#'),
                'summary': entry.get('summary', 'No summary available'),
                'published': entry.get('published', ''),
                'source': feed.feed.get('title', 'Unknown Source')
            })
        return articles
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return []

def update_cache():
    """Update the feed cache"""
    for genre, urls in RSS_FEEDS.items():
        feed_cache[genre] = []
        for url in urls:
            articles = fetch_feed_data(url)
            feed_cache[genre].extend(articles)
        cache_timestamp[genre] = datetime.now()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/feeds')
def get_feeds():
    genre = request.args.get('genre', 'all')
    query = request.args.get('query', '').lower()
    
    # Update cache if empty or old
    if not feed_cache:
        update_cache()
    
    if genre == 'all':
        all_articles = []
        for articles in feed_cache.values():
            all_articles.extend(articles)
    else:
        all_articles = feed_cache.get(genre, [])
    
    # Filter by search query
    if query:
        filtered_articles = []
        for article in all_articles:
            if (query in article['title'].lower() or 
                query in article['summary'].lower()):
                filtered_articles.append(article)
        all_articles = filtered_articles
    
    # Sort by published date (newest first)
    all_articles.sort(key=lambda x: x.get('published', ''), reverse=True)
    
    return jsonify({
        'articles': all_articles[:50],  # Limit to 50 articles
        'total': len(all_articles)
    })

@app.route('/api/refresh')
def refresh_feeds():
    update_cache()
    return jsonify({'status': 'success', 'message': 'Feeds refreshed'})

if __name__ == '__main__':
    # Initialize cache
    print("Loading initial feed data...")
    update_cache()
    print("Starting server on http://localhost:8000")
    app.run(host='0.0.0.0', port=8000, debug=True)