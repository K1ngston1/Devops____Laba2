"""
HMP Load Testing - Load Shapes

Defines load patterns (shapes) for different test scenarios.
Use with --class-picker to select shape and corresponding users.
"""

from locust import LoadTestShape  # type: ignore[attr-defined]


class AverageLoadShape(LoadTestShape):
    """
    Average Load Test Shape

    Pattern: 2m ramp to 10 → 9m hold → 2m ramp to 15 → 10m hold → 2m ramp down
    Duration: 25 minutes
    Users: StudentUser (80%), InstructorUser (20%)
    """

    RAMP_DURATION = 120
    FIRST_HOLD_DURATION = 540
    SECOND_HOLD_DURATION = 600
    INITIAL_USERS = 10
    PEAK_USERS = 15
    SPAWN_RATE = 5
    RAMP_DOWN_RATE = 7.5

    def tick(self):
        run_time = self.get_run_time()

        phase1_end = self.RAMP_DURATION
        phase2_end = phase1_end + self.FIRST_HOLD_DURATION
        phase3_end = phase2_end + self.RAMP_DURATION
        phase4_end = phase3_end + self.SECOND_HOLD_DURATION
        phase5_end = phase4_end + self.RAMP_DURATION

        if run_time < phase1_end:
            return (
                int(run_time / self.RAMP_DURATION * self.INITIAL_USERS),
                self.SPAWN_RATE,
            )
        elif run_time < phase2_end:
            return (self.INITIAL_USERS, self.SPAWN_RATE)
        elif run_time < phase3_end:
            user_increase = self.PEAK_USERS - self.INITIAL_USERS
            return (
                self.INITIAL_USERS
                + int((run_time - phase2_end) / self.RAMP_DURATION * user_increase),
                self.SPAWN_RATE,
            )
        elif run_time < phase4_end:
            return (self.PEAK_USERS, self.SPAWN_RATE)
        elif run_time < phase5_end:
            return (
                self.PEAK_USERS
                - int((run_time - phase4_end) / self.RAMP_DURATION * self.PEAK_USERS),
                self.RAMP_DOWN_RATE,
            )
        else:
            return None


class StressLoadShape(LoadTestShape):
    """
    Stress Test Shape

    Pattern: 4m ramp to 30 → 29m hold → 2m ramp down
    Duration: 35 minutes
    Users: StudentUser (80%), InstructorUser (20%)
    """

    RAMP_DURATION = 240
    HOLD_DURATION = 1740
    RAMP_DOWN_DURATION = 120
    PEAK_USERS = 30
    SPAWN_RATE = 7.5
    RAMP_DOWN_RATE = 15

    def tick(self):
        run_time = self.get_run_time()

        phase1_end = self.RAMP_DURATION
        phase2_end = phase1_end + self.HOLD_DURATION
        phase3_end = phase2_end + self.RAMP_DOWN_DURATION

        if run_time < phase1_end:
            return (
                int(run_time / self.RAMP_DURATION * self.PEAK_USERS),
                self.SPAWN_RATE,
            )
        elif run_time < phase2_end:
            return (self.PEAK_USERS, self.SPAWN_RATE)
        elif run_time < phase3_end:
            return (
                self.PEAK_USERS
                - int(
                    (run_time - phase2_end) / self.RAMP_DOWN_DURATION * self.PEAK_USERS
                ),
                self.RAMP_DOWN_RATE,
            )
        else:
            return None


class SpikeLoadShape(LoadTestShape):
    """
    Spike Test Shape

    Pattern: 1m ramp to 60 → 3m hold → 1m ramp down
    Duration: 5 minutes
    Users: SpikeStudentUser (95%), SpikeInstructorUser (5%)
    """

    RAMP_DURATION = 60
    HOLD_DURATION = 180
    RAMP_DOWN_DURATION = 60
    PEAK_USERS = 60
    SPAWN_RATE = 40

    def tick(self):
        run_time = self.get_run_time()

        phase1_end = self.RAMP_DURATION
        phase2_end = phase1_end + self.HOLD_DURATION
        phase3_end = phase2_end + self.RAMP_DOWN_DURATION

        if run_time < phase1_end:
            return (
                int(run_time / self.RAMP_DURATION * self.PEAK_USERS),
                self.SPAWN_RATE,
            )
        elif run_time < phase2_end:
            return (self.PEAK_USERS, self.SPAWN_RATE)
        elif run_time < phase3_end:
            return (
                self.PEAK_USERS
                - int(
                    (run_time - phase2_end) / self.RAMP_DOWN_DURATION * self.PEAK_USERS
                ),
                self.SPAWN_RATE,
            )
        else:
            return None


class BreakpointLoadShape(LoadTestShape):
    """
    Breakpoint Test Shape

    Pattern: Progressive ramp: 10 → 20 → 40 → 60 → 80 → 100 → 120 → 140 → 160 → 180 → 200 users
             2m ramp + 3m hold per step
    Duration: 57 minutes
    Users: StudentUser (80%), InstructorUser (20%)
    """

    RAMP_DURATION = 120
    HOLD_DURATION = 180
    RAMP_DOWN_DURATION = 120

    USER_LEVELS = [10, 20, 40, 60, 80, 100, 120, 140, 160, 180, 200]
    SPAWN_RATE_LOW = 5
    SPAWN_RATE_MED = 10
    SPAWN_RATE_HIGH = 15
    RAMP_DOWN_RATE = 20

    def tick(self):
        run_time = self.get_run_time()
        cumulative_time = 0

        for i, user_level in enumerate(self.USER_LEVELS):
            if user_level <= 20:
                spawn_rate = self.SPAWN_RATE_LOW
            elif user_level <= 100:
                spawn_rate = self.SPAWN_RATE_MED
            else:
                spawn_rate = self.SPAWN_RATE_HIGH

            ramp_end = cumulative_time + self.RAMP_DURATION
            hold_end = ramp_end + self.HOLD_DURATION

            if run_time < ramp_end:
                prev_users = self.USER_LEVELS[i - 1] if i > 0 else 0
                user_increase = user_level - prev_users
                progress = (run_time - cumulative_time) / self.RAMP_DURATION
                return (prev_users + int(progress * user_increase), spawn_rate)
            elif run_time < hold_end:
                return (user_level, spawn_rate)

            cumulative_time = hold_end

        ramp_down_end = cumulative_time + self.RAMP_DOWN_DURATION
        if run_time < ramp_down_end:
            remaining = 1 - (run_time - cumulative_time) / self.RAMP_DOWN_DURATION
            return (int(self.USER_LEVELS[-1] * remaining), self.RAMP_DOWN_RATE)

        return None


class SoakLoadShape(LoadTestShape):
    """
    Soak Test Shape

    Pattern: 2m ramp to 8 → 176m hold → 2m ramp down
    Duration: 180 minutes (3 hours)
    Users: StudentUser (80%), InstructorUser (20%)
    """

    RAMP_DURATION = 120
    HOLD_DURATION = 10560
    RAMP_DOWN_DURATION = 120
    STEADY_USERS = 8
    SPAWN_RATE = 1

    def tick(self):
        run_time = self.get_run_time()

        phase1_end = self.RAMP_DURATION
        phase2_end = phase1_end + self.HOLD_DURATION
        phase3_end = phase2_end + self.RAMP_DOWN_DURATION

        if run_time < phase1_end:
            return (
                int(run_time / self.RAMP_DURATION * self.STEADY_USERS),
                self.SPAWN_RATE,
            )
        elif run_time < phase2_end:
            return (self.STEADY_USERS, self.SPAWN_RATE)
        elif run_time < phase3_end:
            remaining = phase3_end - run_time
            return (
                int(remaining / self.RAMP_DOWN_DURATION * self.STEADY_USERS),
                self.SPAWN_RATE,
            )
        else:
            return None


class SmokeLoadShape(LoadTestShape):
    """
    Smoke Test Shape

    Pattern: Immediate ramp to 5 → 2m hold → immediate ramp down
    Duration: 2 minutes
    Users: StudentUser, InstructorUser (both active)
    """

    WARMUP_DURATION = 10
    HOLD_DURATION = 110
    USERS = 5
    SPAWN_RATE = 5

    def tick(self):
        run_time = self.get_run_time()

        phase1_end = self.WARMUP_DURATION
        phase2_end = phase1_end + self.HOLD_DURATION

        if run_time < phase1_end:
            return (self.USERS, self.SPAWN_RATE)
        elif run_time < phase2_end:
            return (self.USERS, self.SPAWN_RATE)
        else:
            return None
