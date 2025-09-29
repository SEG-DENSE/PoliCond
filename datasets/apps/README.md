# Privacy Policy Corpus 2024Q4

## Overview
This directory contains 175 applications' privacy policy documents collected between November 30, 2024 and December 2, 2024.  The 175 applications include AppFigures' Top 10 Apps and each 5 apps from 33 category rankings, thus 175=10+33 * 5. We also publish our index file and crawler scripts.

The data was crawled using PoliGraph's open-source crawler script ([UCI-Networking-Group/PoliGraph: PoliGraph: Automated Privacy Policy Analysis using Knowledge Graphs](https://github.com/UCI-Networking-Group/PoliGraph)), which was based Playwright and Mozilla's readability lib. Many thanks! 

## App Coverage
- **Collection Period**: Nov 30, 2024 - Dec 2, 2024
- **Data Sources**: 
  - AppFigures Top 10 Applications
  - 33 App Store Categories, including Weather, Dating, Tools, Maps...
- **Total Documents**: 175 privacy policies
- **File Types**:
  - Original crawled HTML (`crawled.html`)
  - Cleaned text HTML (`cleaned.html`)

## File Structure
```bash
datasets/
└── apps/
    ├── websites.csv         # Metadata(categories, urls)
    ├── crawler/             # Crawling toolkit
    │   ├── crawler.sh       # Script to launch python crawler
    │   ├── crawler.py       # Playwright-based crawler
    │   ├── Readability.js   # Mozilla readability script
    │   ├── Readability-readerable.js # Mozilla readability script
    │   └── ...
    └── htmls/               # Collected documents
        ├── 100_Purple Ocean Psychic Readings/
        	├── cleaned.html # Pure text
          └── crawled.html # Original crawled HTML
        ├── 101_Trucker Path_ Truck GPS & Fuel/
        ├── ... 
```

**Metadata Example (websites.csv)**:

```csv
No,Name,Category,URL
1,Threads,TopApps,https://privacycenter.instagram.com/policy
2,TikTok,TopApps,https://www.tiktok.com/legal/page/us/privacy-policy/en
...
175,Today Weather:Data by NOAA/NWS,Weather,https://www.weather.gov/privacy/
```