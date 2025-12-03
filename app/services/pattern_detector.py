"""Pattern detection service for traffic light schedules."""

from typing import List, Dict, Tuple, Optional
from datetime import datetime, timedelta, time
from statistics import mean, stdev


class PatternDetector:
    """
    Service for detecting traffic light schedule patterns.
    
    Uses a simplified approach:
    - Finds the smallest red gap between consecutive green lights (the base cycle)
    - Assumes this pattern repeats throughout the day
    - Projects the pattern over 24 hours
    - Validates the pattern against other measurements
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
        
        # Calculate standard deviation
        std_dev = None
        if self.total_captures >= 3:
            std_dev = stdev(self.durations)
        
        # Find the base pattern (smallest red gap)
        base_cycle_ms, red_duration_ms = self._find_base_cycle()
        
        # Determine regularity
        schedule_regularity = self._determine_regularity()
        
        # Predict next green phase
        next_green_start, next_green_end = self._predict_next_green_phase(
            base_cycle_ms, avg_duration
        )
        
        return {
            "has_pattern": base_cycle_ms is not None,
            "average_duration_ms": avg_duration,
            "min_duration_ms": min_duration,
            "max_duration_ms": max_duration,
            "stddev_duration_ms": std_dev,
            "typical_duration_ms": avg_duration,
            "schedule_regularity": schedule_regularity,
            "total_captures": self.total_captures,
            "average_cycle_ms": base_cycle_ms,
            "red_duration_ms": red_duration_ms,
            "next_green_start": next_green_start,
            "next_green_end": next_green_end
        }
    
    def _find_base_cycle(self) -> Tuple[Optional[int], Optional[int]]:
        """
        Find the base cycle by looking for the smallest red gap between green lights.
        
        The assumption is that the smallest red gap represents the basic pattern
        (green -> red -> green), which repeats throughout the day.
        
        Returns:
            Tuple of (cycle_time_ms, red_duration_ms) or (None, None) if not enough data
        """
        if len(self.timestamps) < 2:
            return None, None
        
        # Sort by timestamp to ensure chronological order
        sorted_data = sorted(zip(self.timestamps, self.durations))
        
        # Calculate red gaps between consecutive green lights
        red_gaps = []
        for i in range(len(sorted_data) - 1):
            green_start_1, green_duration_1 = sorted_data[i]
            green_start_2, green_duration_2 = sorted_data[i + 1]
            
            # Calculate when first green light ends
            green_end_1 = green_start_1 + timedelta(milliseconds=green_duration_1)
            
            # Calculate red duration (gap between green lights)
            red_duration = (green_start_2 - green_end_1).total_seconds() * 1000
            
            # Only consider positive red durations (ignore overlapping or same-day multiples)
            # Also filter out very large gaps (> 2 hours) as they're likely different days
            if 0 < red_duration < 2 * 60 * 60 * 1000:
                cycle_time = (green_start_2 - green_start_1).total_seconds() * 1000
                red_gaps.append({
                    'red_duration': red_duration,
                    'cycle_time': cycle_time,
                    'green_duration': green_duration_1
                })
        
        if not red_gaps:
            return None, None
        
        # Find the smallest red gap - this is our base pattern
        smallest_gap = min(red_gaps, key=lambda x: x['red_duration'])
        
        return int(smallest_gap['cycle_time']), int(smallest_gap['red_duration'])
    
    def _determine_regularity(self) -> Optional[str]:
        """
        Determine schedule regularity based on variance in durations.
        
        Returns:
            "regular", "somewhat_regular", "irregular", or None if insufficient data
        """
        if self.total_captures < 3:
            return None
        
        # Check variance in green light durations
        std_dev = stdev(self.durations)
        avg_duration = mean(self.durations)
        variance = std_dev / avg_duration
        
        if variance < 0.1:  # Less than 10% variation
            return "regular"
        elif variance < 0.2:  # Less than 20% variation
            return "somewhat_regular"
        else:
            return "irregular"
    
    def _predict_next_green_phase(self, base_cycle_ms: Optional[int], 
                                   avg_duration: int) -> Tuple[Optional[str], Optional[str]]:
        """
        Predict the next green phase based on the base cycle.
        
        Args:
            base_cycle_ms: The base cycle time in milliseconds
            avg_duration: Average green light duration
            
        Returns:
            Tuple of (next_green_start_iso, next_green_end_iso)
        """
        if not self.timestamps or not base_cycle_ms:
            return None, None
        
        # Use the most recent measurement as reference
        last_green_start = max(self.timestamps)
        
        # Handle timezone-aware timestamps
        if last_green_start.tzinfo is not None:
            now = datetime.now(last_green_start.tzinfo)
        else:
            now = datetime.now()
        
        # Project forward using the base cycle
        next_start_dt = last_green_start
        while next_start_dt <= now:
            next_start_dt = next_start_dt + timedelta(milliseconds=base_cycle_ms)
        
        next_end_dt = next_start_dt + timedelta(milliseconds=avg_duration)
        
        return next_start_dt.isoformat(), next_end_dt.isoformat()
    
    def get_daily_timeline(self, reference_date: Optional[datetime] = None) -> List[Dict]:
        """
        Generate a predicted timeline for a full day based on the detected pattern.
        
        Args:
            reference_date: The date to generate the timeline for (defaults to today)
            
        Returns:
            List of dicts with 'start_time', 'end_time', 'state' (green/red)
        """
        if not self.timestamps or len(self.timestamps) < 2:
            return []
        
        if reference_date is None:
            reference_date = datetime.now().date()
        
        # Get the base cycle
        base_cycle_ms, red_duration_ms = self._find_base_cycle()
        if not base_cycle_ms:
            return []
        
        avg_duration = int(mean(self.durations))
        
        # Find a measurement to use as reference (prefer one from same day of week if possible)
        # For simplicity, use the first measurement and align it by time of day
        reference_measurement = self.timestamps[0]
        reference_time = reference_measurement.time()
        
        # Start generating timeline from midnight
        timeline = []
        current_time = datetime.combine(reference_date, time(0, 0, 0))
        end_of_day = current_time + timedelta(days=1)
        
        # Find the first green light of the day by projecting backwards/forwards from reference
        first_green = datetime.combine(reference_date, reference_time)
        
        # Project backwards to find when the pattern starts (could be before reference time)
        while first_green > current_time:
            first_green = first_green - timedelta(milliseconds=base_cycle_ms)
        
        # Now project forward through the entire day
        current_green_start = first_green
        while current_green_start < end_of_day:
            green_end = current_green_start + timedelta(milliseconds=avg_duration)
            red_end = current_green_start + timedelta(milliseconds=base_cycle_ms)
            
            # Only add if within the day
            if current_green_start >= current_time and current_green_start < end_of_day:
                # Add green phase
                timeline.append({
                    'start_time': current_green_start.isoformat(),
                    'end_time': min(green_end, end_of_day).isoformat(),
                    'state': 'green'
                })
                
                # Add red phase
                if green_end < end_of_day:
                    timeline.append({
                        'start_time': green_end.isoformat(),
                        'end_time': min(red_end, end_of_day).isoformat(),
                        'state': 'red'
                    })
            
            current_green_start = red_end
        
        return timeline
    
    def validate_pattern(self, tolerance_ms: int = 5000) -> Dict:
        """
        Validate the detected pattern against all measurements.
        
        Checks if the projected pattern aligns with actual measurements within tolerance.
        
        Args:
            tolerance_ms: Time tolerance in milliseconds
            
        Returns:
            Dictionary with validation results
        """
        base_cycle_ms, _ = self._find_base_cycle()
        if not base_cycle_ms or len(self.timestamps) < 2:
            return {
                'is_valid': False,
                'matches': 0,
                'total': len(self.timestamps),
                'match_rate': 0.0
            }
        
        # Use first measurement as anchor point
        anchor = self.timestamps[0]
        anchor_time = anchor.time()
        
        matches = 0
        for ts in self.timestamps:
            # Check if this timestamp aligns with the pattern
            # Calculate time difference from anchor on the same day
            same_day_anchor = datetime.combine(ts.date(), anchor_time)
            
            # Find the nearest predicted green light
            time_diff = (ts - same_day_anchor).total_seconds() * 1000
            
            # Check if it's close to any multiple of the cycle
            remainder = time_diff % base_cycle_ms
            
            # Check both forward and backward alignment
            if remainder <= tolerance_ms or remainder >= (base_cycle_ms - tolerance_ms):
                matches += 1
        
        match_rate = matches / len(self.timestamps) if self.timestamps else 0.0
        
        return {
            'is_valid': match_rate >= 0.7,  # At least 70% match
            'matches': matches,
            'total': len(self.timestamps),
            'match_rate': match_rate
        }
