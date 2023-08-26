
import dataprofiler as dp
import json

my_text = dp.Data("test/.bash_history")
profile = dp.Profiler(my_text)

# print the report using json to prettify.
report = profile.report(report_options={"output_format": "pretty"})
print(json.dumps(report, indent=4))