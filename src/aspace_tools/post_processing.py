#!/usr/bin/python3
#~/anaconda3/bin/python

'''Miscellaneous functions which can be used to process data that is retrieved from the ArchivesSpace API.'''

import itertools
import string
#import unidecode
import ast
#from fuzzywuzzy import fuzz
import pandas as pd
import traceback
from collections import Counter


def process_extents(csv_row, extent_calc):
    '''Processes the results of the get_extents() function'''
    return [csv_row['uri'], extent_calc['total_extent'], extent_calc['units']]

def process_child_nodes(row, children):
    '''Processes the results of the get_nodes() function'''
    child_list = children['precomputed_waypoints'][row['ao_node_uri']]['0']
    return [[child['uri'], child['title'], child['parent_id']]
                  for child in child_list]

def get_type(s):
    if type(s) is dict:
        if 'type' in s:
            s = s['type']
        else:
            print(s)
    return s

def get_restriction(s):
    if type(s) is dict:
        if 'rights_restriction' in s:
            s = s['rights_restriction']['local_access_restriction_type']
    return s

def remove_newlines(s):
    if s != '':
        s = s.replace('\n', '')
    return s

def process_json(s):
    if s != '':
        try:
            s = json.loads(s)
        #this is bad
        except Exception:
            print(traceback.format_exc())
            s = 'ERROR'
    return s

def get_content(s):
    if type(s) is dict:
        if (s['jsonmodel_type'] == 'note_multipart' and 'content' in s['subnotes'][0]):
            s = remove_newlines(s['subnotes'][0]['content'])
        elif s['jsonmodel_type'] == 'note_singlepart':
            s = remove_newlines(s['content'])
    return s

def extract_note_content(query_string, filepath, dbconn):
    '''this is a better way to extract text from notes than looping through them individually'''
    query_data = dbconn.run_query_df(query_string)
    query_data['note_json'] = query_data['note_json'].apply(process_json)
    query_data['type'] = query_data['note_json'].apply(get_type)
    query_data['note_json'] = query_data['note_json'].apply(get_content)
    query_data.to_csv(filepath, header=True, index=False)
    return query_data

#@atl.as_tools_logger(logger)
def merged_helper(df_1, df_2):
    merged = df_1.merge(df_2, indicator=True, how='outer')
    return merged[merged['_merge'] == 'right_only']

#@atl.as_tools_logger(logger)
def merged(csv_1, csv_2):
    #fp1 = input('Please enter path to CSV1: ')
    df1 = pd.read_csv(csv_1)
    #fp2 = input('Please enter path to CSV2: ')
    df2 = pd.read_csv(csv_2)
    merge_1 = merged_helper(df1, df2)
    merge_2 = merged_helper(df2, df1)
    return (merge_1['uri'].values.tolist(), merge_2['uri'].values.tolist())

# def compare_agents(csvlist):
#     matchlist = []
#     for a, b in itertools.combinations(csvlist, 2):
#         ratio = fuzz.ratio(a[0], b[0])
#         if ratio > 98:
#             matchlist.append([ratio] + a + b)
#     return matchlist

#@atl.as_tools_logger(logger)
def strip_punctuation(csvlist):
    for row in csvlist:
        #or whatever row...
        title = row[0]
        no_punc = title.translate(str.maketrans({key: None for key in string.punctuation}))
        no_punc = no_punc.translate(str.maketrans('', '', string.whitespace))
        no_punc = no_punc.lower()
        #no_punc = unidecode.unidecode(no_punc)
        row.append(no_punc)
    return csvlist

#where did this come from fp_data.append([i['resource']['ref'], i['uri'], instance['sub_container']['top_container']['ref']])
#@atl.as_tools_logger(logger)
def get_reorder_results(record_json, row):
    '''This would be run in a loop over a CSV file which contains a URI'''
    do_list = [[instance['digital_object']['ref'], i] for i, instance in enumerate(record_json['instances'])
                if instance['instance_type'] == 'digital_object']
    row.append(do_list)
    return row

#@atl.as_tools_logger(logger)
def check_instances(record_json):
    fp_data = []
    if record_json['instances']:
        for instance in record_json['instances']:
            if instance['instance_type'] != 'digital_object':
                fp_data.append([i['resource']['ref'], i['uri'], instance['sub_container']['top_container']['ref']])
    return fp_data

#@atl.as_tools_logger(logger)
def filter_contact_info_helper(json_bit):
    exclusions = ['create_time', 'created_by', 'last_modified_by', 'lock_version', 'system_mtime', 'user_mtime', 'uri']
    contact = []
    #fix this
    for item in json_bit:
        new_item = {}
        for key, value in item.items():
            if key not in exclusions:
                new_item[key] = value
            if key == 'telephones':
                if item['telephones'] != []:
                    new_phones = []
                    new_phone = {}
                    for phone in item['telephones']:
                        for k, v in phone.items():
                            if k not in exclusions:
                                new_phone[k] = v
                                #THIS IS A HACK - would add a bunch otherwise; maybe fix this later
                                if new_phone not in new_phones:
                                    new_phones.append(new_phone)
                    new_item['telephones'] = new_phones
        contact.append(new_item)
    return contact

#@atl.as_tools_logger(logger)
def filter_contact_info(csvfile, fileobject, csvoutfile):
    for row in csvfile:
            agent_type = row[0]
            agent_id = row[1]
            contact_info = row[2]
            contact_info = ast.literal_eval(contact_info)
            contact_info = filter_contact_info_helper(contact_info)
            row.insert(0, contact_info)
            csvoutfile.writerow(row)
    fileobject.close()

#@atl.as_tools_logger(logger)
def get_note_content():
    '''Also want to be able to get URIs (??? - what is the extract_uris script?),
    labels, note text, etc.; persistent IDs'''
    pass

#@atl.as_tools_logger(logger)
def join_csvs_on_match(csv_1, csv2, fileobject, csvoutfile):
    for row in csv_1:
        match_item = row[0]
        for r in csv_2:
            match_item_1 = r[0]
            if match_item == match_item_1:
                combined_row = row + r
                csvoutfile.writerow(combined_row)
    fileobject.close()

#@atl.as_tools_logger(logger)
def find_dupes_csv(csvfile, fileobject, csvoutfile):
    '''This actually might be a duplicate function. Check utilities'''
    seen = set()
    for row in csvfile:
        if n in seen:
            csvoutfile.writerow(n)
        else:
            seen.add(n)

def voyager_agent_matching_with_as(markslist, aslist, fileobject, csvoutfile):
    '''This needs to be edited but should get the idea'''
    markslist = [row for row in marksreport]
    as_list = [row for row in as_report]
    ziplist = list(zip(markslist, as_list))
    headers = ['bib', 'headings_dynamic_count_voyager', 'headings_original_count_voyager', 'headings_as_count', 'dynamic_as_diff', 'og_as_diff']
    csvoutfile.writerow(headers)
    for item in ziplist:
        bib = item[0][0]
        headings_dynamic_count = item[0][1]
        headings_original_count = item[0][2]
        headings_as_count = item[1][3]
        dynamic_as_diff = int(headings_dynamic_count) - int(headings_as_count)
        og_as_diff = int(headings_original_count) - int(headings_as_count)
        row = [bib, headings_dynamic_count, headings_original_count, headings_as_count, dynamic_as_diff, og_as_diff]
        csvoutfile.writerow(row)

def match_ao_uris_w_tc_uris(csv1, csv2, fileobject, csvoutfile):
    '''This doesn't work. First split out the box numbers into separate rows
    Don't think that I saved the thing I used to actually do this but should
    be headings_dynamic_count_voyager'''
    header_row = ['ao_uri', 'tc_uri', 'box_number']
    csvoutfile.writerow(header_row)
    data = []
    for i, row in enumerate(csv1):
        try:
            ao_uri = row[0]
            box_numbers = row[1]
            for r in csv2:
                tc_uri = r[0]
                box_num = r[1]
                if ',' in box_numbers:
                    box_numbers = box_numbers.split(',')
                    for box in box_numbers:
                        if box == box_num:
                            data.append([ao_uri, tc_uri, box_num])
                else:
                    if box_numbers == box_num:
                        data.append([ao_uri, tc_uri, box_num])
        except Exception as exc:
            print(row)
            print(traceback.format_exc())
    csvoutfile.writerows(data)
    fileobject.close()

    #         tc_uri = row[0]
    #         box_number = row[1]
    #         print(f'Box number: {box_number}')
    #         for r in csv2:
    #             ao_uri = r[0]
    #             box_numbers = r[1]
    #             if ',' in box_numbers:
    #                 box_numbers = box_numbers.split(',')
    #                 print(box_numbers)
    #                 for box in box_numbers:
    #                     print(f'Box: {box}')
    #                     if box == box_number:
    #                         data.append([ao_uri, tc_uri, box_number])
    #             else:
    #                 print(f'Single box: {box_numbers}')
    #                 if box_numbers == box_number:
    #                     data.append([ao_uri, tc_uri, box_number])
    #     except Exception as exc:
    #         print(row)
    #         print(traceback.format_exc())
    # csvoutfile.writerows(data)
    # fileobject.close()

def process_date_list():
    pass

def add_date_expressions(csvlist):
    for row in csvlist:
        pass

def main():
    pass
    # h1, c1 = u.opencsv('/Users/amd243/Downloads/glad_aos_still_need_dates_boxes.csv')
    # h2, c2 = u.opencsv('/Users/amd243/Desktop/glad_top_containers_created.csv')
    # fileobject, csvoutfile = u.opencsvout('/Users/amd243/Desktop/matched_top_containers.csv')
    # match_ao_uris_w_tc_uris(c1, c2, fileobject, csvoutfile)

if __name__ == "__main__":
    main()

    #
    #
    # for row in csv1:
    #     ao_uri = row[0]
    #     box_numbers = row[1]
    #     for row in csv2:
    #         tc_uri = row[0]
    #         box_number = row[1]
    #         if ',' in box_numbers:
    #             split_box_numbers = box_numbers.split(',')
    #             print(split_box_numbers)
    #             for box in split_box_numbers:
    #                 if box == box_number:
    #                     data.append([ao_uri, tc_uri, box_number])
    #         else:
    #             print(box_numbers)
    #             if box_numbers == box_number:
    #                 data.append([ao_uri, tc_uri, box_number])
    # csvoutfile.writerows(data)
    # fileobject.close()
