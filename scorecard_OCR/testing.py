import re


foo = "Date:8/15/2020"
print(re.findall(r"(\d+\/\d+\/\d+)", foo))