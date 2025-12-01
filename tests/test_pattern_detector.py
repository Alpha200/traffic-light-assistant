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
        
        assert result["has_pattern"] is True
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
        assert result["average_cycle_ms"] == 5 * 60 * 1000  # 5 minutes
        assert result["schedule_regularity"] == "regular"  # Low variation
    
    def test_daily_repeating_pattern(self):
        """Test detection of daily repeating patterns."""
        # Measurements at 8:30 AM over 3 consecutive days
        timestamps = [
            datetime(2025, 12, 1, 8, 30, 0),
            datetime(2025, 12, 2, 8, 30, 0),
            datetime(2025, 12, 3, 8, 30, 0),
        ]
        durations = [30000, 31000, 30500]  # ~30 seconds
        
        detector = PatternDetector(timestamps, durations)
        result = detector.analyze()
        
        assert result["has_pattern"] is True
        assert result["total_captures"] == 3
        assert result["average_duration_ms"] == 30500
        assert result["schedule_regularity"] == "regular"
        # Should detect 24-hour cycle
        assert result["average_cycle_ms"] is not None
        assert result["average_cycle_ms"] == 24 * 60 * 60 * 1000  # 24 hours
    
    def test_multiple_daily_patterns(self):
        """Test detection of multiple patterns at different times of day."""
        # Morning pattern at 8:30 and evening pattern at 17:30
        timestamps = [
            datetime(2025, 12, 1, 8, 30, 0),
            datetime(2025, 12, 1, 17, 30, 0),
            datetime(2025, 12, 2, 8, 30, 0),
            datetime(2025, 12, 2, 17, 30, 0),
            datetime(2025, 12, 3, 8, 30, 0),
        ]
        durations = [30000, 25000, 31000, 24000, 29500]
        
        detector = PatternDetector(timestamps, durations)
        result = detector.analyze()
        
        assert result["has_pattern"] is True
        assert result["total_captures"] == 5
        # Should detect daily patterns
        assert result["average_cycle_ms"] is not None
    
    def test_sparse_measurements_different_days(self):
        """Test with sparse measurements across different days."""
        # Random times across a week
        timestamps = [
            datetime(2025, 12, 1, 8, 30, 0),
            datetime(2025, 12, 3, 14, 15, 0),
            datetime(2025, 12, 5, 17, 45, 0),
            datetime(2025, 12, 7, 9, 0, 0),
        ]
        durations = [30000, 28000, 32000, 29000]
        
        detector = PatternDetector(timestamps, durations)
        result = detector.analyze()
        
        assert result["has_pattern"] is True
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
    
    def test_time_of_day_periods(self):
        """Test that measurements are correctly categorized by time of day."""
        # Various times throughout the day
        timestamps = [
            datetime(2025, 12, 1, 7, 0, 0),    # morning_rush
            datetime(2025, 12, 1, 10, 0, 0),   # late_morning
            datetime(2025, 12, 1, 13, 0, 0),   # lunch
            datetime(2025, 12, 1, 15, 0, 0),   # afternoon
            datetime(2025, 12, 1, 18, 0, 0),   # evening_rush
            datetime(2025, 12, 1, 21, 0, 0),   # evening
            datetime(2025, 12, 1, 2, 0, 0),    # night
        ]
        durations = [30000] * 7
        
        detector = PatternDetector(timestamps, durations)
        result = detector.analyze()
        
        assert result["has_pattern"] is True
        assert result["total_captures"] == 7
        # Should handle different time periods
        assert result["average_duration_ms"] == 30000
    
    def test_prediction_with_daily_pattern(self):
        """Test prediction of next green phase with daily pattern."""
        # Create a pattern at 8:30 AM for 3 days
        timestamps = [
            datetime(2025, 11, 28, 8, 30, 0),
            datetime(2025, 11, 29, 8, 30, 0),
            datetime(2025, 11, 30, 8, 30, 0),
        ]
        durations = [30000, 30000, 30000]
        
        detector = PatternDetector(timestamps, durations)
        result = detector.analyze()
        
        # Should predict next occurrence
        assert result["next_green_start"] is not None
        assert result["next_green_end"] is not None
    
    def test_time_bucket_grouping(self):
        """Test that similar times are grouped into 30-minute buckets."""
        # Times within the same 30-minute bucket (08:00-08:30)
        timestamps = [
            datetime(2025, 12, 1, 8, 15, 0),
            datetime(2025, 12, 2, 8, 20, 0),
            datetime(2025, 12, 3, 8, 25, 0),
        ]
        durations = [30000, 30000, 30000]
        
        detector = PatternDetector(timestamps, durations)
        result = detector.analyze()
        
        assert result["has_pattern"] is True
        # Should recognize these as the same daily pattern
        assert result["average_cycle_ms"] is not None
    
    def test_mixed_short_and_long_cycles(self):
        """Test with both short-term and long-term cycles."""
        # Some consecutive measurements + daily pattern
        timestamps = [
            datetime(2025, 12, 1, 8, 30, 0),
            datetime(2025, 12, 1, 8, 35, 0),  # 5 min later
            datetime(2025, 12, 2, 8, 30, 0),  # Next day
            datetime(2025, 12, 2, 8, 35, 0),  # 5 min later
        ]
        durations = [30000, 30000, 30000, 30000]
        
        detector = PatternDetector(timestamps, durations)
        result = detector.analyze()
        
        assert result["has_pattern"] is True
        assert result["total_captures"] == 4
        # Should detect some kind of cycle
        assert result["average_cycle_ms"] is not None
    
    def test_statistical_measures(self):
        """Test that statistical measures are correctly calculated."""
        timestamps = [
            datetime(2025, 12, 1, 8, 30, 0),
            datetime(2025, 12, 1, 8, 35, 0),
            datetime(2025, 12, 1, 8, 40, 0),
            datetime(2025, 12, 1, 8, 45, 0),
        ]
        durations = [30000, 32000, 28000, 30000]
        
        detector = PatternDetector(timestamps, durations)
        result = detector.analyze()
        
        assert result["average_duration_ms"] == 30000
        assert result["min_duration_ms"] == 28000
        assert result["max_duration_ms"] == 32000
        assert result["stddev_duration_ms"] is not None
        assert result["stddev_duration_ms"] > 0


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
        
        assert result["has_pattern"] is True
        assert result["total_captures"] == 2
        # Should not detect a daily pattern (too far apart)
        # But should still provide basic statistics
    
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
        
        assert result["has_pattern"] is True
        assert result["total_captures"] == 3
    
    def test_timezone_aware_timestamps(self):
        """Test with timezone-aware timestamps."""
        from datetime import timezone
        
        timestamps = [
            datetime(2025, 12, 1, 8, 30, 0, tzinfo=timezone.utc),
            datetime(2025, 12, 2, 8, 30, 0, tzinfo=timezone.utc),
        ]
        durations = [30000, 30000]
        
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


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
