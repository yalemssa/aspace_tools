#/usr/bin/python3
#~/anaconda3/bin/python

import json
import pandas as pd
from utilities import dbssh

'''Clean this up so it can be abstracted from individual use cases'''

#filepath = '/Users/amd243/Desktop/hm_notes.csv'
filepath = '/Users/aliciadetelich/Desktop/odd_notes_refs_malformed_mssa.csv'

query_string = """select CONCAT('/repositories/', archival_object.repo_id, '/archival_objects/', archival_object.id) as uri
	, note.notes as note_json
from note
join archival_object on archival_object.id = note.archival_object_id
where note.notes like '%"type":"odd"%'
and note.notes like '%<ref%'
and note.notes like '%><%'
and archival_object.repo_id = 12
UNION
select CONCAT('/repositories/', resource.repo_id, '/resources/', resource.id) as uri
	, note.notes as note_json
from note
join resource on resource.id = note.resource_id
where (note.notes like '%"type":"odd"%' and note.notes like '%<ref%' and note.notes like '%><%')
and resource.repo_id = 12"""

# query_string = '''
# SELECT CONCAT('/repositories/', ao.repo_id, '/archival_objects/', ao.id) as ao_uri
# 	, CONCAT('/repositories/', resource.repo_id, '/resources/', resource.id) as resource_uri
# 	, replace(replace(replace(replace(replace(identifier, ',', ''), '"', ''), ']', ''), '[', ''), 'null', '') AS call_number
# 	, ifnull(npi.persistent_id, '') as persistent_id
# 	, ifnull(note.notes, '') as note_json
# 	, ifnull(e.external_id, '') as external_id
# 	, ifnull(e.source, '') as external_id_source
# 	, tc.indicator
# FROM archival_object ao
# LEFT JOIN note on note.archival_object_id = ao.id
# LEFT JOIN note_persistent_id npi on npi.note_id = note.id
# LEFT JOIN external_id e on e.archival_object_id = ao.id
# LEFT JOIN instance on instance.archival_object_id = ao.id
# LEFT JOIN sub_container sc on sc.instance_id = instance.id
# LEFT JOIN top_container_link_rlshp tclr on tclr.sub_container_id = sc.id
# LEFT JOIN top_container tc on tc.id = tclr.top_container_id
# LEFT JOIN resource on resource.id = ao.root_record_id
# WHERE ao.repo_id = 12
# #AND (note.notes like '%accessrestrict%' or note.notes is null)
# AND (tc.indicator like '%U%')
# #AND ( e.source like 'local_surrogate%' or e.source is null)
# AND resource.identifier not like '%HM%'
# ORDER BY call_number
# '''

# query_string = '''
# SELECT CONCAT('/repositories/12/resources/', note.resource_id) as uri
# 	, npi.persistent_id
# 	, note.notes as note_json
# FROM note
# JOIN note_persistent_id npi on npi.note_id = note.id
# JOIN resource on resource.id = note.resource_id
# AND note.notes like '%accessrestrict%'
# and resource.id in (4499,
# 2102,
# 2295,
# 2377,
# 2522,
# 2528,
# 2529,
# 2533,
# 2722,
# 2728,
# 2852,
# 3049,
# 3477,
# 3755,
# 3801,
# 3843,
# 4190,
# 4212,
# 4259,
# 4481,
# 4483,
# 4503,
# 4826,
# 4830,
# 4837,
# 4891,
# 4812,
# 4103,
# 2527,
# 2926,
# 3038,
# 3059,
# 3109,
# 3175,
# 3637,
# 3865,
# 3998,
# 4049,
# 4124,
# 4152,
# 4170,
# 4327,
# 4881,
# 3096,
# 3826,
# 4119,
# 4120,
# 4440,
# 4813,
# 4813,
# 4123,
# 4123,
# 4123,
# 3017,
# 4027,
# 4558)
# '''

# query_string = '''
# SELECT CONCAT('/repositories/12/archival_objects/', note.archival_object_id) as uri
# 	, npi.persistent_id
# 	, note.notes as note_json
# FROM note
# JOIN note_persistent_id npi on npi.note_id = note.id
# WHERE note.notes like '%accessrestrict%'
# and note.archival_object_id in (SELECT DISTINCT e.archival_object_id
# /* 	e.external_id
# 	, e.source
# 	, CONCAT('/repositories/12/archival_objects/', e.archival_object_id) as uri
# 	, e.create_time */
# from external_id e
# where e.source like '%local_surrogate_call_number%'
# AND e.external_id in
# ('HM 103',
# 'HM 216',
# 'HM 184',
# 'HM 180',
# 'HM 185',
# 'HM 193',
# 'HM 178',
# 'HM 179',
# 'HM 41',
# 'HM 191',
# 'HM 190',
# 'HM 88',
# 'HM 235',
# 'HM 253',
# 'HM 143',
# 'HM 118',
# 'HM 12',
# 'HM 31',
# 'HM 76',
# 'HM 258',
# 'HM 158',
# 'HM 211',
# 'HM 53',
# 'HM 39',
# 'HM 208',
# 'HM 98',
# 'HM 65',
# 'HM 65',
# 'HM 182',
# 'HM 3',
# 'HM 92',
# 'HM 14',
# 'HM 6',
# 'HM 104',
# 'HM 159',
# 'HM 123',
# 'HM 151',
# 'HM 74',
# 'HM 19',
# 'HM 174',
# 'HM 20',
# 'HM 83',
# 'HM 172',
# 'HM 154',
# 'HM 94',
# 'HM 132',
# 'HM 100',
# 'HM 45',
# 'HM 115',
# 'HM 175',
# 'HM 66',
# 'HM 78',
# 'HM 140',
# 'HM 201',
# 'HM 48',
# 'HM 145'))

# '''

# query_string = '''
# select CONCAT('/repositories/', ao.repo_id, '/archival_objects/', ao.id) as uri
# 	, ao.title as ao_title
# 	, resource.title as resource_title
# 	, replace(replace(replace(replace(replace(identifier, ',', ''), '"', ''), ']', ''), '[', ''), 'null', '') AS call_number
# 	, CONCAT('/repositories/', resource.repo_id, '/resources/', resource.id) as resource_uri
# 	, npi.persistent_id
# 	, note.notes as note_json
# from note
# join archival_object ao on ao.id = note.archival_object_id
# join note_persistent_id npi on npi.note_id = note.id
# join resource on resource.id = ao.root_record_id
# where ao.repo_id = 12
# #sometimes it seems like the likes are case sensitive and sometimes not
# and ((note.notes like '%reel %' or note.notes like '%Reel %') and (note.notes not like '%physdesc%') and (note.notes not like '%materialspec%'))
# '''

# query_string = '''
# select CONCAT('/repositories/', resource.repo_id, '/resources/', resource.id) as uri
# 	, npi.persistent_id
# 	, replace(replace(replace(replace(replace(identifier, ',', ''), '"', ''), ']', ''), '[', ''), 'null', '') AS call_number
# 	, resource.title
# 	, note.notes as note_json
# from resource
# join note on note.resource_id = resource.id
# join note_persistent_id npi on npi.note_id = note.id
# where resource.identifier like '%HM%'
# and note.notes not like '%note_singlepart%'
# and resource.repo_id = 12
# '''

# query_string = '''
# select CONCAT('/repositories/', resource.repo_id, '/resources/', resource.id) as uri
# 	, replace(replace(replace(replace(replace(resource.identifier, ',', ''), '"', ''), ']', ''), '[', ''), 'null', '') AS call_number
# 	, npi.persistent_id
# 	, note.notes as note_json
# from note
# join resource on note.resource_id = resource.id
# left join note_persistent_id npi on npi.note_id = note.id
# where note.notes like '%HM%'
# and note.notes not like '%UseSurrogate%'
# and note.notes not like '%note_singlepart%'
# and resource.suppressed != 1
# and resource.repo_id = 12
# UNION
# select CONCAT('/repositories/', ao.repo_id, '/archival_objects/', ao.id) as uri
# 	, replace(replace(replace(replace(replace(resource.identifier, ',', ''), '"', ''), ']', ''), '[', ''), 'null', '') AS call_number
# 	, npi.persistent_id
# 	, note.notes as note_json
# from note
# join archival_object ao on note.archival_object_id = ao.id
# left join note_persistent_id npi on npi.note_id = note.id
# join resource on ao.root_record_id = resource.id
# where note.notes like '%HM%'
# and note.notes not like '%UseSurrogate%'
# and note.notes not like '%note_singlepart%'
# and resource.suppressed != 1
# and resource.repo_id = 12
# '''

# query_string = '''SELECT CONCAT('/repositories/', resource.repo_id, '/resources/', resource.id) as uri
# 	, note_persistent_id.persistent_id
# 	, note.notes as note_json
# 	, resource.create_time
# FROM note
# JOIN resource on resource.id = note.resource_id
# LEFT JOIN note_persistent_id on note_persistent_id.note_id = note.id
# WHERE (note.notes like "%ualified%" and note.notes like "%restrict%")'''

# query_string = '''select CONCAT('/repositories/', resource.repo_id, '/resources/', resource.id) as uri
# 	, npi.persistent_id
# 	, note.notes as note_json
# from resource
# join note on note.resource_id = resource.id
# left join note_persistent_id npi on npi.note_id = note.id
# #left join rights_restriction rr on rr.resource_id = resource.id
# #eft join rights_restriction_type rrt on rrt.rights_restriction_id = rr.id
# #eft join enumeration_value ev on ev.id = rrt.restriction_type_id
# where note.notes like '%accessrestrict%'
# and resource.id in (2057,
# 2065,
# 2102,
# 2123,
# 2294,
# 2295,
# 2377,
# 2440,
# 2522,
# 2527,
# 2528,
# 2529,
# 2533,
# 2722,
# 2728,
# 2852,
# 2912,
# 2917,
# 2921,
# 2935,
# 2960,
# 2966,
# 2967,
# 3049,
# 3088,
# 3102,
# 3106,
# 3138,
# 3240,
# 3270,
# 3304,
# 3456,
# 3470,
# 3477,
# 3526,
# 3527,
# 3611,
# 3754,
# 3755,
# 3801,
# 3843,
# 3886,
# 3905,
# 3990,
# 4001,
# 4094,
# 4104,
# 4138,
# 4143,
# 4166,
# 4183,
# 4190,
# 4212,
# 4215,
# 4223,
# 4225,
# 4243,
# 4259,
# 4295,
# 4298,
# 4368,
# 4411,
# 4481,
# 4483,
# 4503,
# 4812,
# 4826,
# 4830,
# 4837,
# 4883,
# 4891)'''

def get_content(s):
	if type(s) is dict:
		if s['jsonmodel_type'] == 'note_multipart':
			if 'content' in s['subnotes'][0]:
				s = s['subnotes'][0]['content']
			else:
				s = s
		elif s['jsonmodel_type'] == 'note_singlepart':
			s = s['content']
		else:
			s = s
	return s

def get_type(s):
	if type(s) is dict:
		s = s['type']
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
		except Exception:
			s = 'ERROR'
	return s

'''this isn't totally working as expected


also I read to use apply only where necessary since its just a fancy loop...
'''
def extract_note_content(query_string, filepath, dbconn):
	'''this is a better way to extract text from notes than looping through them individually'''
	query_data = dbconn.run_query(query_string)
	#converts the note_json field to JSON
	query_data['note_json'] = query_data['note_json'].apply(process_json)
	#gets the type out of the json and creates a series
	#type_series = query_data['note_json'].apply(get_type).apply(pd.Series)
	#adds that new series as a new column
	#query_data = query_data.assign(type=type_series)
	#restriction_series = query_data['note_json'].apply(get_restriction).apply(pd.Series)
	#query_data = query_data.assign(type=restriction_series)
	#query_data['rights_restriction'] = query_data['note_json'].apply(get_restriction)
	query_data['type'] = query_data['note_json'].apply(get_type)
	#extracts the content from the JSON and removes the newlines
	query_data['note_json'] = query_data['note_json'].apply(get_content)
	'''this is a filter that returns only access restrictions. For some reason this is not
	working when I use it with the hm film query - but it did work with the previous qualified
	researcher query'''
	#is_access_restrict = query_data['type'] == 'accessrestrict'
	#print(is_access_restrict)
	#query_data = query_data[is_access_restrict]
	print(query_data)
	query_data.to_csv(filepath, header=True, index=False)


def main(query_string, filepath):
	dbconn = dbssh.DBConn()
	extract_note_content(query_string, filepath, dbconn)
	dbconn.close_conn()


if __name__ == "__main__":
	main(query_string, filepath)