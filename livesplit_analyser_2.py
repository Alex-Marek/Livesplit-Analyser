from bs4 import BeautifulSoup
from collections import defaultdict
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
        self.print_splits_summary()


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
            if time:time = datetime.strptime(time.getText()[:-4], "%H:%M:%S.%f").time()
            if pause_time: pause_time = datetime.strptime(pause_time.getText()[:-4], "%H:%M:%S.%f").time()
            new_attempt = Attempt(attempt_id, start_date, end_date, time, pause_time, run_completed)

            self.runs[attempt_id] = new_attempt
           
    def load_segment_history(self, xml_data):
        result = xml_data.find_all("Segment")
        for split in result:
            split_name = split.find("Name").getText()
            segment_history = split.find_all("Time")
            for attempt_information in segment_history:
                time = None
                attempt_id = None
                attempt_id = int(attempt_information.get("id"))
                if self.uses_game_time == True:
                    time = attempt_information.find("GameTime").getText()
                elif self.uses_game_time == False:
                    time = attempt_information.find("RealTime").getText()
                else: return ValueError
                #Livesplit removes ms if exactly 0 which is CRINGE
                if time.find(".") == -1: time += ".0000000"
                time = datetime.strptime(time[:-4], "%H:%M:%S.%f").time()
                self.runs[attempt_id].segments[split_name] = time


    def print_splits_summary(self):
        print(f"Game: {self.game} - {self.category}\
                \nSubsplits: {self.uses_subsplits} - Game-Time: {self.uses_game_time}\
                \nRuns: {len(self.runs)}")
        for value in self.runs.values():
            print(f"Attempt:{value.attempt_id} - {len(value.segments)} Maps - in {value.time}")


    def print_specific_run(self,id):
        self.runs[id].print_segments()


class Attempt:
    def __init__(self, attempt_id = 0, start_date_time = None, end_date_time = None, time = None, pause_time = None, run_completed = False):
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
        for split_name, time in self.segments.items():
            print(f"{split_name} Completed in: {time}")


def main():
    s_file = Splits_File()
    with open("6aa1.lss", 'r') as file:
        raw_data = file.read()
    xml_data = BeautifulSoup(raw_data,'xml')
    s_file.load_whole_file(xml_data)
    s_file.print_splits_summary()



if __name__ == "__main__":
    main()
