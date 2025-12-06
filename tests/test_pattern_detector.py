"""Tests for the PatternDetector service."""

import pytest
from datetime import datetime, timedelta
from app.services.pattern_detector import PatternDetector


class TestPatternDetector:
    """Test suite for PatternDetector class."""
    
    def test_empty_measurements(self):
        """Test with no measurements."""
        detector = PatternDetector([], [])
        result = detector.analyze()
        
        assert result["has_pattern"] is False
        assert result["total_captures"] == 0
    
    def test_single_measurement(self):
        """Test with a single measurement."""
        timestamp = datetime(2025, 12, 1, 8, 30, 0)
        duration = 30000  # 30 seconds
        
        detector = PatternDetector([timestamp], [duration])
        result = detector.analyze()
        
        assert result["has_pattern"] is False  # Can't detect pattern with 1 measurement
        assert result["total_captures"] == 1
        assert result["average_duration_ms"] == 30000
        assert result["min_duration_ms"] == 30000
        assert result["max_duration_ms"] == 30000
        assert result["schedule_regularity"] is None  # Not enough data
    
    def test_consecutive_measurements(self):
        """Test with consecutive measurements (short-term cycle)."""
        base_time = datetime(2025, 12, 1, 8, 30, 0)
        timestamps = [
            base_time,
            base_time + timedelta(minutes=5),
            base_time + timedelta(minutes=10),
            base_time + timedelta(minutes=15),
        ]
        durations = [30000, 31000, 29000, 30500]  # ~30 seconds, slight variation
        
        detector = PatternDetector(timestamps, durations)
        result = detector.analyze()
        
        assert result["has_pattern"] is True
        assert result["total_captures"] == 4
        assert result["average_duration_ms"] == 30125
        assert result["min_duration_ms"] == 29000
        assert result["max_duration_ms"] == 31000
        assert result["average_cycle_ms"] is not None  # Should find the 5-minute cycle
        assert result["schedule_regularity"] == "regular"  # Low variation
        
        # The smallest red gap should be ~4.5 minutes (270 seconds)
        # Cycle = 5 minutes = 300,000ms
        assert abs(result["average_cycle_ms"] - 5 * 60 * 1000) < 10000  # Within 10 seconds
    
    def test_daily_repeating_pattern(self):
        """Test detection of daily repeating patterns - not applicable with new logic."""
        # With new logic, we focus on short-term cycles within a day
        # Daily patterns are detected by the same mechanism
        timestamps = [
            datetime(2025, 12, 1, 8, 30, 0),
            datetime(2025, 12, 2, 8, 30, 0),
            datetime(2025, 12, 3, 8, 30, 0),
        ]
        durations = [30000, 31000, 30500]  # ~30 seconds
        
        detector = PatternDetector(timestamps, durations)
        result = detector.analyze()
        
        assert result["has_pattern"] is False  # 24h gaps are too large, filtered out
        assert result["total_captures"] == 3
        assert result["average_duration_ms"] == 30500
        assert result["schedule_regularity"] == "regular"
    
    def test_multiple_daily_patterns(self):
        """Test detection of multiple patterns at different times of day."""
        # Pattern with 5-minute cycles
        base_time = datetime(2025, 12, 1, 8, 30, 0)
        timestamps = [
            base_time,
            base_time + timedelta(minutes=5),
            base_time + timedelta(minutes=10),
            base_time + timedelta(minutes=15),
            base_time + timedelta(minutes=20),
        ]
        durations = [30000, 25000, 31000, 24000, 29500]
        
        detector = PatternDetector(timestamps, durations)
        result = detector.analyze()
        
        assert result["has_pattern"] is True
        assert result["total_captures"] == 5
        # Should detect the 5-minute cycle
        assert result["average_cycle_ms"] is not None
    
    def test_sparse_measurements_different_days(self):
        """Test with sparse measurements across different days."""
        # Random times across a week - should not find pattern
        timestamps = [
            datetime(2025, 12, 1, 8, 30, 0),
            datetime(2025, 12, 3, 14, 15, 0),
            datetime(2025, 12, 5, 17, 45, 0),
            datetime(2025, 12, 7, 9, 0, 0),
        ]
        durations = [30000, 28000, 32000, 29000]
        
        detector = PatternDetector(timestamps, durations)
        result = detector.analyze()
        
        assert result["has_pattern"] is False  # Gaps too large
        assert result["total_captures"] == 4
        assert result["average_duration_ms"] == 29750
        # With sparse data, should still provide some analysis
        assert result["schedule_regularity"] is not None
    
    def test_irregular_pattern(self):
        """Test detection of irregular patterns with high variation."""
        base_time = datetime(2025, 12, 1, 8, 30, 0)
        timestamps = [
            base_time,
            base_time + timedelta(minutes=5),
            base_time + timedelta(minutes=10),
            base_time + timedelta(minutes=15),
        ]
        # High variation in durations
        durations = [20000, 50000, 25000, 60000]
        
        detector = PatternDetector(timestamps, durations)
        result = detector.analyze()
        
        assert result["has_pattern"] is True
        assert result["schedule_regularity"] == "irregular"
    
    def test_somewhat_regular_pattern(self):
        """Test detection of somewhat regular patterns."""
        base_time = datetime(2025, 12, 1, 8, 30, 0)
        timestamps = [
            base_time,
            base_time + timedelta(minutes=5),
            base_time + timedelta(minutes=10),
            base_time + timedelta(minutes=15),
        ]
        # Moderate variation - between 10-20% variance for somewhat_regular
        durations = [30000, 38000, 32000, 40000]
        
        detector = PatternDetector(timestamps, durations)
        result = detector.analyze()
        
        assert result["has_pattern"] is True
        assert result["schedule_regularity"] == "somewhat_regular"
    
    def test_pattern_detection_simple(self):
        """Test simple pattern detection with clear cycle."""
        # Traffic light with 2-minute cycle: 30s green, 90s red
        base_time = datetime(2025, 12, 1, 8, 0, 0)
        timestamps = [
            base_time,
            base_time + timedelta(minutes=2),
            base_time + timedelta(minutes=4),
            base_time + timedelta(minutes=6),
        ]
        durations = [30000, 30000, 30000, 30000]  # All 30 seconds
        
        detector = PatternDetector(timestamps, durations)
        result = detector.analyze()
        
        assert result["has_pattern"] is True
        assert result["total_captures"] == 4
        assert result["average_duration_ms"] == 30000
        # Cycle should be 2 minutes (120,000ms)
        assert result["average_cycle_ms"] == 120000
        # Red duration should be ~90 seconds (90,000ms)
        assert result["red_duration_ms"] == 90000
    
    def test_timeline_generation(self):
        """Test generation of daily timeline."""
        base_time = datetime(2025, 12, 1, 8, 0, 0)
        timestamps = [
            base_time,
            base_time + timedelta(minutes=2),
            base_time + timedelta(minutes=4),
        ]
        durations = [30000, 30000, 30000]
        
        detector = PatternDetector(timestamps, durations)
        timeline = detector.get_daily_timeline(reference_date=datetime(2025, 12, 1).date())
        
        # Should generate timeline entries
        assert len(timeline) > 0
        
        # Check structure
        assert all('start_time' in entry for entry in timeline)
        assert all('end_time' in entry for entry in timeline)
        assert all('state' in entry for entry in timeline)
        assert all(entry['state'] in ['green', 'red'] for entry in timeline)
    
    def test_timeline_generation_limited_hours(self):
        """Test generation of timeline limited to specific hours."""
        base_time = datetime(2025, 12, 1, 8, 0, 0)
        timestamps = [
            base_time,
            base_time + timedelta(minutes=2),
            base_time + timedelta(minutes=4),
        ]
        durations = [30000, 30000, 30000]
        
        detector = PatternDetector(timestamps, durations)
        # Generate timeline for only 1 hour
        timeline_1h = detector.get_daily_timeline(reference_date=datetime(2025, 12, 1).date(), hours=1)
        # Generate timeline for full day (24 hours)
        timeline_24h = detector.get_daily_timeline(reference_date=datetime(2025, 12, 1).date(), hours=24)
        
        # 1-hour timeline should have fewer entries than 24-hour timeline
        assert len(timeline_1h) < len(timeline_24h)
        assert len(timeline_1h) > 0
        
        # Check that all entries are valid
        assert all('start_time' in entry for entry in timeline_1h)
        assert all('end_time' in entry for entry in timeline_1h)
        assert all('state' in entry for entry in timeline_1h)
    
    def test_pattern_validation(self):
        """Test pattern validation against measurements."""
        base_time = datetime(2025, 12, 1, 8, 0, 0)
        timestamps = [
            base_time,
            base_time + timedelta(minutes=2),
            base_time + timedelta(minutes=4),
            base_time + timedelta(minutes=6),
        ]
        durations = [30000, 30000, 30000, 30000]
        
        detector = PatternDetector(timestamps, durations)
        validation = detector.validate_pattern()
        
        assert validation['is_valid'] is True
        assert validation['match_rate'] > 0.7  # At least 70% match
        assert validation['matches'] >= 3
        assert validation['total'] == 4


class TestPatternDetectorEdgeCases:
    """Test edge cases and boundary conditions."""
    
    def test_very_long_cycle(self):
        """Test with measurements very far apart."""
        timestamps = [
            datetime(2025, 12, 1, 8, 30, 0),
            datetime(2025, 12, 15, 8, 30, 0),  # 2 weeks later
        ]
        durations = [30000, 30000]
        
        detector = PatternDetector(timestamps, durations)
        result = detector.analyze()
        
        assert result["has_pattern"] is False  # Gap too large (> 2 hours)
        assert result["total_captures"] == 2
        # Should still provide basic statistics
    
    def test_same_time_same_day(self):
        """Test with multiple measurements at the same time on the same day."""
        base_time = datetime(2025, 12, 1, 8, 30, 0)
        timestamps = [
            base_time,
            base_time + timedelta(seconds=30),
            base_time + timedelta(minutes=1),
        ]
        durations = [30000, 30000, 30000]
        
        detector = PatternDetector(timestamps, durations)
        result = detector.analyze()
        
        # Very short cycles might not be detected as pattern
        # (red duration would be negative or very small)
        assert result["total_captures"] == 3
        # Should still provide basic statistics
        assert result["average_duration_ms"] == 30000
    
    def test_timezone_aware_timestamps(self):
        """Test with timezone-aware timestamps."""
        from datetime import timezone
        
        base_time = datetime(2025, 12, 1, 8, 0, 0, tzinfo=timezone.utc)
        timestamps = [
            base_time,
            base_time + timedelta(minutes=2),
            base_time + timedelta(minutes=4),
        ]
        durations = [30000, 30000, 30000]
        
        detector = PatternDetector(timestamps, durations)
        result = detector.analyze()
        
        assert result["has_pattern"] is True
        # Should handle timezone-aware datetime objects
        assert result["next_green_start"] is not None
    
    def test_duration_variance_threshold(self):
        """Test regularity detection at variance thresholds."""
        base_time = datetime(2025, 12, 1, 8, 30, 0)
        
        # Exactly at regular threshold (10% variance)
        timestamps = [base_time + timedelta(minutes=i*5) for i in range(5)]
        avg = 30000
        durations = [avg, avg * 1.05, avg * 0.95, avg * 1.08, avg * 0.92]
        
        detector = PatternDetector(timestamps, durations)
        result = detector.analyze()
        
        assert result["schedule_regularity"] in ["regular", "somewhat_regular"]
    
    def test_overlapping_green_lights(self):
        """Test with overlapping measurements (shouldn't happen but handle gracefully)."""
        base_time = datetime(2025, 12, 1, 8, 0, 0)
        timestamps = [
            base_time,
            base_time + timedelta(seconds=10),  # Overlaps with first
        ]
        durations = [30000, 30000]
        
        detector = PatternDetector(timestamps, durations)
        result = detector.analyze()
        
        # Should handle without crashing
        assert result["total_captures"] == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
