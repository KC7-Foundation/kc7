from code import interact
from datetime import datetime
from pickletools import floatnl
import string

class Clock():

    @staticmethod
    def get_current_gametime(start_time:datetime, seed_date:str, time_multiplier:int=1000) -> datetime:
        """
        Return current time in the game as timestamp
        """
        seed_date = datetime.timestamp(Clock.from_string(seed_date, format="%Y-%m-%d")) #TODO this could be simpler
        start_time = Clock.from_string(start_time).timestamp()
        computed_datetime = seed_date + (Clock._get_elapsed_time(start_time) * time_multiplier) 

        return computed_datetime

    @staticmethod
    def get_current_gametime_as_str(start_time:datetime, seed_date:str) -> str:
        """
        Return the current simulated time as timestamp
        """
        gametime = Clock.get_current_gametime(start_time=start_time, seed_date=seed_date)
        return str(gametime)


    @staticmethod
    def _get_elapsed_time(start_time:float) -> int:
        """
        Get number of real seconds since game was started
        """
        return datetime.now().timestamp() - start_time


    @staticmethod
    def is_business_hours(timestamp:float) -> bool:
        """
        params: time is a datetime object
        Returns true if time is within business hours (M-F 7-6PM local time)
        Returns false otherwise
        """
        time = datetime.fromtimestamp(timestamp) #convert timestamp to datetime

        if time.weekday in ["1", "7"]:
            return False
        elif time.hour > 18 or time.hour < 7:
            return False
        else:
            return True

    @staticmethod
    def from_string(time:str, format:str="%Y-%m-%d %H:%M:%S.%f"):
        """
        params: time - string in datetime format (.e.g '2014-03-22 07:54:43.010126')
        Return datetime object
        """
        return datetime.strptime(time, format)


    @staticmethod
    def from_string_to_timestamp(time:str, format:str="%Y-%m-%d %H:%M:%S.%f"):
        """
        params: time - string in datetime format (.e.g '2014-03-22 07:54:43.010126')
        Return timestamp float
        """
        return datetime.strptime(time, format).timestamp()

    @staticmethod
    def from_timestamp_to_string(timestamp: float):
        """
        params: timestamp - datetime as a timestamp (float)
        Return timestamp as string
        """
        return str(datetime.fromtimestamp(timestamp))

    @staticmethod
    def increment_time(start_time:float, increment:int) -> float:
        """
        Increment time locally without impacting system time
        params: start_time - datetime object
        params: increment - number of seconds to add to time
        Returns new local datetime
        """
        return start_time + increment
        

    # @staticmethod
    # def increment_time(start_time:datetime, increment:int) -> datetime:
    #     """
    #     Increment time locally without impacting system time
    #     params: start_time - datetime object
    #     params: increment - number of seconds to add to time
    #     Returns new local datetime
    #     """
    #     start_timestamp = datetime.timestamp(start_time) 
    #     calculated_timestamp = start_timestamp + increment
        
    #     return datetime.fromtimestamp(calculated_timestamp)

    # @staticmethod
    # def increment_datetime_str(str_time:str, increment_seconds:int) -> str:
    #     """
    #     Increment a datetime value that is given as string 
    #     params: str_time - datetime value as string
    #     increment_seconds - number of seconds t oadd to time
    #     Return a new datetime in string format
    #     """
    #     time_as_timestamp = Clock.from_string_to_timestamp(str_time) 
    #     # add time delay and convert back to datetime string
    #     return Clock.from_timestamp_to_string(time_as_timestamp + increment_seconds)