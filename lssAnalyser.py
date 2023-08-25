from bs4 import BeautifulSoup
from bs4 import Tag
from datetime import datetime
from datetime import time
from datetime import timedelta
from collections import defaultdict

class Splits_File:
    completed_runs = [int]
    segment_info = {}           #string:bool
    subsplits = False
    runs = {}

    def find_splits(self, segments):
        split_segment_info = {}
        if type(segments) == Tag:
            segNames = segments.find_all("Name")
            for value in segNames:
                value = value.getText()
                if value.find("{") > -1 and value.find("}") > -1:
                    self.subsplits = True
                    split_segment_info[value] = True
                else:
                    split_segment_info[value] = False
        self.segment_info = split_segment_info

    def read_attempt_history(self, attempts):
        personal_best = ""
        for attempt_value in attempts:
            if type(attempt_value) == Tag:
                game_time = pause_time = None
                start_date = attempt_value.get("started")
                end_date = attempt_value.get("ended")
                is_comp = False
                id = attempt_value.get("id")
                if type(id) is str: id = int(id)
                if type(start_date) is str: start_date = datetime.strptime(start_date, "%m/%d/%Y %H:%M:%S")
                if type(end_date) is str: end_date = datetime.strptime(end_date, "%m/%d/%Y %H:%M:%S")
                if len(attempt_value) != 0:
                    is_comp = True
                    game_time = attempt_value.find("GameTime")
                    pause_time = attempt_value.find("PauseTime")
                    if pause_time: pause_time = datetime.strptime(pause_time.getText()[:-4], "%H:%M:%S.%f").time()
                    if game_time:
                        game_time = datetime.strptime(game_time.getText()[:-4], "%H:%M:%S.%f").time()
                        if personal_best == "" or game_time < personal_best:
                            personal_best = game_time
                new_run = run(id,start_date, end_date,personal_best,game_time, pause_time, is_comp)
                new_run.load_segment_info(self.segment_info)
                self.runs[id] = new_run

    def read_segment_history(self, segment_data):
        for segment_single in segment_data:
            name = segment_single.find("Name").getText()
            segment_history = segment_single.find_all("Time")
            for attempt_times in segment_history:
                new_segment = segment()
                game_time_gold = ""
                id = attempt_times.get("id")
                if type(id) is str: id = int(id)
                game_time = attempt_times.find("GameTime").getText()
                
                #Livesplit removes the ms if it's exactly 0 CRINGE
                if game_time.find(".") == -1: game_time += ".0000000"
                game_time = datetime.strptime(game_time[:-4], "%H:%M:%S.%f").time()
                
                if game_time_gold == "":
                    game_time_gold = game_time

                if game_time_gold == game_time:
                    new_segment.create_segment(name, game_time, True)
                else:
                    new_segment.create_segment(name, game_time, False)
                self.runs[id].segments[name] = new_segment

                

class run:
    segments = {}
    super_segments = {}
    goldCount = 0
    finalMap = None
    length = 0
    def __init__(self,id, s_date, e_date, p_bat, g_t, p_t, is_comp):
        self.attempt_id = id
        self.start_date = s_date
        self.end_date = e_date
        self.person_best_at_time = p_bat
        self.game_time = g_t
        self.pause_time = p_t
        self.is_completed = is_comp

    def load_segment_info(self, segment_info):    
        new_segments = defaultdict(segment)
        new_super_segments = defaultdict(segment)
        for value, super_split in segment_info.items():
            if super_split == True:
                new_super_segments[value]
            new_segments[value]
        self.segments = new_segments
        self.super_segments = new_super_segments

    def calc_super_segments(self):
        time_count = ""
        for value in self.segments.values():
            map_name = value.name
            game_time = value.game_time
            if game_time is not None:
                if time_count == "":
                    time_count = value.game_time
                else:
                    if time_count != None:
                        time_count = add_date_time_time(game_time, time_count)

            if map_name in self.super_segments:
                new_segment = segment()
                new_segment.create_segment(map_name,time_count,False)
                self.super_segments[map_name] = new_segment
                time_count = ""
            
        

    def print_super_segments(self):
        for value in self.super_segments.values():
            print(f"{value.name} in {value.game_time}")

    def print_run_info(self):
        print(f"ID:{self.attempt_id}, \nStartDate:{self.start_date}, \nEndDate:{self.end_date},")
        print(f"PB:{self.person_best_at_time}, \nGameTime:{self.game_time}")
        print(f"Run Length: {len(self.segments)},\nCompleted:{self.is_completed}.\n")

    def print_segments(self):
        for values in self.segments.values():
            print(f"{values.name} in: {values.game_time}")
        print(f"Ending Time: {self.game_time}")

class segment:
    name = ""
    game_time = None
    was_gold = False

    def create_segment(self, split_name, g_time, w_gold):
       self.name = split_name
       self.game_time = g_time
       self.was_gold = w_gold


def add_date_time_time(value_one, value_two):
    v_two = timedelta(hours=value_one.hour,minutes=value_one.minute,seconds=value_one.second,microseconds=value_one.microsecond)
    v_one = timedelta(hours=value_two.hour,minutes=value_two.minute,seconds=value_two.second,microseconds=value_two.microsecond)
    v_three = v_one + v_two
    hours, remainder = divmod(v_three.total_seconds(), 3600)
    minutes, seconds = divmod(remainder, 60)
    microseconds = v_three.microseconds
    new_date_time = time(int(hours), int(minutes), int(seconds), int(microseconds))
    return new_date_time




def main():
    splits_file = Splits_File()
    with open("6aa1.lss", 'r') as f:
        data = f.read()
    bs_Data = BeautifulSoup(data,'xml')
    # Find all Split names and whether they're supersplits
    splits_file.find_splits(bs_Data.find("Segments"))
    # Read through attempt history to get a glossary of all runs in the splits
    splits_file.read_attempt_history(bs_Data.find_all("AttemptHistory")[0])
    # Now to read through the split history into the runs
    splits_file.read_segment_history(bs_Data.find_all("Segment"))
    #print(type(splits_file.runs[41].segments))
    #splits_file.runs[41].print_segments()
    splits_file.runs[41].calc_super_segments()
    splits_file.runs[41].print_super_segments()
    #for run in splits_file.runs.values():
        #run.print_run_info()







if __name__ == "__main__":
    main()
