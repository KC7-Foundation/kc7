from code import interact
from datetime import datetime
from pickletools import floatnl
from random import randint
import random

class Clock():
    """
    A class used to determine in-game time and compute values related to it
    """

    @staticmethod
    def get_current_gametime(start_time: datetime, seed_date: str, time_multiplier: int = 10000) -> datetime:
        """
        Returns the current gametime as a datetime value based on a scaled multiple of real-world time

        Parameters
        ----------
        start_time : datetime
            The real-world datetime value when the game started running
        seed_date : str
            The time in-game when the simulation should start (example: 2022-01-01 will be the earliest in-game time)
        time_multiplier : int
            The value representing the multiplier between real-world and in-game time (default is 10000)

        Returns
        ----------
        datetime
            A datetime value representing the current in-game time
        """
        # TODO: time_multiplier should be read from global config
        seed_date = datetime.timestamp(Clock.from_string(
            seed_date, format="%Y-%m-%d"))  # TODO this could be simpler
        start_time = Clock.from_string(start_time).timestamp()
        computed_datetime = seed_date + \
            (Clock._get_elapsed_time(start_time) * time_multiplier)

        return computed_datetime

    @staticmethod
    def get_current_gametime_as_str(start_time: datetime, seed_date: str) -> str:
        """
        Return the current simulated time as timestamp
        """
        gametime = Clock.get_current_gametime(
            start_time=start_time, seed_date=seed_date)
        return str(gametime)

    @staticmethod
    def _get_elapsed_time(start_time: float) -> int:
        """
        Get number of real seconds since game was started
        """
        return datetime.now().timestamp() - start_time

    @staticmethod
    def is_business_hours(timestamp: float) -> bool:
        """
        params: time is a datetime object
        Returns true if time is within business hours (M-F 7-6PM local time)
        Returns false otherwise
        """
        time = datetime.fromtimestamp(
            timestamp)  # convert timestamp to datetime

        if time.weekday in ["1", "7"]:
            return False
        elif time.hour > 18 or time.hour < 7:
            return False
        else:
            return True

    @staticmethod
    def from_string(time: str, format: str = "%Y-%m-%d %H:%M:%S.%f") -> datetime:
        """
        params: time - string in datetime format (.e.g '2014-03-22 07:54:43.010126')
        Return datetime object
        """
        return datetime.strptime(time, format)

    @staticmethod
    def from_string_to_timestamp(time: str, format: str = "%Y-%m-%d %H:%M:%S.%f") -> float:
        """
        params: time - string in datetime format (.e.g '2014-03-22 07:54:43.010126')
        Return timestamp float
        """
        return datetime.strptime(time, format).timestamp()

    @staticmethod
    def from_timestamp_to_string(timestamp: float) -> str:
        """
        params: timestamp - datetime as a timestamp (float)
        Return timestamp as string
        """
        return str(datetime.fromtimestamp(timestamp))

    @staticmethod
    def increment_time(start_time: float, increment: int) -> float:
        """
        Increment time locally without impacting system time
        params: start_time - datetime object
        params: increment - number of seconds to add to time
        Returns new local datetime
        """
        return start_time + increment

    @staticmethod
    def delay_time_by(start_time: float, factor: str, is_negative=False, is_random=False) -> float:
        """
        Increment time by month, days, hours, minutes, seconds
        """
        if factor not in ["month","days","hours","minutes","seconds"]:
            raise Exception('"factor" must be one of the following values: ["days","hours","minutes","seconds"]')
        
        days, hours, minutes, seconds = 0, 0, 0, 0

        if is_random:
            direction = random.choice([1, -1])
        elif is_negative:
            direction = -1
        else:
            direction = 1

        if factor == "month":
            days = randint(1, 31) * direction
        if factor == "days":
            days = randint(1, 7) * direction
        elif factor == "hours":
            hours = randint(1,24) * direction
        elif factor == "minutes":
            minutes = randint(1, 60) * direction
        elif factor == "seconds":
            seconds = randint(1, 60) * direction



        increment_value = (days * 86400) + (hours * 3600) + (minutes * 60) + seconds

        return start_time + increment_value
