
# import dataprofiler as dp
# import json

# my_text = dp.Data("test/.bash_history")
# profile = dp.Profiler(my_text)

# # print the report using json to prettify.
# report = profile.report(report_options={"output_format": "pretty"})
# print(json.dumps(report, indent=4))


import binascii, hashlib
input_str = "SOMETHING_AS_INPUT_TO_HASH"
ntlm_hash = binascii.hexlify(hashlib.new('md4', input_str.encode('utf-16le')).digest())
print(ntlm_hash)