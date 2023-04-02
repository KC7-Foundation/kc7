from datetime import datetime, timedelta, time, date
from random import randint
import random
import numpy as np
from scipy.stats import norm

class Clock():
    """
    A class used to determine in-game time and compute values related to it
    """
    
    @staticmethod
    def generate_bimodal_timestamp(start_date: date, start_hour, day_length):
        """
        Generate a timestamp value based on a bimodal distribution
        centered around the middle of the time range specified.

        Parameters:
            start_time_str (str): A string representing the start time.
            end_time_str (str): A string representing the end time.

        Returns:
            A datetime object representing the generated timestamp.
        """
        start_time = datetime.combine(start_date, time(hour=start_hour))
        end_time = start_time + timedelta(hours=day_length)
        midpoint = start_time + (end_time - start_time) / 2
        bimodal_mean = [midpoint - timedelta(hours=2), midpoint + timedelta(hours=2)]
        bimodal_std = [timedelta(hours=1), timedelta(hours=1)]
        weights = [0.4, 0.6]
        # Generate a random index based on the weights
        index = np.random.choice([0, 1], p=weights)
        # Generate a random timestamp based on the selected bimodal distribution
        timestamp = datetime.fromtimestamp(norm.rvs(
            loc=bimodal_mean[index].timestamp(),
            scale=bimodal_std[index].total_seconds()))
        
        return timestamp
    
    @staticmethod
    def get_random_time() -> time:
        """
        Provides a random time component to be used alongside a constructed date
        """
        hour=randint(0,23)
        minute=randint(0,59)
        second=randint(0,59)

        return time(hour=hour, minute=minute, second=second)

    @staticmethod
    def is_business_hours(timestamp: float) -> bool:
        """
        DEPRECATED: Needs to be re-implemented using new timing logic
        """
        pass

    @staticmethod
    def from_timestamp_to_string(timestamp: float) -> str:
        """
        params: timestamp - datetime as a timestamp (float)
        Return timestamp as string
        """
        return datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")

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
    def weekday_to_string(weekday_int: int) -> str:
        return ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday'][weekday_int]
    
    @staticmethod
    def from_timestamp_to_weekday_string(timestamp: float) -> str:
        timestamp_as_date = date.fromtimestamp(timestamp)
        return Clock.weekday_to_string(timestamp_as_date.weekday())
    
    @staticmethod
    def get_time_near_start_of_workday(workday_start_hour: int) -> time:
        """
        Gets a random time within the first few hours of a workday
        """
        hours_at_start_of_day = [workday_start_hour, workday_start_hour+1, workday_start_hour+2]
        return time(
            hour=random.choice(hours_at_start_of_day),
            minute=randint(0,59),
            second=randint(0,59)
        )

    @staticmethod
    def delay_time_in_working_hours(start_time: float, factor: str, workday_start_hour: int, workday_length_hours: int, working_days_of_week: list) -> float:
        """
        This function can be called to increment a time within business hours for a given work schedule
        First, we will try a normal time increment
        From here, there are multiple possible scenarios:
        - The incremented time will not be a working weekday
            - If this is the case, we increment the day until we get to a weekday
        - The incremented time will be within working hours for the day
            - If this is the case, everything is OK and we return the timestamp
        - The incremented time is before the start of work for the current day
            - If this is the case, we get a datetime near the start of the current day
        - The incremented time is after the end of the current workday
            - If this the case, we go to near the start of the next working day
        NOTE: This function only works for forward increments. Reverse increments cannot be corrected to working hours
        """
        # Try to do a regular increment
        incremented_time = Clock.delay_time_by(start_time, factor)

        # If the adjusted time is not a working day, increment the day until we get to a working day
        while Clock.from_timestamp_to_weekday_string(incremented_time) not in working_days_of_week:
            incremented_time_as_datetime = datetime.fromtimestamp(incremented_time)
            incremented_time = (incremented_time_as_datetime + timedelta(days=1)).timestamp()

        # Is the incremented time within the working hours of that day?
        if Clock.get_start_of_workday(date.fromtimestamp(incremented_time), workday_start_hour)\
            <= incremented_time <=\
                Clock.get_end_of_workday(date.fromtimestamp(incremented_time), workday_start_hour, workday_length_hours):
            return incremented_time

        # If the adjusted time is before the start time of the current working day, then return a time near the start of this workday
        if incremented_time < Clock.get_start_of_workday(date.fromtimestamp(incremented_time), workday_start_hour):
            time_component = Clock.get_time_near_start_of_workday(workday_start_hour)
            current_date = date.fromtimestamp(incremented_time)
            return datetime.combine(date=current_date, time=time_component).timestamp()
        
        # If the adjusted time is after the end time of the current working day, then return a time near the start of the next workday
        if incremented_time > Clock.get_end_of_workday(date.fromtimestamp(incremented_time), workday_start_hour, workday_length_hours):
            new_date = (datetime.fromtimestamp(incremented_time) + timedelta(days=1)).date()
            time_component = Clock.get_time_near_start_of_workday(workday_start_hour)
            incremented_time = datetime.combine(date=new_date, time=time_component).timestamp()
            
            # Check again to make sure this is a working day
            while Clock.from_timestamp_to_weekday_string(incremented_time) not in working_days_of_week:
                incremented_time_as_datetime = datetime.fromtimestamp(incremented_time)
                incremented_time = (incremented_time_as_datetime + timedelta(days=1)).timestamp()

            return incremented_time
        
    @staticmethod
    def get_start_of_workday(current_date: date, start_hour:int):
        return datetime.combine(date=current_date, time=time(hour=start_hour)).timestamp()
    
    @staticmethod
    def get_end_of_workday(current_date: date, start_hour:int, workday_length_hours:int):
        start_of_workday = datetime.fromtimestamp(Clock.get_start_of_workday(current_date=current_date, start_hour=start_hour))
        return (start_of_workday + timedelta(hours=workday_length_hours)).timestamp()

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
        if factor in ["months", "days", "hours"]:
            hours = randint(1,24) * direction
        if factor in ["months", "days", "hours", "minutes"]:
            minutes = randint(1, 60) * direction
        if factor in ["months", "days", "hours", "minutes", "seconds"]:
            seconds = randint(1, 60) * direction

        increment_value = (days * 86400) + (hours * 3600) + (minutes * 60) + seconds

        return start_time + increment_value 