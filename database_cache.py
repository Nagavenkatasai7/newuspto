#!/usr/bin/env python3
"""
Database Caching Layer for USPTO Opposition Scraper
Provides persistent caching of trademark data to reduce API calls.
"""

import sqlite3
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from contextlib import contextmanager
import threading


class TrademarkCache:
    """Thread-safe SQLite-based cache for trademark data."""

    def __init__(self, db_path: str = "trademark_cache.db", cache_ttl_days: int = 30):
        """
        Initialize the trademark cache.

        Args:
            db_path: Path to SQLite database file
            cache_ttl_days: Number of days before cached data is considered stale
        """
        self.db_path = db_path
        self.cache_ttl_days = cache_ttl_days
        self._lock = threading.Lock()
        self._initialize_database()

    @contextmanager
    def _get_connection(self):
        """Context manager for database connections."""
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row  # Enable dict-like row access
        try:
            yield conn
        finally:
            conn.close()

    def _initialize_database(self):
        """Create database tables if they don't exist."""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            # Main cache table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS trademark_cache (
                    serial_number TEXT PRIMARY KEY,
                    mark_name TEXT,
                    filing_date TEXT,
                    mark_type INTEGER DEFAULT 0,
                    us_classes TEXT,
                    international_classes TEXT,
                    description TEXT,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    api_call_count INTEGER DEFAULT 0,
                    error_message TEXT
                )
            """)

            # Index for fast date queries
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_last_updated
                ON trademark_cache(last_updated)
            """)

            # Statistics table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS cache_stats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    operation TEXT,
                    serial_number TEXT,
                    response_time_ms REAL
                )
            """)

            # Configuration table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS cache_config (
                    key TEXT PRIMARY KEY,
                    value TEXT,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Initialize default config
            cursor.execute("""
                INSERT OR IGNORE INTO cache_config (key, value) VALUES
                    ('cache_ttl_days', ?),
                    ('anthropic_calls_saved', '0'),
                    ('tsdr_calls_saved', '0')
            """, (str(self.cache_ttl_days),))

            conn.commit()

    def get_cached_data(self, serial_number: str) -> Optional[Dict]:
        """
        Retrieve cached trademark data if available and not stale.

        Args:
            serial_number: Trademark serial number

        Returns:
            Dict with trademark data or None if cache miss/stale
        """
        start_time = time.time()

        with self._lock:
            with self._get_connection() as conn:
                cursor = conn.cursor()

                # Calculate stale date
                stale_date = (datetime.now() - timedelta(days=self.cache_ttl_days)).isoformat()

                cursor.execute("""
                    SELECT * FROM trademark_cache
                    WHERE serial_number = ? AND last_updated > ?
                """, (serial_number, stale_date))

                row = cursor.fetchone()

                response_time = (time.time() - start_time) * 1000

                if row:
                    # Cache hit
                    self._log_stat('hit', serial_number, response_time)

                    # Parse JSON fields
                    data = {
                        'serial_number': row['serial_number'],
                        'mark_name': row['mark_name'],
                        'filing_date': row['filing_date'],
                        'mark_type': row['mark_type'],
                        'us_classes': json.loads(row['us_classes']) if row['us_classes'] else [],
                        'international_classes': json.loads(row['international_classes']) if row['international_classes'] else [],
                        'description': row['description'],
                        'cached': True,
                        'cache_date': row['last_updated']
                    }

                    return data
                else:
                    # Cache miss
                    self._log_stat('miss', serial_number, response_time)
                    return None

    def save_to_cache(self, serial_number: str, data: Dict):
        """
        Save trademark data to cache.

        Args:
            serial_number: Trademark serial number
            data: Dictionary containing trademark data
        """
        start_time = time.time()

        with self._lock:
            with self._get_connection() as conn:
                cursor = conn.cursor()

                # Serialize class arrays to JSON
                us_classes_json = json.dumps(data.get('us_classes', []))
                intl_classes_json = json.dumps(data.get('international_classes', []))

                # Insert or replace
                cursor.execute("""
                    INSERT OR REPLACE INTO trademark_cache (
                        serial_number, mark_name, filing_date, mark_type,
                        us_classes, international_classes, description,
                        last_updated, api_call_count, error_message
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP,
                              COALESCE((SELECT api_call_count FROM trademark_cache WHERE serial_number = ?), 0) + 1,
                              ?)
                """, (
                    serial_number,
                    data.get('mark_name', ''),
                    data.get('filing_date', ''),
                    data.get('mark_type', 0),
                    us_classes_json,
                    intl_classes_json,
                    data.get('description', ''),
                    serial_number,
                    data.get('error', None)
                ))

                conn.commit()

                response_time = (time.time() - start_time) * 1000
                operation = 'update' if cursor.rowcount > 0 else 'insert'
                self._log_stat(operation, serial_number, response_time)

    def _log_stat(self, operation: str, serial_number: str, response_time_ms: float):
        """Log cache operation statistics."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO cache_stats (operation, serial_number, response_time_ms)
                VALUES (?, ?, ?)
            """, (operation, serial_number, response_time_ms))
            conn.commit()

    def increment_api_savings(self, api_type: str):
        """
        Increment the count of saved API calls.

        Args:
            api_type: 'anthropic' or 'tsdr'
        """
        key_map = {
            'anthropic': 'anthropic_calls_saved',
            'tsdr': 'tsdr_calls_saved'
        }

        if api_type not in key_map:
            return

        with self._lock:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                key = key_map[api_type]

                cursor.execute("""
                    UPDATE cache_config
                    SET value = CAST((CAST(value AS INTEGER) + 1) AS TEXT),
                        updated_at = CURRENT_TIMESTAMP
                    WHERE key = ?
                """, (key,))

                conn.commit()

    def get_cache_statistics(self) -> Dict:
        """
        Get comprehensive cache statistics.

        Returns:
            Dictionary with cache metrics
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()

            # Total cached records
            cursor.execute("SELECT COUNT(*) as total FROM trademark_cache")
            total_cached = cursor.fetchone()['total']

            # Cache hits/misses in last 24 hours
            yesterday = (datetime.now() - timedelta(days=1)).isoformat()

            cursor.execute("""
                SELECT operation, COUNT(*) as count
                FROM cache_stats
                WHERE timestamp > ?
                GROUP BY operation
            """, (yesterday,))

            stats_24h = {row['operation']: row['count'] for row in cursor.fetchall()}

            hits = stats_24h.get('hit', 0)
            misses = stats_24h.get('miss', 0)
            total_requests = hits + misses

            hit_rate = (hits / total_requests * 100) if total_requests > 0 else 0

            # Average response times
            cursor.execute("""
                SELECT operation, AVG(response_time_ms) as avg_time
                FROM cache_stats
                WHERE timestamp > ?
                GROUP BY operation
            """, (yesterday,))

            avg_times = {row['operation']: row['avg_time'] for row in cursor.fetchall()}

            # API call savings
            cursor.execute("""
                SELECT key, value FROM cache_config
                WHERE key IN ('anthropic_calls_saved', 'tsdr_calls_saved')
            """)

            api_savings = {row['key']: int(row['value']) for row in cursor.fetchall()}

            # Stale records count
            stale_date = (datetime.now() - timedelta(days=self.cache_ttl_days)).isoformat()
            cursor.execute("""
                SELECT COUNT(*) as stale_count
                FROM trademark_cache
                WHERE last_updated <= ?
            """, (stale_date,))
            stale_count = cursor.fetchone()['stale_count']

            return {
                'total_cached_records': total_cached,
                'cache_hits_24h': hits,
                'cache_misses_24h': misses,
                'hit_rate_24h': round(hit_rate, 2),
                'avg_hit_time_ms': round(avg_times.get('hit', 0), 2),
                'avg_miss_time_ms': round(avg_times.get('miss', 0), 2),
                'anthropic_calls_saved': api_savings.get('anthropic_calls_saved', 0),
                'tsdr_calls_saved': api_savings.get('tsdr_calls_saved', 0),
                'stale_records': stale_count,
                'cache_ttl_days': self.cache_ttl_days
            }

    def clear_stale_records(self) -> int:
        """
        Remove stale records from cache.

        Returns:
            Number of records deleted
        """
        with self._lock:
            with self._get_connection() as conn:
                cursor = conn.cursor()

                stale_date = (datetime.now() - timedelta(days=self.cache_ttl_days)).isoformat()

                cursor.execute("""
                    DELETE FROM trademark_cache
                    WHERE last_updated <= ?
                """, (stale_date,))

                deleted_count = cursor.rowcount
                conn.commit()

                return deleted_count

    def clear_all_cache(self):
        """Clear all cached data (keep statistics)."""
        with self._lock:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM trademark_cache")
                conn.commit()

    def get_cached_serial_numbers(self) -> List[str]:
        """Get list of all cached serial numbers."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT serial_number FROM trademark_cache ORDER BY last_updated DESC")
            return [row['serial_number'] for row in cursor.fetchall()]

    def export_cache_to_json(self, filepath: str):
        """Export entire cache to JSON file."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM trademark_cache")

            records = []
            for row in cursor.fetchall():
                records.append({
                    'serial_number': row['serial_number'],
                    'mark_name': row['mark_name'],
                    'filing_date': row['filing_date'],
                    'mark_type': row['mark_type'],
                    'us_classes': json.loads(row['us_classes']) if row['us_classes'] else [],
                    'international_classes': json.loads(row['international_classes']) if row['international_classes'] else [],
                    'description': row['description'],
                    'last_updated': row['last_updated'],
                    'api_call_count': row['api_call_count']
                })

            with open(filepath, 'w') as f:
                json.dump(records, f, indent=2)


# Convenience functions for easy integration
def initialize_cache(db_path: str = "trademark_cache.db", ttl_days: int = 30) -> TrademarkCache:
    """Initialize and return a TrademarkCache instance."""
    return TrademarkCache(db_path, ttl_days)


if __name__ == "__main__":
    # Test the cache
    print("Testing TrademarkCache...")

    cache = initialize_cache()

    # Test data
    test_data = {
        'mark_name': 'TEST MARK',
        'filing_date': '2024-01-01',
        'mark_type': 2,
        'us_classes': [{'code': '001', 'description': 'Chemicals'}],
        'international_classes': [{'code': '001', 'description': 'Chemical products'}],
        'description': 'Test trademark'
    }

    # Save to cache
    print("\nSaving test data...")
    cache.save_to_cache('12345678', test_data)

    # Retrieve from cache
    print("\nRetrieving from cache...")
    cached = cache.get_cached_data('12345678')
    print(f"Cached data: {cached}")

    # Get statistics
    print("\nCache statistics:")
    stats = cache.get_cache_statistics()
    for key, value in stats.items():
        print(f"  {key}: {value}")

    print("\n✓ Cache test completed!")
