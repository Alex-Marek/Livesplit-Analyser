from livesplit_analyser_2 import *
# from openpyxl import Workbook
# from openpyxl.utils import get_column_letter
import datetime
import xlsxwriter as xlsxwriter
from pandas.io.formats import excel
import numpy as np
import pandas as pd

SPLIT_TIME_LENGTH = 11
VERTICAL_OFFSET = 0
HORIZONTAL_OFFSET = 9
pd.io.formats.excel.ExcelFormatter.header_style = None

def main():
    splits_file = Splits_File()
    with open("6aa1.lss", 'r') as file:
        data = file.read()
    xml_data = BeautifulSoup(data,'xml')
    splits_file.load_whole_file(xml_data)
        

    splits = splits_file.splits
    attempts = splits_file.runs

    # Splits
    max_split_length = 0
    split_name_list = []
    if splits_file.uses_subsplits == True:
        for name in splits:
            if name[0] == "-":
                split_name_list.append(name[1:])
                if len(name[1:]) > max_split_length: max_split_length = len(name[1:]) 

            elif name.find('{') > -1 and name.find('}') > -1:
                new_name = name[name.find('}') + 2:]
                split_name_list.append(name[name.find('}') + 2:])
                if len(new_name) > max_split_length: max_split_length = len(new_name) 
    split_name_list.append("Final Time")
    

    #PB's at time of run
    # pbat = {"Personal Best at time" : []}
    # start_time = None
    # unconverted = None
    # for id, run in attempts.items():
    #     if run.run_completed: 
    #         if start_time == None:
    #             start_time = timedelta(run.time)
    #             unconverted = run.time
    #         elif start_time is not None and start_time < timedelta(run.time):
    #             start_time = timedelta(run.time)
    #             unconverted = run.time
    #     pbat["Personal Best at time"].append(start_time)
    #
    # pbat["Personal Best at time"].reverse()
    # df_pb_at_run = pd.DataFrame(pbat,dtype=str, columns=None)
    # df_pb_at_run = df_pb_at_run.transpose()
    # print(df_pb_at_run)
    #print(df_pb_at_run)


    # All runs Sheet
    all_attempt_ids = {"Attempt IDs" : []}
    all_runs = {}
    all_runs_count = 0
    for id, run in reversed(attempts.items()):
        segment_list = run.get_segment_times()

        for x in range(len(segment_list), len(splits)):
            if len(segment_list) < len(splits): segment_list.append("")

        segment_list.append(run.get_run_time())
        all_runs[all_runs_count] = segment_list
        all_runs_count += 1
        all_attempt_ids["Attempt IDs"].append(id)

    df_all_runs = pd.DataFrame(all_runs, index=split_name_list)
    df_all_attempt_ids = pd.DataFrame.from_dict(all_attempt_ids, orient='index') 
    df_all_runs = pd.concat([df_all_attempt_ids, df_all_runs])


    # Completed Runs Sheet
    comp_runs = {}
    comp_count = 0
    comp_attempt_ids = {"Attempt IDs" : []}
    for id, run in reversed(attempts.items()):
        if run.run_completed:
            segment_list = run.get_segment_times()
            for x in range(len(segment_list), len(splits)):
                if len(segment_list > len(splits)): segment_list.append("")

            segment_list.append(run.get_run_time())
            comp_runs[comp_count] = segment_list
            comp_count += 1
            comp_attempt_ids["Attempt IDs"].append(id)
            
        # comp_runs["Final Time"] = 
    df_comp_attempt_ids = pd.DataFrame.from_dict(comp_attempt_ids, orient='index')
    df_comp_runs = pd.DataFrame(comp_runs,index=split_name_list, columns=None)
    df_comp_runs = pd.concat([df_comp_attempt_ids, df_comp_runs])
    #print(df_comp_runs)


    # Most Recent Run
    most_recent_run = comp_attempt_ids["Attempt IDs"][0]
    run = splits_file.runs[most_recent_run]
    segment_times = run.get_segment_times()
    segment_times.append(run.get_run_time())
    df_mrr = pd.DataFrame(segment_times, index=split_name_list, columns=None)


    # PB Sheet
    pbs = {}
    cur_pb = None
    pb_count = 0
    pb_attempt_ids = {"Attempt IDs" : []}
    for id, run in attempts.items():
        run_is_pb = False
        if run.run_completed:
            if cur_pb is None: cur_pb = run.time; run_is_pb = True
            elif run.time < cur_pb: run_is_pb = True

        if run_is_pb:
            segment_list = run.get_segment_times()
            for x in range(len(segment_list), len(splits)):
                if len(segment_list > len(splits)): segment_list.append("NaN")

            segment_list.append(run.get_run_time())
            pbs[pb_count] = segment_list
            pb_count += 1
            pb_attempt_ids["Attempt IDs"].append(id)
    df_pb_attempt_ids = pd.DataFrame.from_dict(pb_attempt_ids, orient='index')
    df_pb = pd.DataFrame(pbs,index=split_name_list, columns=None)
    df_pb = pd.concat([df_pb_attempt_ids, df_pb])
    #print(df_pb)

    #Default Styling function
    def default_styling(val):
        styles = []
        for value in val:
            if val.name % 2 == 0: 
                styles.append('background-color: lightgray; text-align: center')
            else: styles.append('background-color: white; text-align: center')
        return styles


    # Writing to spreadsheet
    with pd.ExcelWriter('test.xlsx', engine='xlsxwriter', datetime_format='hh:mm:ss') as writer:
        wb = writer.book
        mrr = wb.add_worksheet("Most Recent Run")
        ar = wb.add_worksheet("All Runs")
        cr = wb.add_worksheet("Complete Runs")
        pb = wb.add_worksheet("Personal Bests")
        il = wb.add_worksheet("Individual Levels")
        mi = wb.add_worksheet("Miscellaneous")
        df = pd.DataFrame(
            {
                "Date and time": [
                    datetime.time(11, 30, 55),
                    datetime.time(1, 20, 33),
                    datetime.time(3, 11, 10),
                    datetime.time(16, 45, 35),
                    datetime.time(12, 10, 15),
                ],
            })
        format1 = wb.add_format({'num_format': 'HH:MM:SS.000'})
        ar.set_column(1,2, 50, format1)
        print(df)
        df.to_excel(writer, "All Runs")
        # Most Recent Runs
        df_mrr_styled = df_mrr.style.apply(default_styling)
        df_mrr_styled.to_excel(writer, engine="xlsxwriter",\
                        sheet_name="Most Recent Run", header=True,\
                        index=True, startrow=VERTICAL_OFFSET,\
                        startcol=HORIZONTAL_OFFSET)

        # for column_index in range(2, mrr.max_column +1):
        #     column_letter = get_column_letter(column_index)
        #     mrr.column_dimensions[column_letter].width = SPLIT_TIME_LENGTH
        # mrr.column_dimensions[get_column_letter(HORIZONTAL_OFFSET+1)].width = max_split_length+2

        # All Runs
        df_all_runs_styled = df_all_runs.style.apply(default_styling)
        df_all_runs_styled.to_excel(writer, engine="xlsxwriter", \
                                    sheet_name="All Runs", header=True, \
                                    index=True, startrow=VERTICAL_OFFSET, \
                                    startcol=HORIZONTAL_OFFSET)

        # cell = ar['K3']
        # cell.number_format = "HH:MM:SS.000"
        # for column_index in range(2, ar.max_column +1):
        #     column_letter = get_column_letter(column_index)
        #     ar.column_dimensions[column_letter].width = SPLIT_TIME_LENGTH
        # ar.column_dimensions[get_column_letter(HORIZONTAL_OFFSET+1)].width = max_split_length+2

        # Current Runs
        df_comp_runs_styled = df_comp_runs.style.apply(default_styling)
        df_comp_runs_styled.to_excel(writer, engine='xlsxwriter', \
                                     sheet_name="Complete Runs", header=True, \
                                     index=True, startrow=VERTICAL_OFFSET, \
                                     startcol=HORIZONTAL_OFFSET)

        # for column_index in range(2, cr.max_column +1):
        #     column_letter = get_column_letter(column_index)
        #     cr.column_dimensions[column_letter].width = SPLIT_TIME_LENGTH
        # cr.column_dimensions[get_column_letter(HORIZONTAL_OFFSET+1)].width = max_split_length+2

        # Personal Bests
        df_pb = df_pb.style.apply(default_styling)
        df_pb.to_excel(writer, engine='xlsxwriter', \
                                    sheet_name="Personal Bests", header=True, \
                                    index=True, startrow=VERTICAL_OFFSET, \
                                    startcol=HORIZONTAL_OFFSET)

        # for column_index in range(2, pb.max_column +1):
        #     column_letter = get_column_letter(column_index)
        #     pb.column_dimensions[column_letter].width = SPLIT_TIME_LENGTH
        # pb.column_dimensions[get_column_letter(HORIZONTAL_OFFSET+1)].width = max_split_length+2

if __name__ == "__main__":
    main()


#*Spreadsheet
#-All Runs sheet (AR)
#-Completed Runs sheet (CR)
#-Split/subsplit/map sheet (ILs)
#-PB Sheet (PB)
#-Reset sheet (RS)
#-Misc (MI)
