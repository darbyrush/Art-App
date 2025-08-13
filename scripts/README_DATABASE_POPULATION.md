# Database Population Scripts

This directory contains scripts to populate your art database with real artworks from various museum APIs.

## Available Scripts

### 1. `quick_populate.py` - Fast Testing (Recommended for Development)
- **Purpose**: Quickly populate database with a small number of artworks for testing
- **Default Target**: 100 artworks
- **Use Case**: Development, testing, quick demos
- **Speed**: Fast (few minutes)

**Usage:**
```bash
# Use default (100 artworks)
python scripts/quick_populate.py

# Specify custom target
python scripts/quick_populate.py 50
python scripts/quick_populate.py 200
```

### 2. `populate_db_comprehensive.py` - Full Production Population
- **Purpose**: Comprehensive population for production use
- **Default Target**: 1000 artworks
- **Use Case**: Production deployment, large exhibits
- **Speed**: Slower (10-30 minutes depending on target)

**Usage:**
```bash
# Use defaults (1000 total, 200 per source)
python scripts/populate_db_comprehensive.py

# Specify custom targets
python scripts/populate_db_comprehensive.py 500 100
python scripts/populate_db_comprehensive.py 2000 300
```

**Parameters:**
- First argument: Total target artworks
- Second argument: Maximum artworks per source

## What These Scripts Do

1. **Connect to Museum APIs**: Fetches from available sources:
   - Metropolitan Museum of Art (Met)
   - Cleveland Museum of Art
   - Art Institute of Chicago
   - Harvard Art Museums
   - Smithsonian Institution
   - Walters Art Museum
   - National Gallery (London)

2. **Fetch Real Artworks**: Gets actual artwork data including:
   - High-quality images
   - Artist information
   - Titles and dates
   - Museum departments
   - Origin information

3. **Store in Database**: Saves all data to your local database
4. **Avoid Duplicates**: Prevents duplicate artworks
5. **Progress Tracking**: Shows real-time progress and statistics

## Prerequisites

1. **Database Setup**: Ensure your database is configured and accessible
2. **API Keys**: Some sources require API keys (see `backend/config.py`)
3. **Dependencies**: All required Python packages installed
4. **Network Access**: Internet connection for API calls

## Running the Scripts

### Step 1: Navigate to Project Root
```bash
cd /path/to/your/art-app
```

### Step 2: Activate Virtual Environment (if using one)
```bash
source venv/bin/activate  # On macOS/Linux
# or
venv\Scripts\activate     # On Windows
```

### Step 3: Run Population Script
```bash
# Quick population (recommended first)
python scripts/quick_populate.py

# Or comprehensive population
python scripts/populate_db_comprehensive.py
```

## Expected Output

```
🚀 Quick Art Database Population
========================================
🎯 Target: 100 artworks

✅ Database initialized
📈 Current artworks: 0
🔍 Sources: cleveland, met, chicago, walters, national_gallery
📊 Fetching 20 per source...

🔄 cleveland...
   ✅ 20 artworks added

🔄 met...
   ✅ 20 artworks added

🔄 chicago...
   ✅ 20 artworks added

🔄 walters...
   ✅ 20 artworks added

🔄 national_gallery...
   ✅ 20 artworks added

🎉 Quick population complete!
📊 Total artworks: 100
🆕 New artworks: 100

⏱️ Time: 2.45 seconds
```

## Troubleshooting

### Common Issues

1. **Import Errors**: Make sure you're running from the project root directory
2. **Database Connection**: Check your database configuration in `database/config.py`
3. **API Rate Limits**: Some museums have rate limits - scripts include delays
4. **Memory Issues**: For very large datasets, the comprehensive script commits in batches

### Error Messages

- **"Database initialization warning"**: Usually safe to ignore, database may already exist
- **"No artworks returned from [source]"**: API may be temporarily unavailable
- **"Error processing artwork"**: Individual artwork issue, script continues

## Performance Tips

1. **Start Small**: Use `quick_populate.py` first to test
2. **Monitor Progress**: Watch the console output for progress
3. **Respectful API Usage**: Scripts include delays between API calls
4. **Batch Processing**: Large datasets are processed in batches to avoid memory issues

## After Population

Once your database is populated:

1. **Check Your Exhibit Page**: Navigate to your exhibit view to see the artworks
2. **Verify Data**: Check that images load and information displays correctly
3. **Monitor Performance**: Large datasets may affect page load times initially
4. **Consider Caching**: Implement image caching for better performance

## Customization

You can modify the scripts to:
- Change the target artwork counts
- Adjust delays between API calls
- Add more error handling
- Implement different filtering criteria
- Add progress bars or logging

## Support

If you encounter issues:
1. Check the console output for error messages
2. Verify your database configuration
3. Ensure all dependencies are installed
4. Check your internet connection for API access
