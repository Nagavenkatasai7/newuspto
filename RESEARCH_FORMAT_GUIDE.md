# Research Format Export - User Guide

## 📋 Overview

The bulk party scraper now supports **Research Format Export** - a special format designed to match your existing research Excel database format. This allows you to **directly copy-paste** scraped opposition data into your research Excel file without any manual reformatting.

## 🎯 What is Research Format?

Research Format is a specific Excel layout where:
- **One row = One opposition** (not one trademark)
- Fixed metadata columns (brand_id, gvkey, company name, dates, results)
- **Alternating TM Type and Serial Number columns** for all trademarks in the opposition

### Format Structure

```
brand_id | gvkey | conm | Alt Name | Plaintiff | Marks | US GS | INT GS | Opp Start Date | Opp End Date | Result | TM Type | Serial No | TM Type | Serial No | ...
```

**Example:**
```
15011 | 3007 | BRINKER INTL INC | BRINKER INTL | 1 | 6 | 8 | 5 | 2019-10-23 | 2020-04-08 | 1 | 1 | 73100212 | 1 | 77246612 | 2 | 85400645 | 2 | 78863594 | 2 | 78855972
```

This opposition has 6 trademarks, so there are 6 pairs of (TM Type, Serial Number).

## 🚀 How to Use

### Step 1: Run Bulk Party Search

1. Go to "📦 Bulk Party Search" tab
2. Enter party name (e.g., "Nike Inc")
3. Click "🔍 Step 1: Find Oppositions"
4. Review results
5. Click "✅ Confirm & Start Scraping"
6. Wait for scraping to complete

### Step 2: Choose Research Format

1. Scroll down to "💾 Download Complete Results"
2. Select **"Research Format (Copy-Paste Ready)"**

### Step 3: Enter Metadata (Optional)

- **Brand ID**: Enter if you have one (e.g., "15011")
- **GVKEY**: Enter company GVKEY if you have it (e.g., "003007")
- **Leave blank** if you don't have these - you can fill them in Excel later

### Step 4: Download or Copy-Paste

**Option A: Download Excel File**
- Click "📥 Download Research Excel"
- Open the file
- Copy the rows
- Paste into your research Excel

**Option B: Direct Copy-Paste**
- Click on "📋 Copy Data for Paste" expander
- Select all the text in the code block
- Copy (Ctrl+C or Cmd+C)
- Go to your research Excel
- Click on the cell where you want to start pasting
- Paste (Ctrl+V or Cmd+V)
- Excel will automatically separate the data into columns!

**Option C: Download TSV**
- Click "📋 Download as TSV (Tab-Separated)"
- Open the .tsv file in Excel
- Copy and paste into your research Excel

## 📊 Column Definitions

### Fixed Columns (Always Present)

| Column | Description | Example | How It's Determined |
|--------|-------------|---------|---------------------|
| brand_id | Brand identifier | 15011 | Entered by you (optional) |
| gvkey | Company identifier | 003007 | Entered by you (optional) |
| conm | Company name | BRINKER INTL INC | From party search name |
| Alt Name | Alternative name | BRINKER INTL | Same as company name (you can edit) |
| Plaintiff | Is plaintiff? | 1 or 0 | 1 if party is plaintiff, 0 if defendant |
| Marks | Number of trademarks | 6 | Count of serial numbers |
| US GS | Unique US classes count | 8 | Count of unique US class codes |
| INT GS | Unique Intl classes count | 5 | Count of unique international class codes |
| Opp Start Date | Opposition filing date | 2019-10-23 | From TTABVue |
| Opp End Date | Opposition end date | 2020-04-08 | From TTABVue (termination date) |
| Result | Opposition result | 1, 0, or blank | 1=Sustained, 0=Dismissed, blank=Pending |

### Dynamic Columns (Based on Number of Trademarks)

After the fixed columns, the pattern alternates:

| Pattern | Description | Example |
|---------|-------------|---------|
| TM Type | Trademark type (0-3) | 1 |
| Serial No | Serial number | 73100212 |
| TM Type | Trademark type (0-3) | 1 |
| Serial No | Serial number | 77246612 |
| ... | ... | ... |

**TM Type Values:**
- **0** = No Image
- **1** = Standard Text
- **2** = Stylized/Design
- **3** = Slogan

## 💡 Tips & Best Practices

### 1. Handling Large Datasets
- If you have 100+ oppositions, consider downloading TSV instead of copy-pasting
- Excel may struggle with very wide pastes (oppositions with 50+ trademarks)

### 2. Filling Missing Data
- Leave brand_id and gvkey blank during export
- Fill them in your research Excel using VLOOKUP or INDEX-MATCH later
- This is faster than entering them one-by-one

### 3. Plaintiff/Defendant Detection
- The system automatically detects if the searched party is plaintiff or defendant
- Based on name matching (case-insensitive)
- May not be 100% accurate if multiple parties with similar names

### 4. Data Verification
- Always verify the "Marks" count matches your expectation
- Check that "Result" values make sense (Sustained vs Dismissed)
- Review the "Failed Serials" column in Standard Format if errors occurred

### 5. Combining with Existing Data
- Paste new data at the bottom of your research Excel
- Use Excel's "Remove Duplicates" feature based on Opposition Number
- Sort by dates or company name as needed

## 🔄 Comparison: Standard vs Research Format

| Feature | Standard Format | Research Format |
|---------|----------------|-----------------|
| **Layout** | One row per opposition with comma-separated lists | One row per opposition with alternating columns |
| **Best For** | Analysis, review, data exploration | Copy-pasting into existing research database |
| **Trademark Data** | Comma-separated in cells | Separate columns for each trademark |
| **Excel Compatibility** | Good for viewing | Perfect for database-style sheets |
| **Metadata** | Hidden sheet with stats | Embedded in each row |
| **Copy-Paste** | Requires reformatting | Direct paste ready |

## 📝 Example Workflow

**Scenario:** You're researching trademark oppositions for Nike Inc from 2020-2024.

1. **Search & Scrape**
   - Enter "Nike Inc"
   - Date range: 01/01/2020 to 12/31/2024
   - Find 47 oppositions
   - Scrape all (takes ~35 minutes first run, ~8 minutes repeat run)

2. **Export in Research Format**
   - Select "Research Format"
   - Enter brand_id: "12345" (if you have it)
   - Enter gvkey: "006174" (if you have it)
   - Click "Download Research Excel"

3. **Add to Database**
   - Open your research Excel
   - Scroll to the bottom row
   - Open the downloaded file
   - Copy all data rows (skip header)
   - Paste at the bottom of your research Excel
   - Save

4. **Clean Up (Optional)**
   - Remove duplicate oppositions if any
   - Fill in any missing metadata
   - Apply your Excel formatting/formulas
   - Create pivot tables for analysis

## ⚠️ Important Notes

### Data Accuracy
- All data comes directly from USPTO sources
- No manual entry or assumptions
- If a field is blank, it means USPTO didn't provide that data

### Opposition Numbers
- Opposition numbers are NOT included in the output
- Add an "Opposition Number" column in your Excel if you need to track them
- Or download Standard Format which includes opposition numbers

### Date Formats
- Dates are in YYYY-MM-DD format
- Excel may auto-convert to its default date format
- This is normal and expected

### Serial Number Formatting
- Serial numbers are 8-digit numbers
- Excel may remove leading zeros
- Format cells as "Text" to preserve leading zeros

## 🐛 Troubleshooting

### "Some columns appear empty"
- This is normal if different oppositions have different numbers of trademarks
- Excel shows empty cells for unused TM Type/Serial columns

### "Data pastes into one column"
- Make sure you're pasting tab-separated data
- Try downloading TSV and opening in Excel instead

### "Plaintiff column shows wrong values"
- The system matches party name to determine plaintiff
- If both parties have similar names, it may be incorrect
- Manually verify and correct as needed

### "brand_id and gvkey are blank"
- These are optional fields you provide
- System cannot determine these automatically
- Fill them in after pasting into your research Excel

## 📞 Support

If you encounter issues:
1. Check this guide first
2. Try downloading Standard Format to verify data is correct
3. Check BULK_SCRAPING_IMPLEMENTATION.md for technical details
4. Review the Streamlit console for error messages

---

**Version:** 1.0
**Last Updated:** October 2024
**Compatible With:** Example.xlsx research database format
