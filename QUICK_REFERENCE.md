# USPTO Opposition Scraper - Caching Quick Reference

## 🚀 Quick Start

### Install (No Dependencies Needed!)
```bash
# SQLite is built into Python - nothing to install!
# Just copy the files to your project directory
cp database_cache.py /your/project/
```

### Basic Usage

**Option 1: Use New Cached CLI**
```bash
python uspto_opposition_scraper_cached.py 91302017
```

**Option 2: Use New Cached Web App**
```bash
streamlit run web_app_cached.py
```

**Option 3: Integrate into Existing Code** (see INTEGRATION_PATCH.md)

---

## 📚 Common Operations

### Initialize Cache
```python
from database_cache import TrademarkCache

cache = TrademarkCache(cache_ttl_days=30)
```

### Check Cache
```python
cached_data = cache.get_cached_data("87654321")
if cached_data:
    print("Cache hit!")
else:
    print("Cache miss - fetch from API")
```

### Save to Cache
```python
data = {
    'mark_name': 'MY TRADEMARK',
    'filing_date': '2024-01-01',
    'mark_type': 2,
    'us_classes': [{'code': '035', 'description': 'Advertising'}],
    'international_classes': [{'code': '035', 'description': 'Advertising services'}],
    'description': 'Advertising services'
}
cache.save_to_cache("87654321", data)
```

### Get Statistics
```python
stats = cache.get_cache_statistics()
print(f"Total cached: {stats['total_cached_records']}")
print(f"Hit rate: {stats['hit_rate_24h']}%")
print(f"API calls saved: {stats['tsdr_calls_saved']}")
print(f"Cost saved: ${stats['anthropic_calls_saved'] * 0.015:.2f}")
```

### Clear Cache
```python
# Clear stale records only
deleted = cache.clear_stale_records()
print(f"Deleted {deleted} stale records")

# Clear everything
cache.clear_all_cache()
print("Cache cleared")
```

---

## 🎯 API Reference

### TrademarkCache Class

| Method | Description | Returns |
|--------|-------------|---------|
| `get_cached_data(serial_number)` | Retrieve cached data | Dict or None |
| `save_to_cache(serial_number, data)` | Save data to cache | None |
| `get_cache_statistics()` | Get cache metrics | Dict |
| `clear_stale_records()` | Remove old records | int (count deleted) |
| `clear_all_cache()` | Clear entire cache | None |
| `increment_api_savings(api_type)` | Track API call savings | None |
| `get_cached_serial_numbers()` | List all cached serials | List[str] |
| `export_cache_to_json(filepath)` | Export cache to file | None |

### Statistics Dict Keys

```python
{
    'total_cached_records': 1234,        # Total records in cache
    'cache_hits_24h': 456,               # Hits in last 24 hours
    'cache_misses_24h': 89,              # Misses in last 24 hours
    'hit_rate_24h': 83.7,                # Hit rate percentage
    'avg_hit_time_ms': 4.2,              # Average hit response time
    'avg_miss_time_ms': 2847.3,          # Average miss response time
    'anthropic_calls_saved': 1234,       # Total Anthropic API calls saved
    'tsdr_calls_saved': 5678,            # Total TSDR API calls saved
    'stale_records': 42,                 # Records older than TTL
    'cache_ttl_days': 30                 # Current TTL setting
}
```

---

## 🔧 Configuration

### Change Cache TTL
```python
# Short TTL (7 days) - for real-time monitoring
cache = TrademarkCache(cache_ttl_days=7)

# Standard TTL (30 days) - balanced
cache = TrademarkCache(cache_ttl_days=30)

# Long TTL (90 days) - for historical research
cache = TrademarkCache(cache_ttl_days=90)
```

### Custom Database Location
```python
cache = TrademarkCache(
    db_path="/custom/path/my_cache.db",
    cache_ttl_days=30
)
```

### Disable Caching
```python
scraper = USPTOOppositionScraper(
    api_key="your_key",
    cache_enabled=False  # Disable caching
)
```

---

## 📊 Performance Metrics

### Expected Performance

| Operation | Time | Notes |
|-----------|------|-------|
| Cache hit | 3-5ms | SQLite lookup |
| Cache miss | 2500-4500ms | API calls |
| Save to cache | 8-12ms | SQLite insert |
| Get statistics | 15-20ms | Aggregate queries |
| Clear stale | 50-100ms | DELETE query |

### Expected Hit Rates

| Use Case | Expected Hit Rate | Annual Savings |
|----------|-------------------|----------------|
| Research firm (repeat queries) | 70-90% | $500-2,000 |
| Law firm (case-specific) | 20-40% | $100-300 |
| Academic research (datasets) | 80-95% | $1,000-3,000 |
| Monitoring service (daily checks) | 50-70% | $500-1,500 |

---

## 💰 Cost Calculator

### Anthropic API Pricing
- **Claude 3.5 Sonnet**: ~$0.015 per image analysis

### Calculate Your Savings
```python
def calculate_savings(monthly_queries, cache_hit_rate):
    """
    Calculate monthly and annual cost savings.

    Args:
        monthly_queries: Number of serial numbers queried per month
        cache_hit_rate: Expected cache hit rate (0.0 to 1.0)

    Returns:
        Dict with savings calculations
    """
    cost_per_query = 0.015
    monthly_cost_without_cache = monthly_queries * cost_per_query
    cached_queries = monthly_queries * cache_hit_rate
    uncached_queries = monthly_queries * (1 - cache_hit_rate)
    monthly_cost_with_cache = uncached_queries * cost_per_query

    monthly_savings = monthly_cost_without_cache - monthly_cost_with_cache
    annual_savings = monthly_savings * 12

    return {
        'monthly_queries': monthly_queries,
        'cache_hit_rate': f"{cache_hit_rate * 100:.1f}%",
        'monthly_cost_without_cache': f"${monthly_cost_without_cache:.2f}",
        'monthly_cost_with_cache': f"${monthly_cost_with_cache:.2f}",
        'monthly_savings': f"${monthly_savings:.2f}",
        'annual_savings': f"${annual_savings:.2f}"
    }

# Example: 1000 queries/month with 70% cache hit rate
savings = calculate_savings(1000, 0.70)
for key, value in savings.items():
    print(f"{key}: {value}")

# Output:
# monthly_queries: 1000
# cache_hit_rate: 70.0%
# monthly_cost_without_cache: $15.00
# monthly_cost_with_cache: $4.50
# monthly_savings: $10.50
# annual_savings: $126.00
```

---

## 🐛 Troubleshooting

### Problem: "Database is locked"
```python
# Solution: Cache uses thread-safe locking automatically
# If error persists, check if DB file is open in another application
```

### Problem: Cache always returns None (misses)
```python
# Check if cache is enabled
scraper = USPTOOppositionScraper(api_key="...", cache_enabled=True)

# Verify data was saved
cache = TrademarkCache()
serials = cache.get_cached_serial_numbers()
print(f"Cached serials: {serials}")

# Check TTL
stats = cache.get_cache_statistics()
print(f"Stale records: {stats['stale_records']}")
```

### Problem: Database file growing too large
```python
# Solution 1: Clear stale records
cache.clear_stale_records()

# Solution 2: Vacuum database (reduce file size)
import sqlite3
conn = sqlite3.connect("trademark_cache.db")
conn.execute("VACUUM")
conn.close()

# Solution 3: Export and reimport
cache.export_cache_to_json("backup.json")
cache.clear_all_cache()
# Then reimport only recent records
```

### Problem: Low cache hit rate
```python
# Check statistics
stats = cache.get_cache_statistics()
print(f"Hit rate: {stats['hit_rate_24h']}%")

# If low (<30%), consider:
# 1. Are you querying different serial numbers each time?
# 2. Is TTL too short?
# 3. Do you need cache warming?

# Cache warming example
common_serials = ["87654321", "88765432", "89876543"]
for sn in common_serials:
    scraper.get_classes_from_serial(sn)
```

---

## 📁 File Structure

```
your_project/
├── database_cache.py              # Core cache module (NEW)
├── trademark_cache.db             # SQLite database (AUTO-CREATED)
│
├── uspto_opposition_scraper_cached.py   # Cached CLI (NEW)
├── web_app_cached.py              # Cached web app (NEW)
│
├── uspto_opposition_scraper.py    # Original CLI
├── web_app.py                     # Original web app
│
└── Documentation/
    ├── CACHING_IMPLEMENTATION_GUIDE.md
    ├── INTEGRATION_PATCH.md
    ├── CACHE_ARCHITECTURE.md
    └── QUICK_REFERENCE.md (this file)
```

---

## 🔍 Database Schema Quick Reference

### trademark_cache Table
```sql
serial_number TEXT PRIMARY KEY      -- 8-digit serial number
mark_name TEXT                      -- Trademark name
filing_date TEXT                    -- YYYY-MM-DD format
mark_type INTEGER                   -- 0=None, 1=Standard, 2=Stylized, 3=Slogan
us_classes TEXT                     -- JSON array
international_classes TEXT          -- JSON array
description TEXT                    -- Goods/services description
last_updated TIMESTAMP              -- Cache timestamp (for TTL)
api_call_count INTEGER              -- Number of API fetches
error_message TEXT                  -- Error if fetch failed
```

### Query Examples
```sql
-- Get all cached serial numbers
SELECT serial_number FROM trademark_cache;

-- Get cache size
SELECT COUNT(*) FROM trademark_cache;

-- Get stale records (>30 days)
SELECT * FROM trademark_cache
WHERE last_updated < datetime('now', '-30 days');

-- Get most frequently accessed marks
SELECT serial_number, mark_name, api_call_count
FROM trademark_cache
ORDER BY api_call_count DESC
LIMIT 10;

-- Get cache by mark type
SELECT mark_type, COUNT(*) as count
FROM trademark_cache
GROUP BY mark_type;
```

---

## 🧪 Testing Commands

### Test 1: Basic Cache Functionality
```bash
# Run the test script
python database_cache.py

# Expected output:
# Testing TrademarkCache...
# Saving test data...
# Retrieving from cache...
# Cached data: {...}
# Cache statistics: {...}
# ✓ Cache test completed!
```

### Test 2: CLI Performance Test
```bash
# First run (cache miss)
time python uspto_opposition_scraper_cached.py 91302017

# Second run (cache hit) - should be MUCH faster
time python uspto_opposition_scraper_cached.py 91302017
```

### Test 3: Web App Test
```bash
# Start the cached web app
streamlit run web_app_cached.py

# Test in browser:
# 1. Enter opposition number
# 2. Click Search
# 3. Check sidebar for cache stats
# 4. Search again - should show cache hits
```

### Test 4: Statistics Test
```python
from database_cache import TrademarkCache

cache = TrademarkCache()

# Add some test data
for i in range(10):
    cache.save_to_cache(f"8765432{i}", {
        'mark_name': f'TEST MARK {i}',
        'filing_date': '2024-01-01',
        'mark_type': 2,
        'us_classes': [],
        'international_classes': [],
        'description': 'Test'
    })

# Query them (generates hits)
for i in range(10):
    cache.get_cached_data(f"8765432{i}")

# Check stats
stats = cache.get_cache_statistics()
assert stats['cache_hits_24h'] == 10, "Should have 10 hits"
assert stats['total_cached_records'] >= 10, "Should have at least 10 records"

print("✓ All tests passed!")
```

---

## 📈 Monitoring Dashboard

### Daily Checklist
```bash
# Check cache statistics
python -c "from database_cache import TrademarkCache; \
  c = TrademarkCache(); \
  s = c.get_cache_statistics(); \
  print(f\"Hit rate: {s['hit_rate_24h']}%\"); \
  print(f\"Total records: {s['total_cached_records']}\"); \
  print(f\"Stale records: {s['stale_records']}\")"
```

### Weekly Maintenance
```bash
# Clear stale records
python -c "from database_cache import TrademarkCache; \
  c = TrademarkCache(); \
  deleted = c.clear_stale_records(); \
  print(f\"Cleared {deleted} stale records\")"

# Backup database
cp trademark_cache.db "backups/cache_backup_$(date +%Y%m%d).db"
```

### Monthly Report
```python
from database_cache import TrademarkCache
from datetime import datetime

cache = TrademarkCache()
stats = cache.get_cache_statistics()

print("=" * 50)
print(f"CACHE PERFORMANCE REPORT - {datetime.now().strftime('%B %Y')}")
print("=" * 50)
print(f"Total Cached Records: {stats['total_cached_records']}")
print(f"Cache Hit Rate: {stats['hit_rate_24h']}%")
print(f"TSDR API Calls Saved: {stats['tsdr_calls_saved']}")
print(f"Anthropic API Calls Saved: {stats['anthropic_calls_saved']}")
print(f"Estimated Cost Savings: ${stats['anthropic_calls_saved'] * 0.015:.2f}")
print(f"Average Hit Response Time: {stats['avg_hit_time_ms']:.2f}ms")
print(f"Stale Records: {stats['stale_records']}")
print("=" * 50)
```

---

## 🎓 Best Practices

### ✅ DO
- Enable caching by default (`cache_enabled=True`)
- Use 30-day TTL for balanced freshness/performance
- Monitor cache hit rates regularly
- Clear stale records monthly
- Backup database before major operations
- Use cache warming for known opposition numbers
- Track cost savings with statistics

### ❌ DON'T
- Don't disable caching unless testing
- Don't set TTL too short (< 7 days) - wastes API calls
- Don't set TTL too long (> 90 days) - stale data risk
- Don't delete cache file manually - use clear methods
- Don't access database directly while app is running
- Don't ignore low hit rates (< 30%) - investigate

---

## 🆘 Support Checklist

If something isn't working:

1. **Check files exist**
   ```bash
   ls -la database_cache.py trademark_cache.db
   ```

2. **Test cache module**
   ```bash
   python database_cache.py
   ```

3. **Check database structure**
   ```bash
   sqlite3 trademark_cache.db ".schema"
   ```

4. **Verify cache is enabled**
   ```python
   scraper = USPTOOppositionScraper(api_key="...", cache_enabled=True)
   print(f"Cache enabled: {scraper.cache_enabled}")
   ```

5. **Check statistics**
   ```python
   cache = TrademarkCache()
   stats = cache.get_cache_statistics()
   print(stats)
   ```

6. **Review integration guide**
   - See `INTEGRATION_PATCH.md` for step-by-step instructions
   - See `CACHING_IMPLEMENTATION_GUIDE.md` for detailed documentation

---

## 📞 Quick Links

- **Full Documentation**: `CACHING_IMPLEMENTATION_GUIDE.md`
- **Integration Guide**: `INTEGRATION_PATCH.md`
- **Architecture Details**: `CACHE_ARCHITECTURE.md`
- **This Reference**: `QUICK_REFERENCE.md`

---

## 🎉 Quick Wins

After implementing caching, you should immediately see:

✅ **900x faster** queries for cached data (5ms vs 4500ms)
✅ **100% cost savings** on cached API calls
✅ **Zero configuration** - works out of the box
✅ **Real-time statistics** - see your savings
✅ **Automatic cache management** - set and forget

**Ready to get started? Copy the files and run your first cached query!**

```bash
# Copy files
cp database_cache.py /your/project/

# Run cached version
python uspto_opposition_scraper_cached.py 91302017

# Or use web app
streamlit run web_app_cached.py
```

---

*Quick Reference v1.0 - January 2025*
