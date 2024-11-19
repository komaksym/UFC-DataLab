import pdb

def month_conversion(date):
    date = date.replace(" ", "")
    day, month, year = date.split("/")

    if int(day) < 10 and not day.startswith("0"):
        day = f"0{day}"
    if int(month) < 10 and not month.startswith("0"):
        month = f"0{month}"

    return f"{day}/{month}/{year}"

foo = "5/8/2020"
print(month_conversion(foo))