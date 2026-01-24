# Custom-Nerd/Nerd-Engine: Installation Case Studies
## Step-by-Step Setup for Different Use Cases

## Table of Contents
1. [Installation Overview](#installation-overview)
2. [Case Study 1: DietNerd Installation](#case-study-1-dietnerd-installation)
3. [Case Study 2: NewsNerd Installation](#case-study-2-newsnerd-installation)
4. [Case Study 3: Fresh Custom Domain Installation](#case-study-3-fresh-custom-domain-installation)
5. [Common Installation Issues](#common-installation-issues)
6. [Post-Installation Validation](#post-installation-validation)
7. [Maintenance and Updates](#maintenance-and-updates)

---

## Installation Overview

Custom-Nerd/Nerd-Engine supports multiple installation scenarios:
- **Fresh Installation**: Starting from scratch with base system
- **Domain-Specific Setup**: Configuring for specific use cases (Diet, News, etc.)
- **Configuration Switching**: Moving between different domain configurations
- **Custom Domain Creation**: Building new domain-specific implementations

### System Requirements
- **OS**: macOS, Linux, or Windows with WSL
- **Python**: 3.8 or higher
- **Memory**: 4GB RAM minimum, 8GB recommended
- **Storage**: 2GB free space
- **Network**: Stable internet connection for API access

---

## Case Study 1: DietNerd Installation

### Scenario
Setting up Custom-Nerd/Nerd-Engine for **medical and nutrition research** with academic database integration.

### Target Users
- Healthcare professionals
- Nutrition researchers
- Medical students
- Health-conscious consumers seeking evidence-based information

### Step-by-Step Installation

#### **Phase 1: Initial System Setup**

1. **Download and Extract Project**
   ```bash
   # Navigate to your projects directory
   cd ~/Projects
   
   # Extract Custom-Nerd/Nerd-Engine (assuming downloaded from GitHub/Drive)
   unzip customnerd-main.zip
   cd customnerd-main
   ```

2. **Grant Script Permissions**
   (Skipped: Python scripts do not require executable permissions when run with the python interpreter.)

3. **Run Initial Setup**
   ```bash
   python3 setup.py
   ```
   
   **Expected Output:**
   ```
   🚀 Setting up Custom-Nerd/Nerd-Engine...
   📦 Creating virtual environment...
   📥 Installing dependencies...
   ✅ Setup completed successfully!
   ```

   **Installation Time**: 20-30 minutes (depending on internet speed)

#### **Phase 2: API Keys Configuration**

1. **Obtain Required API Keys**
   - **NCBI API Key**: Register at https://ncbiinsights.ncbi.nlm.nih.gov/2017/11/02/new-api-keys-for-the-e-utilities/
   - **OpenAI API Key**: Get from https://openai.com/api/
   - **Elsevier API Key**: Apply at https://dev.elsevier.com/
   - **Springer API Key**: Register at https://dev.springernature.com/
   - **Wiley API Key**: Apply at https://onlinelibrary.wiley.com/library-info/resources/text-and-datamining

2. **Start Backend Server**
   ```bash
   cd customnerd-backend
   python run.py
   ```
   
   **Wait for confirmation:**
   ```
   INFO:     Application startup complete
   ```

3. **Open Frontend and Configure**
   ```bash
   # In new terminal window
   cd customnerd-website
   open index.html  # macOS
   # or
   xdg-open index.html  # Linux
   ```

4. **Configure API Keys via Web Interface**
   - Click **Configuration** → **Environment Configuration**
   - Enter API keys:
     ```
     NCBI_API_KEY: [your_ncbi_key]
     OPENAI_API_KEY: [your_openai_key]
     ELSEVIER_API_KEY: [your_elsevier_key]
     SPRINGER_API_KEY: [your_springer_key]
     WILEY_API_KEY: [your_wiley_key]
     ENTREZ_EMAIL: [your_email]
     ```
   - Click **Save**

#### **Phase 3: DietNerd Configuration**

1. **Load DietNerd Configuration**
   - Go to **Configuration** → **Load and Save State**
   - Select **DietNerd** from dropdown
   - Click **Load State**
   
   **System Response:**
   ```
   ✅ DietNerd configuration loaded successfully
   ```

2. **Verify DietNerd Settings**
   - **Frontend Configuration**:
     - Site Name: "Diet Nerd"
     - Theme: Medical blue (#EFF8FF)
     - Icon: 🥗
     - Tagline: Evidence-based nutrition guidance

   - **Search Strategies**:
     - ✅ PDF Upload: Enabled
     - ✅ PMID Search: Enabled  
     - ✅ PubMed Search: Enabled (Default)
     - ✅ References: Visible

#### **Phase 4: Installation Validation**

1. **Test Basic Functionality**
   ```
   Test Query: "What are the health benefits of omega-3 fatty acids?"
   ```
   
   **Expected Workflow:**
   - Question validation passes
   - Search strategy selection appears
   - PubMed search executes
   - Articles are collected and processed
   - Evidence-based response generated
   - Academic references displayed

2. **Verify Medical Features**
   - **PDF Upload**: Test with nutrition research paper
   - **PMID Search**: Test with valid PMID (e.g., "12345678")
   - **Medical Validation**: Test recipe questions (should be rejected)

3. **Check Academic Integration**
   - Verify PubMed connectivity
   - Check citation formatting
   - Validate reference links
   - Test full-text retrieval (when available)

#### **Phase 5: DietNerd Customization (Optional)**

1. **Customize Medical Disclaimer**
   - Go to **Configuration** → **Frontend Configuration**
   - Modify disclaimer text for your jurisdiction/organization
   - Update contact information

2. **Adjust Search Parameters**
   - **Backend Configuration** → modify search limits
   - **Prompt Engineering** → customize medical validation
   - **User Flow** → adjust search strategy preferences

### DietNerd Installation Checklist

- [ ] Base system setup completed (30 minutes)
- [ ] All medical APIs configured and tested
- [ ] DietNerd configuration loaded successfully
- [ ] Medical theme and branding applied
- [ ] PDF upload functionality working
- [ ] PMID search capability enabled
- [ ] PubMed integration validated
- [ ] Academic references displaying correctly
- [ ] Medical disclaimer updated
- [ ] Recipe question filtering working
- [ ] Full test query completed successfully

### Expected DietNerd Features Post-Installation

✅ **Medical Research Focus**: PubMed academic integration  
✅ **Professional Interface**: Medical blue theme, comprehensive features  
✅ **Academic Tools**: PDF upload, PMID search, full references  
✅ **Quality Control**: Recipe filtering, medical validation  
✅ **Evidence Standards**: Peer-reviewed source prioritization  

---

## Case Study 2: NewsNerd Installation

### Scenario
Setting up Custom-Nerd/Nerd-Engine for **current events and news analysis** with real-time information sources.

### Target Users
- Journalists and reporters
- Policy researchers
- News analysts
- General public seeking factual news analysis

### Step-by-Step Installation

#### **Phase 1: Base Installation**

1. **Complete Initial Setup** (Same as DietNerd Phase 1)
   ```bash
   cd customnerd-main
   python3 setup.py
   ```

#### **Phase 2: News-Specific API Configuration**

1. **Obtain NewsAPI Key**
   - Register at https://newsapi.org/
   - Choose appropriate plan (Developer/Business)
   - Note API limitations and rate limits

2. **Configure News APIs**
   - Start backend: `python run.py`
   - Open frontend configuration
   - **Environment Configuration**:
     ```
     NEWS_API_KEY: [your_newsapi_key]
     OPENAI_API_KEY: [your_openai_key]
     # Note: Academic APIs not required for NewsNerd
     ```

#### **Phase 3: NewsNerd Configuration**

1. **Load NewsNerd State**
   - **Configuration** → **Load and Save State**
   - Select **NewsNerd**
   - Click **Load State**

2. **Verify NewsNerd Settings**
   - **Frontend Configuration**:
     - Site Name: "News Nerds"
     - Theme: Neutral gray (#e9e2e2)
     - Tagline: "We answer your news related questions"

   - **Search Strategies**:
     - ❌ PDF Upload: Disabled
     - ❌ PMID Search: Disabled
     - ✅ News Search: Enabled (Only option)
     - ❌ References: Hidden (Simplified interface)

#### **Phase 4: News Integration Validation**

1. **Test News Functionality**
   ```
   Test Query: "What are the latest developments in renewable energy policy?"
   ```
   
   **Expected Workflow:**
   - News relevance validation
   - Simplified search interface
   - NewsAPI integration
   - Current articles collection
   - Factual analysis response
   - Streamlined presentation

2. **Verify News-Specific Features**
   - **Real-time Content**: Recent articles prioritized
   - **Multiple Sources**: Various news outlets
   - **Simplified Interface**: No academic complexity
   - **Current Events Focus**: Timeliness over peer review

#### **Phase 5: NewsNerd Optimization**

1. **Configure News Sources**
   - Review NewsAPI source preferences
   - Adjust query parameters for relevance
   - Set geographic/language preferences

2. **Customize News Validation**
   - **Backend Configuration** → News relevance prompts
   - Adjust for opinion vs factual content
   - Configure source credibility weighting

### NewsNerd Installation Checklist

- [ ] Base system setup completed
- [ ] NewsAPI key configured and validated
- [ ] NewsNerd configuration loaded
- [ ] News theme applied (gray/neutral)
- [ ] Academic features disabled (PDF, PMID)
- [ ] Simplified interface confirmed
- [ ] News search functionality working
- [ ] Real-time article collection tested
- [ ] Multiple news sources verified
- [ ] Current events query completed successfully

### Expected NewsNerd Features Post-Installation

✅ **Current Events Focus**: Real-time news integration  
✅ **Simplified Interface**: Streamlined for general audience  
✅ **Multi-Source**: Diverse news outlet aggregation  
✅ **Relevance Filtering**: News-appropriate content validation  
✅ **Accessibility**: General public usability optimization  

---

## Case Study 3: Fresh Custom Domain Installation

### Scenario
Creating a **new domain-specific implementation** from scratch (example: LegalNerd for legal research).

### Step-by-Step Process

#### **Phase 1: Domain Planning**

1. **Define Requirements**
   ```
   Domain: Legal Research
   Target Users: Lawyers, Legal Researchers, Law Students
   Data Sources: Legal databases, case law, statutes
   Key Features: Case citations, legal document upload, jurisdiction filtering
   ```

2. **API Research**
   - Identify legal database APIs (Westlaw, LexisNexis, etc.)
   - Research access requirements and costs
   - Plan data integration approach

#### **Phase 2: Base Installation**

1. **Standard Setup**
   ```bash
   python3 setup.py
   python3 run.py
   ```

2. **Access Configuration Interface**
   - Open frontend in browser
   - Navigate to Configuration panel

#### **Phase 3: Custom Configuration Creation**

1. **Frontend Configuration**
   - **Configuration** → **Frontend Configuration**
   ```javascript
   Site Name: "Legal Nerd"
   Site Icon: "⚖️"
   Tagline: "Evidence-based legal research and analysis"
   Background Color: "#f8f9fa" (Professional theme)
   Font Family: "'Times New Roman', serif"
   Disclaimer: "Legal research for educational purposes only..."
   ```

2. **User Flow Configuration**
   - **Configuration** → **User Flow Configuration**
   ```javascript
   Search Strategies:
   - Upload Legal Documents: Enabled
   - Case Citation Search: Enabled  
   - Legal Database Search: Enabled (Default)
   Reference Section: Visible (Legal citations)
   ```

3. **Backend Integration**
   - **Configuration** → **User Flow Configuration** → **AI Code Generator**
   - Input legal API documentation
   - Generate custom `collect_articles()` function
   - Test and refine integration

4. **Prompt Engineering**
   - **Configuration** → **Backend Configuration**
   - Customize prompts for legal domain:
     ```
     Question Validation: Legal research appropriateness
     Query Generation: Legal database optimization
     Content Processing: Legal terminology handling
     Response Synthesis: Legal disclaimer compliance
     ```

#### **Phase 4: Testing and Refinement**

1. **Functional Testing**
   ```
   Test Queries:
   - "What is the precedent for contract interpretation in technology licensing?"
   - "How do courts handle intellectual property disputes in AI?"
   ```

2. **Integration Validation**
   - Legal database connectivity
   - Case citation formatting
   - Legal document processing
   - Jurisdiction-specific filtering

#### **Phase 5: State Management**

1. **Save Custom Configuration**
   - **Configuration** → **Load and Save State**
   - Enter name: "LegalNerd"
   - Click **Save State**

2. **Backup Configuration**
   - Export configuration files
   - Document customizations
   - Create deployment guide

### Custom Domain Installation Checklist

- [ ] Domain requirements defined and documented
- [ ] Required APIs identified and accessed
- [ ] Base Custom-Nerd/Nerd-Engine installation completed
- [ ] Frontend branding customized
- [ ] Search strategies configured appropriately
- [ ] Backend API integration implemented
- [ ] Domain-specific prompts engineered
- [ ] Functional testing completed successfully
- [ ] Configuration saved as custom state
- [ ] Documentation and backup completed

---

## Common Installation Issues

### Issue 1: Python Dependencies
**Problem**: Package installation failures during setup
```bash
ERROR: Failed building wheel for [package]
```

**Solutions**:
```bash
# Update pip and setuptools
pip install --upgrade pip setuptools

# Install with verbose output to diagnose
pip install -v [package]

# Use conda if pip fails
conda install [package]

# Skip problematic packages temporarily
pip install --ignore-installed [package]
```

### Issue 2: API Key Validation
**Problem**: API keys not working or rate limit errors

**Solutions**:
1. **Verify API Key Format**: Check for extra spaces, incomplete keys
2. **Test API Access**: Use curl or API testing tools
3. **Check Rate Limits**: Review API plan limitations
4. **Validate Permissions**: Ensure API key has required scopes

### Issue 3: Port Conflicts
**Problem**: Backend server fails to start
```bash
ERROR: Address already in use
```

**Solutions**:
```bash
# Find process using port 8000
lsof -i :8000

# Kill conflicting process
kill -9 [PID]

# Or use different port
uvicorn main:app --port 8001
```

### Issue 4: Configuration Loading Failures
**Problem**: Saved states not loading properly

**Solutions**:
1. **Check File Permissions**: Ensure read/write access
2. **Validate JSON Format**: Check for syntax errors
3. **Clear Browser Cache**: Force refresh configuration
4. **Restart Backend**: Reload configuration system

### Issue 5: Academic Database Access
**Problem**: PubMed/academic APIs not responding

**Solutions**:
1. **Verify Email Configuration**: Required for NCBI access
2. **Check Network Connectivity**: Firewall or proxy issues
3. **Validate API Quotas**: Daily/monthly limits exceeded
4. **Test Alternative Endpoints**: Backup API access methods

---

## Post-Installation Validation

### Comprehensive Testing Checklist

#### **Basic Functionality**
- [ ] Backend server starts without errors
- [ ] Frontend loads and displays correctly
- [ ] Configuration interface accessible
- [ ] API keys validate successfully

#### **Domain-Specific Features**
- [ ] Search strategies work as configured
- [ ] Data sources return appropriate content
- [ ] Validation logic filters correctly
- [ ] Response quality meets domain standards

#### **Performance Validation**
- [ ] Response times under 30 seconds for typical queries
- [ ] Concurrent user handling (if applicable)
- [ ] Memory usage within expected limits
- [ ] Error handling graceful and informative

#### **Security Validation**
- [ ] API keys stored securely
- [ ] No sensitive data in browser cache
- [ ] HTTPS configured (production)
- [ ] Input sanitization working

### Monitoring Setup

1. **Application Monitoring**
   ```bash
   # Check backend logs
   tail -f uvicorn.log
   
   # Monitor system resources
   htop
   
   # Check API usage
   cat api_usage.log
   ```

2. **Quality Metrics**
   - Response accuracy assessment
   - User feedback collection
   - Error rate monitoring
   - Performance benchmarking

---

## Maintenance and Updates

### Regular Maintenance Tasks

#### **Weekly**
- [ ] Check API key usage and limits
- [ ] Review error logs for issues
- [ ] Test core functionality
- [ ] Update content caches if applicable

#### **Monthly**
- [ ] Update Python dependencies
- [ ] Review and update prompts based on usage
- [ ] Backup configuration states
- [ ] Performance optimization review

#### **Quarterly**
- [ ] API provider updates and changes
- [ ] Security patches and updates
- [ ] User feedback integration
- [ ] Feature enhancement planning

### Update Procedures

1. **Dependency Updates**
   ```bash
   # Activate virtual environment
   source venv/bin/activate
   
   # Update packages
   pip list --outdated
   pip install --upgrade [package]
   
   # Test functionality after updates
   ```

2. **Configuration Updates**
   - Save current state before changes
   - Test updates in development environment
   - Deploy incrementally to production
   - Monitor for issues post-deployment

3. **API Integration Updates**
   - Monitor API provider announcements
   - Test new API versions in staging
   - Update authentication methods as needed
   - Maintain backward compatibility when possible

---

## Conclusion

These installation case studies demonstrate Custom-Nerd/Nerd-Engine's flexibility and ease of deployment across different use cases:

- **DietNerd**: Full academic research setup with medical database integration
- **NewsNerd**: Streamlined current events configuration with news API integration  
- **Custom Domains**: Framework for creating specialized implementations

The modular architecture ensures that regardless of the target domain, the installation process follows consistent patterns while allowing for domain-specific customization and optimization.

For additional support:
- Review the main `README.md` for general setup guidance
- Consult `DETAILED_PROJECT_DOCUMENTATION.md` for architecture details
- Check `CASE_STUDIES_DOCUMENTATION.md` for configuration examples 