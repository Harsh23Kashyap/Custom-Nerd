# Custom-Nerd/Nerd-Engine Case Studies: Quick Reference Guide

## DietNerd vs NewsNerd vs SpaceNerd Configuration Comparison

### 🏥 DietNerd (Medical Research Domain)

#### **Visual Identity**
- **Theme**: Medical Blue (#EFF8FF)
- **Icon**: 🥗 (Salad)
- **Tagline**: "Evidence-based nutrition questions backed by strongest scientific evidence"
- **Disclaimer**: Medical disclaimer with professional advice references

#### **Search Capabilities**
| Feature | Status | Purpose |
|---------|--------|---------|
| PDF Upload | ✅ Enabled | Research paper uploads |
| PMID Search | ✅ Enabled | Direct PubMed article access |
| Database Search | ✅ Enabled (Default) | Primary search method |
| References Section | ✅ Visible | Academic citations display |

#### **Backend Integration**
- **Primary API**: Bio.Entrez (PubMed)
- **Data Focus**: Peer-reviewed medical literature
- **Search Strategy**: Academic database optimization
- **Validation**: Recipe/animal question filtering

#### **Question Examples**
- "What are the health benefits of intermittent fasting?"
- "Is resveratrol effective in humans?"
- "Effects of omega-3 fatty acids on cardiovascular health?"

---

### 🌌 SpaceNerd (Space Research Domain)

#### **Visual Identity**
- **Theme**: Space Neutral (#f5f4f4)
- **Icon**: ⋆⁺₊⋆ ☾⋆⁺₊⋆ (Stars)
- **Tagline**: "We answer your space related questions based on Nasa"
- **Disclaimer**: Educational purposes disclaimer

#### **Search Capabilities**
| Feature | Status | Purpose |
|---------|--------|---------|
| PDF Upload | ❌ Disabled | Not relevant for space research |
| PMID Search | ❌ Disabled | Not applicable to space literature |
| Database Search | ✅ Enabled (Default) | Space literature search |
| Query Cleaning | ✅ Enabled | Advanced query preprocessing |
| References Section | ✅ Visible | Academic citations with DOI/arXiv IDs |

#### **Backend Integration**
- **Primary APIs**: arXiv API, NASA ADS
- **Data Focus**: Preprints and peer-reviewed space literature
- **Search Strategy**: Astronomy category optimization
- **Validation**: Space science topic relevance
- **Query Cleaning**: Advanced preprocessing for complex terminology

#### **Question Examples**
- "What are the latest findings on exoplanet atmospheric composition?"
- "How do black hole mergers affect gravitational wave detection?"
- "What is the current understanding of dark matter distribution in galaxies?"

---

### 📰 NewsNerd (Current Events Domain)

#### **Visual Identity**
- **Theme**: Neutral Gray (#e9e2e2)
- **Icon**: 🥗 (Same as DietNerd - could be customized)
- **Tagline**: "We answer your news related questions"
- **Disclaimer**: Simple educational disclaimer with news consumption advice

#### **Search Capabilities**
| Feature | Status | Purpose |
|---------|--------|---------|
| PDF Upload | ❌ Disabled | Not relevant for news |
| PMID Search | ❌ Disabled | Not applicable to news |
| Database Search | ✅ Enabled (Default) | News article search |
| References Section | ❌ Hidden | Simplified interface |

#### **Backend Integration**
- **Primary APIs**: GNews API, NewsAPI, The Guardian Open Platform
- **Data Focus**: Current news articles and reports
- **Search Strategy**: News relevance optimization
- **Validation**: News topic relevance filtering

#### **Question Examples**
- "Geopolitical implications of latest G7 summit decisions?"
- "How has media coverage of climate change evolved?"
- "How does misinformation spread through social media?"

---

## Configuration Pattern Templates

### 🔬 Academic Research Pattern (DietNerd Model)
```javascript
{
  "domain": "academic_research",
  "theme": "professional_medical",
  "search_strategies": {
    "upload-articles": true,
    "pmid-search": true, 
    "database-search": true
  },
  "query_cleaning": false,
  "references": "full_academic",
  "validation": "domain_specific_filtering",
  "data_sources": ["pubmed", "academic_databases"],
  "disclaimer": "professional_advice_required"
}
```

**Best for**: Medical, Scientific, Legal, Technical domains

### 📊 Current Events Pattern (NewsNerd Model)
```javascript
{
  "domain": "current_events",
  "theme": "neutral_professional",
  "search_strategies": {
    "upload-articles": false,
    "pmid-search": false,
    "database-search": true
  },
  "query_cleaning": false,
  "references": "simplified_or_hidden",
  "validation": "topic_relevance",
  "data_sources": ["gnews", "newsapi", "guardian"],
  "disclaimer": "educational_awareness"
}
```

**Best for**: News, Politics, Market Analysis, Social Trends

### 🌌 Space Research Pattern (SpaceNerd Model)
```javascript
{
  "domain": "space_research",
  "theme": "space_neutral",
  "search_strategies": {
    "upload-articles": false,
    "pmid-search": false,
    "database-search": true
  },
  "query_cleaning": true,
  "references": "full_academic_with_identifiers",
  "validation": "domain_specific_filtering",
  "data_sources": ["arxiv", "nasa_ads"],
  "disclaimer": "educational_purposes"
}
```

**Best for**: Astronomy, Space Science, Astrophysics, Planetary Science

---

## Key Differentiation Points

### Data Source Strategy
| Aspect | DietNerd | NewsNerd | SpaceNerd |
|--------|----------|----------|-----------|
| **Primary Source** | PubMed Medical Database | GNews/NewsAPI/Guardian | arXiv/ADS (configurable) |
| **Content Type** | Peer-reviewed studies | News articles & reports | Preprints + peer-reviewed |
| **Time Sensitivity** | Research validity | Current relevance | Recency + publication status |
| **Quality Metric** | Scientific rigor | Factual accuracy | Scientific rigor |
| **Query Cleaning** | Not enabled | Not enabled | Advanced preprocessing |

### User Interface Philosophy
| Aspect | DietNerd | NewsNerd | SpaceNerd |
|--------|----------|----------|-----------|
| **Complexity** | Full feature set | Simplified interface | Full feature set |
| **Target User** | Health professionals | General public | Researchers/enthusiasts |
| **Evidence Display** | Comprehensive references | Streamlined presentation | References with DOI/arXiv IDs |
| **Input Methods** | Multiple search strategies | Single search focus | Multiple search strategies |
| **Query Processing** | Standard | Standard | Advanced cleaning |

### Processing Approach
| Aspect | DietNerd | NewsNerd | SpaceNerd |
|--------|----------|----------|-----------|
| **Query Optimization** | Medical terminology | News keywords | Astronomy categories + keywords |
| **Content Processing** | Abstract + full-text | Article summaries | Abstract/full-text when available |
| **Citation Style** | Academic format | Simplified references | DOI/arXiv linked academic format |
| **Validation Focus** | Medical appropriateness | News relevance | Astronomy topic relevance |
| **Query Preprocessing** | None | None | Advanced cleaning & normalization |

---

## Implementation Checklist

### For Academic Domains (DietNerd Pattern)
- [ ] Enable PDF upload functionality
- [ ] Configure PMID/ID search capability
- [ ] Set up academic database APIs
- [ ] Implement comprehensive reference system
- [ ] Add professional disclaimers
- [ ] Optimize for peer-reviewed content
- [ ] Include study quality assessments

### For Current Events Domains (NewsNerd Pattern)
- [ ] Disable academic-specific features
- [ ] Configure news/current events APIs
- [ ] Simplify user interface
- [ ] Focus on content recency
- [ ] Streamline reference display
- [ ] Optimize for general audience
- [ ] Include appropriate disclaimers

### For Space Research Domains (SpaceNerd Pattern)
- [ ] Configure arXiv and NASA ADS APIs
- [ ] Enable query cleaning functionality
- [ ] Implement advanced query preprocessing
- [ ] Set up astronomy category filters
- [ ] Configure DOI/arXiv reference system
- [ ] Optimize for complex terminology
- [ ] Include space science disclaimers

### For Hybrid Domains
- [ ] Assess which features are relevant
- [ ] Configure multiple data sources
- [ ] Implement adaptive reference system
- [ ] Create domain-specific validation
- [ ] Balance complexity vs usability
- [ ] Test with representative users
- [ ] Document configuration decisions

---

## Rapid Deployment Guide

### 1. Choose Base Pattern
- **Academic Research**: Use DietNerd as template
- **Current Events**: Use NewsNerd as template
- **Space Research**: Use SpaceNerd as template (arXiv/ADS with query cleaning)
- **Custom Hybrid**: Mix and match features

### 2. Customize Configuration
- Update `user_env.js` for visual identity
- Modify `user_search_apis.py` for data sources
- Adapt `openai_prompts.py` for domain validation
- Configure `clean_query.py` for advanced preprocessing (if needed)
- Configure `variables.env` with API keys

### 3. Test Implementation
- Validate search functionality
- Test domain-specific queries
- Verify API integrations
- Check user experience flow

### 4. Deploy and Monitor
- Save configuration state
- Monitor performance metrics
- Gather user feedback
- Iterate based on results

---

## Success Metrics by Domain Type

### Academic Research Domains
- **Quality**: Citation accuracy, peer-review percentage
- **Relevance**: Domain-specific content match
- **Usability**: Professional user adoption
- **Reliability**: Consistent academic standards

### Current Events Domains
- **Timeliness**: Content freshness and relevance
- **Coverage**: Source diversity and breadth
- **Accessibility**: General audience comprehension
- **Accuracy**: Fact-checking and verification

### Space Research Domains
- **Terminology**: Complex astronomy term handling
- **Preprocessing**: Advanced query cleaning and normalization
- **Content Mix**: Preprints and peer-reviewed balance
- **References**: DOI/arXiv identifier accuracy

This quick reference guide provides immediate guidance for implementing new domain-specific configurations using the proven DietNerd, NewsNerd, and SpaceNerd patterns as foundations. 