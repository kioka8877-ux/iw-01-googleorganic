"""
IW-01 GoogleOrganic — Google Organic Search Results
Iron Warrior #1 — Le plus simple, le moins cher, JSON propre.
Attaque : SerpWow ($120/10K reqs)
"""
from fastapi import FastAPI, Query, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from bs4 import BeautifulSoup
from urllib.parse import quote_plus
import sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'shared'))
from base import (
    create_app, fetch_html, SearchResult, SERPResponse,
    clean_text, get_timestamp, measure_latency
)
import time

app = create_app("IW-01 GoogleOrganic", "Google organic search results — top 10, JSON propre")

@app.get("/search", response_model=SERPResponse)
async def google_organic(
    q: str = Query(..., description="Search query"),
    num: int = Query(10, ge=1, le=100, description="Number of results"),
    gl: str = Query("us", description="Country (us, fr, uk, de, jp...)"),
    hl: str = Query("en", description="Language (en, fr, es, de...)"),
):
    start = time.time()
    url = f"https://www.google.com/search?q={quote_plus(q)}&num={num}&gl={gl}&hl={hl}"
    try:
        html = await fetch_html(url)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Google fetch failed: {e}")

    soup = BeautifulSoup(html, 'html.parser')
    results = []
    seen_urls = set()

    # Parse organic results
    for div in soup.find_all('div', class_='g'):
        h3 = div.find('h3')
        link = div.find('a', href=True)
        snippet_tag = div.find('div', class_='VwiC3b') or div.find('span', class_='aCOpRe')
        if h3 and link:
            href = link['href']
            if href.startswith('/url?q='):
                href = href.split('/url?q=')[1].split('&')[0]
            if href in seen_urls or not href.startswith('http'):
                continue
            seen_urls.add(href)
            results.append(SearchResult(
                title=clean_text(h3.get_text()),
                url=href,
                snippet=clean_text(snippet_tag.get_text()) if snippet_tag else "",
                position=len(results) + 1,
            ))
            if len(results) >= num:
                break

    # Fallback: parse via data-ved attributes
    if not results:
        for a in soup.find_all('a', href=True):
            href = a['href']
            h3 = a.find('h3')
            if h3 and href.startswith('http') and 'google.com' not in href:
                if href in seen_urls:
                    continue
                seen_urls.add(href)
                results.append(SearchResult(
                    title=clean_text(h3.get_text()),
                    url=href,
                    snippet="",
                    position=len(results) + 1,
                ))
                if len(results) >= num:
                    break

    # Related searches
    related = []
    for rs in soup.find_all('a', class_='fl'):
        related.append(clean_text(rs.get_text()))
    if not related:
        for rs in soup.find_all('p', class_='BBwThe'):
            related.append(clean_text(rs.get_text()))

    # People Also Ask
    paa = []
    for pa in soup.find_all('div', class_='related-question-pair'):
        q_text = pa.find('span', class_='CSY3tc')
        if q_text:
            paa.append(clean_text(q_text.get_text()))

    # Total results
    total = None
    total_tag = soup.find('div', id='result-stats')
    if total_tag:
        total = clean_text(total_tag.get_text())

    return SERPResponse(
        query=q, engine="google", total_results=total,
        results=results, related_searches=related[:10],
        people_also_ask=paa[:5],
        timestamp=get_timestamp(), latency_ms=measure_latency(start),
    )
