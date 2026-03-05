# Module 3: Document Loading

## Learning Objectives
- Master different document loading strategies for RAG systems
- Compare text, PDF, and web-based content loading approaches
- Understand content cleaning and preprocessing techniques
- Build unified knowledge bases from multiple file types
- Learn best practices for production document ingestion

## Prerequisites
- Completed Module 2 (Vector Stores)
- Understanding of document chunking and embeddings
- OpenAI API key configured

## Scripts in This Module

### 1. `1_text_files.py` - Text File Loading Fundamentals
Master the basics of loading text documents:
- Single file vs. multiple file loading patterns
- Directory-based loading with glob patterns
- Content metadata management
- Chunk distribution analysis across documents

**Key learning:** Different approaches to text file ingestion and their trade-offs

### 2. `2_pdf_loading.py` - PDF Document Processing
Handle PDF documents in RAG systems:
- PDF creation from text sources (for demonstration)
- PDF text extraction using PyPDFLoader
- Page-level metadata preservation
- Comparison of PDF vs. text loading results

**Key learning:** PDF-specific considerations and processing techniques

### 3. `3_web_sources.py` - Web Content Integration
Load content from web sources:
- URL accessibility checking with proper headers
- Web scraping with WebBaseLoader
- Simplified content cleaning using BeautifulSoup
- BeautifulSoup vs basic text processing comparison
- Rate limiting and error handling

**Key learning:** Web content integration with effective cleaning strategies

**Note:** Only 3 scripts are currently implemented in this module.

## Key Concepts

- **Document Loaders**: Specialized classes for different file types and sources
- **Content Cleaning**: Removing artifacts and normalizing text from various sources
- **Metadata Management**: Tracking source information and document properties
- **Source Provenance**: Maintaining information about where content originated
- **Format-Specific Processing**: Handling unique characteristics of each document type
- **Unified Ingestion**: Creating consistent processing pipelines for mixed content

## Document Type Comparison

| Feature | Text Files | PDF Files | Web Sources |
|---------|------------|-----------|-------------|
| **Processing Speed** | 🟢 Fastest | 🟡 Medium | 🔴 Slowest |
| **Content Quality** | 🟢 Clean | 🟡 May have artifacts | 🟡 Cleanable |
| **Reliability** | 🟢 High | 🟢 High | 🟡 Network dependent |
| **Setup Complexity** | 🟢 Simple | 🟡 Medium | 🟡 Medium |
| **Metadata Richness** | 🔴 Basic | 🟢 Rich | 🟡 Medium |
| **Best For** | Simple content | Documents | Live/current data |

## Running the Code

```bash
# Basic text file loading
uv run python "03_document_loading/1_text_files.py"

# PDF document processing (creates sample PDFs)
uv run python "03_document_loading/2_pdf_loading.py"

# Web content integration (requires internet)
uv run python "03_document_loading/3_web_sources.py"
```

## Expected Behavior

**1_text_files.py:**
- Demonstrates 4 loading approaches with the same content
- Shows chunk distribution across scientists
- Creates comprehensive comparison analysis

**2_pdf_loading.py:**
- Creates `datasets/pdfs/` directory with sample PDFs
- Compares PDF vs. text extraction results
- Shows page-level processing capabilities

**3_web_sources.py:**
- Loads from Wikipedia URLs with accessibility checks
- Demonstrates simplified content cleaning with BeautifulSoup
- Shows successful RAG question-answering with web content
- Handles network errors gracefully with proper fallbacks

## Dependencies Added

This module adds several new dependencies:
- **pypdf**: PDF text extraction
- **reportlab**: PDF creation for demonstrations
- **requests**: HTTP requests for web content
- **beautifulsoup4**: HTML parsing and cleaning

## Common Issues

- **PDF extraction quality**: Some PDFs may have poor text extraction
- **Web access**: Scripts handle network failures with fallback content
- **Content encoding**: Files must be UTF-8 compatible
- **Rate limiting**: Web scripts include delays to respect server limits
- **File permissions**: Ensure write access for creating sample files

## Content Processing Pipeline

1. **Source Detection**: Identify file type and appropriate loader
2. **Content Extraction**: Use format-specific extraction methods
3. **Cleaning**: Remove artifacts and normalize formatting
4. **Metadata Enrichment**: Add source tracking and document properties
5. **Chunking**: Apply consistent text splitting across all sources
6. **Indexing**: Create unified embeddings regardless of source type

## Best Practices by Source Type

**Text Files:**
- Use DirectoryLoader with glob patterns for flexibility
- Implement consistent metadata schemas
- Consider file encoding issues

**PDF Files:**
- Test extraction quality with your specific PDF types
- Preserve page-level information in metadata
- Handle text extraction failures gracefully

**Web Sources:**
- Always check robots.txt and terms of service
- Implement rate limiting and respectful crawling
- Use simplified, robust cleaning approaches
- Handle network failures gracefully
- Clean navigation and UI elements effectively