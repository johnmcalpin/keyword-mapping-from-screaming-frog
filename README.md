# Keyword to URL Mapper Using Screaming Frog

A powerful Python tool for mapping keywords to URLs using Screaming Frog data with intelligent scoring algorithms. Perfect for SEO professionals, content strategists, and digital marketers who need to efficiently map keyword lists to existing website content.

## 🚀 Features

- **Intelligent Scoring System**: Uses weighted scoring across multiple content fields (titles, headings, meta descriptions, URL structure)
- **One-to-One Mapping**: Each keyword gets assigned to exactly one URL (the best match)
- **Multiple Keywords per URL**: Popular URLs can have many relevant keywords assigned
- **Content Field Analysis**: Analyzes titles, H1/H2 tags, meta descriptions, URL paths, and more
- **Screaming Frog Integration**: Works seamlessly with Screaming Frog CSV exports
- **Quality Ratings**: Provides match quality ratings (Excellent, Good, Fair, Weak)
- **Comprehensive Reporting**: Detailed statistics and top matches summary
- **BOM Character Handling**: Robust CSV parsing that handles encoding issues

## 📋 Requirements

- Python 3.7+
- Required packages: `csv`, `logging`, `re`, `argparse`, `tqdm`, `pathlib`, `urllib.parse`, `collections`

## 🛠️ Installation

1. Clone this repository:
```bash
git clone https://github.com/johnmcalpin/keyword-mapping-from-screaming-frog.git
cd keyword-url-mapper
```

2. Create a virtual environment (recommended):
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install required packages:
```bash
pip install tqdm
```

## 📝 Input File Formats

### Keywords File (`keywords.txt`)
A simple text file with one keyword per line:
```
keyword 1
keyword 2
keyword 3
```

### Screaming Frog Export (`internal_all.csv`)
Export from Screaming Frog with these columns:
- **Address**: The URL of each page
- **Title 1**: Page title tag
- **H1-1**: Primary H1 heading
- **H2-1**: Primary H2 heading
- **Meta Description 1**: Meta description
- **Meta Keywords 1**: Meta keywords (if present)

## 🚀 Usage

### Basic Usage
```bash
python keywordmapper.py
```

This will use default filenames:
- Keywords: `keywords.txt`
- Screaming Frog data: `internal_all.csv`
- Output: `keyword_mappings_final.csv`

### Advanced Usage
```bash
python keywordmapper.py --keywords-file my_keywords.txt --screaming-frog-file my_data.csv --output-file results.csv --log-level DEBUG
```

### Command Line Options
- `--keywords-file`: Path to keywords text file (default: `keywords.txt`)
- `--screaming-frog-file`: Path to Screaming Frog CSV export (default: `internal_all.csv`)
- `--output-file`: Output CSV filename (default: `keyword_mappings_final.csv`)
- `--log-level`: Logging level - DEBUG, INFO, WARNING, ERROR (default: `INFO`)

## 📊 Output Format

The script generates a CSV file with these columns:

| Column | Description |
|--------|-------------|
| `keyword` | The input keyword |
| `matched_url` | The best matching URL |
| `match_score` | Numerical score (higher = better match) |
| `page_title` | Title of the matched page |
| `h1_heading` | H1 heading of the matched page |
| `meta_description` | Meta description of the matched page |
| `match_quality` | Quality rating (Excellent/Good/Fair/Weak) |

## 🧮 Scoring Algorithm

The tool uses a sophisticated weighted scoring system:

| Content Field | Weight | Description |
|---------------|--------|-------------|
| Page Title | 5.0× | Most important for keyword relevance |
| H1 Heading | 4.0× | Primary page topic indicator |
| URL Structure | 3.0× | Path and domain components |
| Meta Keywords | 2.5× | Explicit keyword targeting |
| Meta Description | 2.0× | Page summary content |
| H2 Headings | 1.5× | Secondary topic indicators |

**Scoring Logic:**
- **Exact phrase match**: 10 points (whole word) or 7 points (partial)
- **Multi-word matching**: Percentage of keyword words found × 5 points
- **Individual word matches**: 2 points per significant word (3+ characters)

## 📈 Example Results

```
KEYWORD MAPPING RESULTS
======================================================================
Total Keywords: 43
Matched Keywords: 43
Unmatched Keywords: 0
Match Rate: 100.0%
Unique URLs Matched: 28
Average Match Score: 89.3

TOP 10 MATCHES:
 1. 'playground shade structure' → playground-shade-structure (score: 125.0)
 2. 'commercial playground equipment' → commercial-playground-equipment (score: 125.0)
 3. 'commercial shade structures' → commercial-shade-structures (score: 120.0)
 4. 'shade sail installation' → sail-shade-installation (score: 105.0)
 5. 'playground equipment installation' → playground-installation (score: 98.8)
```

## 🔧 Troubleshooting

### Common Issues

**Empty URLs in results:**
- This is usually caused by BOM (Byte Order Mark) characters in CSV files
- The script automatically handles this, but ensure you're using the latest version

**Low match scores:**
- Check that your keywords align with actual page content
- Try using broader or more specific keywords
- Review the page titles and headings in your Screaming Frog data

**No matches found:**
- Verify your keywords file format (one keyword per line)
- Ensure your Screaming Frog export includes the required columns
- Check file paths and permissions

### Debug Mode
Run with debug logging to see detailed matching information:
```bash
python keywordmapper.py --log-level DEBUG
```

## 🎯 Best Practices

1. **Keyword Selection**: Use keywords that naturally appear in your content
2. **Quality Data**: Ensure your Screaming Frog export includes meta descriptions and headings
3. **Review Results**: Check match quality ratings and scores
4. **Iterative Process**: Refine keywords based on initial results

## 📁 File Structure
```
keyword-url-mapper/
├── keywordmapper.py          # Main script
├── keywords.txt              # Your keywords (one per line)
├── internal_all.csv          # Screaming Frog export
├── keyword_mappings_final.csv # Results output
├── keyword_mapper.log        # Execution log
└── README.md                 # This file
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/improvement`)
3. Commit your changes (`git commit -am 'Add new feature'`)
4. Push to the branch (`git push origin feature/improvement`)
5. Create a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built for SEO professionals and content strategists
- Designed to work seamlessly with Screaming Frog SEO Spider
- Optimized for large-scale keyword mapping projects

## 📞 Support

If you encounter any issues or have questions:
1. Check the troubleshooting section above
2. Review the debug logs (`keyword_mapper.log`)
3. Open an issue on GitHub with your error details and input file formats

---

**Made with ❤️ for the SEO community**
