SELECT note.resource_id
	, resource.ead_id
	, npi.persistent_id
	, replace(replace(CAST(note.notes as CHAR (500000) CHARACTER SET UTF8), '"', ''), '{', '') as note_text
FROM note
JOIN resource on note.resource_id = resource.id
JOIN note_persistent_id npi on npi.note_id = note.id
WHERE note.resource_id in ('4100', '4027', '3015', '2912', '3017', '2917', '4104', '4435', '4143', '4436', '4170', '4817', '4564', '3827', '4120', '4122', '4123', '4819', '3611', '3095', '3841', '4548', '4823', '4471', '4492', '4295', '4298', '4552', '4372', '4481', '4482', '3218', '4468', '3631', '4502', '3893', '3687', '4507', '3713', '3451', '3910', '3721', '4513', '4527', '4846', '4897', '3743', '3744', '3752', '4520', '4016', '3538', '3541', '3542', '3759', '4528', '3761', '4851', '4852', '4529', '4098', '3772', '5184', '3777', '4021', '3780', '5249', '4900', '4887', '5177', '4904', '4951')
AND note.notes like '%accessrestrict%'
ORDER BY note.resource_id