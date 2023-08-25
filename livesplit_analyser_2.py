from bs4 import BeautifulSoup
from datetime import datetime,timedelta,time

class Splits_File:
    def __init__(self, splits = [], uses_subsplits = False, runs = {}, \
                 path = "", game = "", category = "", uses_game_time = True):
        self.splits = splits
        self.uses_subsplits = uses_subsplits
        self.runs = runs
        self.path = path
        self.game = game
        self.uses_game_time = uses_game_time
        self.category = category
    
    def load_whole_file(self, xml_data):
        self.load_meta_data(xml_data)
        self.load_attempt_history(xml_data)
        self.load_segment_history(xml_data)

    def load_meta_data(self, xml_data):
        game_name = xml_data.find("GameName")
        category_name = xml_data.find("CategoryName")
        if game_name: self.game = game_name.getText()
        if category_name: self.category = category_name.getText()

    def load_attempt_history(self, xml_data):
        results = xml_data.find_all("Attempt")
        for attempt in results:
            run_completed = False
            attempt_id, time, pause_time = None, None, None
            attempt_id = int(attempt.get("id"))
            start_date = attempt.get("started")
            end_date = attempt.get("ended")
            if start_date: start_date = datetime.strptime(start_date, "%m/%d/%Y %H:%M:%S")
            if end_date:end_date = datetime.strptime(end_date, "%m/%d/%Y %H:%M:%S")
            if len(attempt) != 0:
                run_completed = True
                if self.uses_game_time == True: time = attempt.find("GameTime")
                elif self.uses_game_time == False: time = attempt.find("RealTime")
                else: raise ValueError
            pause_time = attempt.find("PauseTime")
            if time:
                time = datetime.strptime(time.getText()[:-4], "%H:%M:%S.%f").time()
            if pause_time: 
                pause_time = datetime.strptime(pause_time.getText()[:-4], "%H:%M:%S.%f").time()
            new_attempt = Attempt(attempt_id, start_date, end_date, time, pause_time, run_completed)

            self.runs[attempt_id] = new_attempt
           
    def load_segment_history(self, xml_data):
        result = xml_data.find_all("Segment")
        run_time = {}
        for split in result:
            split_gold = None
            is_supersplit = False
            split_name = split.find("Name").getText()
            segment_history = split.find_all("Time")
            if split_name.find("{") != -1 and split_name.find("}") != -1: is_supersplit = True
            for attempt_information in segment_history:
                is_gold = False
                attempt_id = int(attempt_information.get("id"))
                if self.uses_game_time == True: time = attempt_information.find("GameTime").getText()
                elif self.uses_game_time == False: time = attempt_information.find("RealTime").getText()
                else: return ValueError
                if time.find(".") == -1: time += ".0000000"
                time = datetime.strptime(time[:-4], "%H:%M:%S.%f").time()
                if run_time.get(attempt_id) is None: run_time[attempt_id] = time
                else: run_time[attempt_id] = add_date_time_time(run_time[attempt_id], time)
                if not split_gold: split_gold = time; is_gold = True
                elif time < split_gold: split_gold = time; is_gold = True
                new_segment = Segment(time=time, is_supersplit = is_supersplit, was_gold = is_gold, run_time = run_time[attempt_id])
                self.runs[attempt_id].segments[split_name] = new_segment

    def print_splits_summary(self):
        print(f"Game: {self.game} - {self.category}\
                \nSubsplits: {self.uses_subsplits} - Game-Time: {self.uses_game_time}\
                \nRuns: {len(self.runs)}")
        for value in self.runs.values():
            print(f"Attempt:{value.attempt_id} - {len(value.segments)} Maps - in {value.time}")

    def print_specific_run(self,id):
        self.runs[id].print_segments()


class Attempt:
    def __init__(self, attempt_id = 0, start_date_time = None, end_date_time = None,\
            time = None, pause_time = None, run_completed = False):
        self.attempt_id = attempt_id
        self.start_date_time = start_date_time
        self.end_date_time = end_date_time
        self.pause_time = pause_time
        self.time = time
        self.run_completed = run_completed
        self.segments = {}

    def print_attempt_summary(self):
        print(f" ID: {self.attempt_id},\n Start Date: {self.start_date_time},\
                \n End Date: {self.end_date_time},\n Completed: {self.run_completed},\
                \n Run Time: {self.time},\n Pause Time: {self.pause_time} \n")

    def print_segments(self):
        for split_name, segment_info in self.segments.items():
            print(f"{split_name} \
                    \nCompleted in: {segment_info.time}\
                    \nrun_time: {segment_info.run_time}\
                    \nwas_gold?: {segment_info.was_gold}\
                    \nsuper split?: {segment_info.is_supersplit}\n")


class Segment:
    def __init__(self, was_gold = False, time = None,\
            run_time = None, is_supersplit = False):
        self.was_gold = was_gold
        self.time = time
        self.run_time = run_time
        self.is_supersplit = is_supersplit


def add_date_time_time(value_one, value_two):
    v_two = timedelta(hours=value_one.hour,minutes=value_one.minute,seconds=value_one.second,microseconds=value_one.microsecond)
    v_one = timedelta(hours=value_two.hour,minutes=value_two.minute,seconds=value_two.second,microseconds=value_two.microsecond)
    v_three = v_one + v_two
    hours, remainder = divmod(v_three.total_seconds(), 3600)
    minutes, seconds = divmod(remainder, 60)
    microseconds = v_three.microseconds
    new_date_time = time(int(hours), int(minutes), int(seconds), int(microseconds))
    return new_date_time
