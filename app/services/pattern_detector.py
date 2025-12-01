"""Pattern detection service for traffic light schedules."""

from typing import List, Dict, Tuple, Optional
from datetime import datetime, timedelta
from statistics import mean, stdev
from collections import defaultdict


class PatternDetector:
    """
    Service for detecting traffic light schedule patterns.
    
    Handles sparse measurements and detects daily repeating patterns by:
    - Grouping measurements by time-of-day periods
    - Detecting patterns at similar times across different days
    - Predicting next green phases based on historical patterns
    """
    
    def __init__(self, timestamps: List[datetime], durations: List[int]):
        """
        Initialize the pattern detector with measurement data.
        
        Args:
            timestamps: List of green light start times
            durations: List of green light durations in milliseconds
        """
        self.timestamps = timestamps
        self.durations = durations
        self.total_captures = len(timestamps)
        
    def analyze(self) -> Dict:
        """
        Analyze the measurements and return pattern information.
        
        Returns:
            Dictionary containing pattern statistics and predictions
        """
        if not self.timestamps:
            return {
                "has_pattern": False,
                "total_captures": 0
            }
        
        # Calculate basic statistics
        avg_duration = int(mean(self.durations))
        min_duration = min(self.durations)
        max_duration = max(self.durations)
        
        # Group by time periods and detect patterns
        time_periods = self._group_by_time_periods()
        daily_patterns = self._detect_daily_patterns()
        
        # Calculate cycle time
        avg_cycle_ms = self._calculate_average_cycle(daily_patterns)
        
        # Determine regularity
        schedule_regularity = self._determine_regularity(time_periods, daily_patterns)
        
        # Predict next green phase
        next_green_start, next_green_end = self._predict_next_green_phase(
            daily_patterns, avg_duration, avg_cycle_ms
        )
        
        # Calculate standard deviation
        std_dev = None
        if self.total_captures >= 3:
            std_dev = stdev(self.durations)
        
        return {
            "has_pattern": True,
            "average_duration_ms": avg_duration,
            "min_duration_ms": min_duration,
            "max_duration_ms": max_duration,
            "stddev_duration_ms": std_dev,
            "typical_duration_ms": avg_duration,
            "schedule_regularity": schedule_regularity,
            "total_captures": self.total_captures,
            "average_cycle_ms": avg_cycle_ms,
            "next_green_start": next_green_start,
            "next_green_end": next_green_end
        }
    
    @staticmethod
    def _get_time_of_day_period(dt: datetime) -> str:
        """Categorize time into periods for pattern detection."""
        hour = dt.hour
        if 6 <= hour < 9:
            return "morning_rush"
        elif 9 <= hour < 12:
            return "late_morning"
        elif 12 <= hour < 14:
            return "lunch"
        elif 14 <= hour < 17:
            return "afternoon"
        elif 17 <= hour < 20:
            return "evening_rush"
        elif 20 <= hour < 23:
            return "evening"
        else:
            return "night"
    
    @staticmethod
    def _get_time_bucket(dt: datetime, bucket_minutes: int = 30) -> str:
        """Get a time bucket (e.g., "08:30", "09:00") for grouping similar times across days."""
        bucket_hour = dt.hour
        bucket_minute = (dt.minute // bucket_minutes) * bucket_minutes
        return f"{bucket_hour:02d}:{bucket_minute:02d}"
    
    def _group_by_time_periods(self) -> Dict[str, List[int]]:
        """Group measurements by time-of-day periods."""
        periods = defaultdict(list)
        for ts, duration in zip(self.timestamps, self.durations):
            period = self._get_time_of_day_period(ts)
            periods[period].append(duration)
        return dict(periods)
    
    def _detect_daily_patterns(self) -> Dict[str, Dict]:
        """
        Detect daily repeating patterns by grouping measurements from similar times across different days.
        
        Returns:
            Dictionary with time buckets as keys and pattern info as values
        """
        # Group measurements by time bucket (30-minute intervals)
        time_buckets = defaultdict(lambda: {"durations": [], "timestamps": [], "cycle_times": []})
        
        for ts, duration in zip(self.timestamps, self.durations):
            bucket = self._get_time_bucket(ts, bucket_minutes=30)
            time_buckets[bucket]["durations"].append(duration)
            time_buckets[bucket]["timestamps"].append(ts)
        
        # Calculate cycle times within each bucket (time between occurrences on different days)
        daily_patterns = {}
        for bucket, data in time_buckets.items():
            if len(data["timestamps"]) >= 2:
                # Sort timestamps
                sorted_ts = sorted(data["timestamps"])
                
                # Calculate time differences (looking for ~24-hour cycles)
                cycle_times = []
                for i in range(len(sorted_ts) - 1):
                    diff_hours = (sorted_ts[i + 1] - sorted_ts[i]).total_seconds() / 3600
                    # If measurements are roughly 24 hours apart (20-28 hours to account for variation)
                    if 20 <= diff_hours <= 28:
                        cycle_times.append(diff_hours * 3600 * 1000)  # Convert to ms
                
                avg_duration = int(mean(data["durations"])) if data["durations"] else None
                avg_cycle = int(mean(cycle_times)) if cycle_times else None
                
                daily_patterns[bucket] = {
                    "avg_duration": avg_duration,
                    "avg_cycle": avg_cycle,
                    "sample_count": len(data["timestamps"]),
                    "last_occurrence": max(data["timestamps"]),
                    "durations": data["durations"],
                    "cycle_times": cycle_times
                }
        
        return daily_patterns
    
    def _calculate_average_cycle(self, daily_patterns: Dict) -> Optional[int]:
        """
        Calculate average cycle time, preferring daily pattern data if available.
        Falls back to consecutive measurements if daily patterns aren't detected.
        """
        # First, try to use daily patterns (24-hour cycles)
        all_daily_cycles = []
        for pattern in daily_patterns.values():
            if pattern.get("avg_cycle"):
                all_daily_cycles.append(pattern["avg_cycle"])
        
        if all_daily_cycles:
            return int(mean(all_daily_cycles))
        
        # Fallback: calculate from consecutive measurements (short-term cycles)
        if len(self.timestamps) >= 2:
            cycle_times = []
            for i in range(len(self.timestamps) - 1):
                cycle_ms = int((self.timestamps[i + 1] - self.timestamps[i]).total_seconds() * 1000)
                # Only consider cycles less than 30 minutes (typical traffic light cycle)
                if cycle_ms < 30 * 60 * 1000:
                    cycle_times.append(cycle_ms)
            
            if cycle_times:
                return int(mean(cycle_times))
        
        return None
    
    def _determine_regularity(self, time_periods: Dict, daily_patterns: Dict) -> Optional[str]:
        """
        Determine schedule regularity based on consistency across days and time periods.
        
        Returns:
            "regular", "somewhat_regular", "irregular", or None if insufficient data
        """
        if self.total_captures < 3:
            return None
        
        # Check if we have daily repeating patterns
        strong_daily_patterns = sum(1 for p in daily_patterns.values() if p["sample_count"] >= 2)
        
        if strong_daily_patterns >= 2:
            # Check consistency within daily patterns
            pattern_variances = []
            for pattern in daily_patterns.values():
                if len(pattern["durations"]) >= 2:
                    variance = stdev(pattern["durations"]) / mean(pattern["durations"])
                    pattern_variances.append(variance)
            
            if pattern_variances:
                avg_variance = mean(pattern_variances)
                if avg_variance < 0.1:  # Less than 10% variation
                    return "regular"
                elif avg_variance < 0.2:
                    return "somewhat_regular"
                else:
                    return "irregular"
        
        # Fallback: check overall variance
        std_dev = stdev(self.durations)
        avg_duration = mean(self.durations)
        variance = std_dev / avg_duration
        
        if variance < 0.1:
            return "regular"
        elif variance < 0.2:
            return "somewhat_regular"
        else:
            return "irregular"
    
    def _predict_next_green_phase(self, daily_patterns: Dict, avg_duration: int, 
                                   avg_cycle_ms: Optional[int]) -> Tuple[Optional[str], Optional[str]]:
        """
        Predict the next green phase using daily patterns.
        Looks for patterns at the current time of day based on historical data.
        """
        if not self.timestamps:
            return None, None
        
        now = datetime.now(self.timestamps[0].tzinfo)
        current_bucket = self._get_time_bucket(now, bucket_minutes=30)
        
        # Strategy 1: Use daily pattern for current time bucket
        if current_bucket in daily_patterns:
            pattern = daily_patterns[current_bucket]
            last_occurrence = pattern["last_occurrence"]
            
            # Check if last occurrence was yesterday or earlier
            hours_since = (now - last_occurrence).total_seconds() / 3600
            
            if hours_since >= 20:  # More than 20 hours ago
                # Predict based on 24-hour cycle
                predicted_next = last_occurrence + timedelta(days=1)
                # Adjust to today's date but keep the time
                predicted_next = predicted_next.replace(
                    year=now.year, month=now.month, day=now.day
                )
                
                next_green_start = predicted_next.isoformat()
                next_green_end = (predicted_next + timedelta(milliseconds=pattern["avg_duration"])).isoformat()
                return next_green_start, next_green_end
        
        # Strategy 2: Look for upcoming patterns within the next few hours
        upcoming_patterns = []
        for bucket, pattern in daily_patterns.items():
            bucket_hour, bucket_minute = map(int, bucket.split(':'))
            bucket_time = now.replace(hour=bucket_hour, minute=bucket_minute, second=0, microsecond=0)
            
            # If this time is in the future today
            if bucket_time > now:
                upcoming_patterns.append((bucket_time, pattern))
            # Or early tomorrow
            elif bucket_time <= now:
                tomorrow_time = bucket_time + timedelta(days=1)
                upcoming_patterns.append((tomorrow_time, pattern))
        
        if upcoming_patterns:
            # Sort by time and pick the nearest
            upcoming_patterns.sort(key=lambda x: x[0])
            next_time, pattern = upcoming_patterns[0]
            
            next_green_start = next_time.isoformat()
            next_green_end = (next_time + timedelta(milliseconds=pattern["avg_duration"])).isoformat()
            return next_green_start, next_green_end
        
        # Strategy 3: Fallback to simple cycle-based prediction (original logic)
        if avg_cycle_ms and len(self.timestamps) > 0:
            last_green_start = self.timestamps[-1]
            
            # If it's a short cycle (< 30 min), predict based on last measurement
            if avg_cycle_ms < 30 * 60 * 1000:
                next_start_dt = last_green_start + timedelta(milliseconds=avg_cycle_ms)
                next_green_start = next_start_dt.isoformat()
                next_end_dt = next_start_dt + timedelta(milliseconds=avg_duration)
                next_green_end = next_end_dt.isoformat()
                return next_green_start, next_green_end
        
        return None, None
