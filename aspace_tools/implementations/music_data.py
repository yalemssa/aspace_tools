#!/usr/bin/python3

from collections import OrderedDict
from aspace_tools import crud as c
from aspace_tools import json_data as jd
from aspace_tools import aspace_run
from aspace_tools import queries
from utilities import utilities as u
from utilities import dbssh
import traceback


#THIS PROBABLY DOESN'T WORK ANYMORE

def write_outfile(creator_data, csvoutfile):
    '''This function writes distinct creator data to an outfile for manual review'''
    print('Writing outfile')
    out_header = ['parent_uri', 'resource_uri', 'repo_uri', 'name']
    csvoutfile.writerow(out_header)
    for i, row in enumerate(creator_data, 1):
        csvoutfile.writerows(row)

def match_uris(composition_data, creator_data):
    '''This function matches up newly created subseries URIs with data about
    archival objects which represent compositions by the creators named in the
    subseries title. The URI is used as the 'parent' value when updating the
    parent of the composition archival objects.'''
    print('Matching URIs')
    new_data = []
    for rows in composition_data:
        for row in rows:
            if row:
                parent_uri = row[1]
                agent_name = row[5]
                for num, r in enumerate(creator_data):
                    p_uri = r[0]
                    a_name = r[3]
                    subseries_uri = r[4]
                    if (agent_name == a_name and parent_uri == p_uri):
                        new_row = list(row)
                        new_row.append(subseries_uri)
                        new_data.append(new_row)
    return new_data

def add_positions(music_data):
    '''This function takes the output of the get_music_data function after it is combined with the
    new subseries data, and adds a value for the archival object position.'''
    print('Adding archival object positions')
    from collections import defaultdict
    query_dict = defaultdict(list)
    for row in music_data:
        #this should always be the same??
        new_parent_uri = row[7]
        query_dict[new_parent_uri].append(row)
    query_dict = enumerate_values(query_dict)
    return query_dict

def enumerate_values(query_dict):
    for k, v in query_dict.items():
        for i, row in enumerate(v):
            row.append(i)
    return query_dict

def flatten_data(enumerated_data_dict):
    '''This function takes the dictionary output of the add_positions function and flattens it out.

       What I really need to do here is create a list of dictionaries
    '''
    print('Flattening data')
    flat_list = []
    for key, value in enumerated_data_dict.items():
        for item in value:
            #I do not understand why these objects are not being found?????? Where the fuck are the URIs coming
            #from if they don't exist in test?????
            ao_uri = item[0]
            #do not want this to be hardcoded...but since this is a specific implementation it is fine for now
            parent_uri = key.replace('/repositories/6/archival_objects/', '')
            position = item[8]
            flat_list.append({'child_uri': ao_uri, 'parent_uri': parent_uri, 'position': position})
    print('Number of archival objects to move: ' + str(len(flat_list)))
    return flat_list

def main():
    #1: Get a list of distinct creators for each collection, write output to file
    #cfg_fp = input('Please enter path to config file: ')
    list_of_parent_ids = input('Please enter path to list of parent IDs: ')
    try:
        header_row, parent_id_list = u.opencsv(list_of_parent_ids)
        #need to do this to re-use the list
        parent_id_list = [row for row in parent_id_list]
        #set the configuration file here??
        dbconn = dbssh.DBConn()
        print('Running queries')
        creator_data = aspace_run.run_db_queries(dbconn, parent_id_list, queries.get_distinct_creators)
        composition_data = aspace_run.run_db_queries(dbconn, parent_id_list, queries.get_music_data)
        outfile_path = input('Please enter path to outfile: ')
        fileobject, csvoutfile = u.opencsvout(outfile_path)
        write_outfile(creator_data, csvoutfile)
        fileobject.close()
        #2: Review manually and remediate any issues with agent records or duplicate agents
        to_continue = input('After reviewing file please enter CONTINUE to continue: ')
        if to_continue == 'CONTINUE':
            #3: Create subseries for each agent record, save new URI
            agent_data = u.opencsvdict(outfile_path)
            #do the config here - need to fix utilities again
            api_url, headers = u.login()
            print('Creating subseries')
            rows_w_uris = aspace_run.call_api(api_url, headers, agent_data, crud=c.create_data, json_data=jd.create_subseries)
            #but if I'm just going to put it in a list anyway?? I guess for other implementations it makes more sense?
            #Match new subseries URIs with all children
            combined_data = match_uris(composition_data, rows_w_uris)
            #5: Run data munging functions to get appropriate position
            enumerated_data = add_positions(combined_data)
            #NOW need to flatten this data as I did before...
            flattened_data = flatten_data(enumerated_data)
            #6: Use update ao position action to make change
            dirpath = u.setdirectory()
            aspace_run.call_api(api_url, headers, flattened_data, dirpath=dirpath, crud=c.update_parent)
    except Exception as exc:
        print('Error: ')
        print(traceback.format_exc())
    finally:
        dbconn.close_conn()


if __name__ == "__main__":
    main()
