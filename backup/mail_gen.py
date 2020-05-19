import csv, argparse, os.path, sys
from validate_email import validate_email

parser = argparse.ArgumentParser()
parser.add_argument('-f', type=str , default='' , nargs='+' , help='file scrapped to get the email from')
parser.add_argument('-o', type=str , default='' , nargs='+' , help='file to output')
parser.add_argument('-p', type=str , default='' , nargs='+' , help='adding prefixes i think are good')
args = parser.parse_args()

list_leads = args.f[0]
file_output = args.f[0] + "_email" + "csv"
if (args.o) : file_output = args.o[0] + "csv"

added_prefixes = args.p[0].split(",")

websites = []
if os.path.isfile(list_leads):
    with open(list_leads, newline='') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=',')
        for row in spamreader:
             websites.append(row[1])
else :
    print("no file found")
    sys.exit()


bad_prefix = ["dqmhqmsdfhmlskgmqgqmsoghqq"]
default_prefix = ["contact","direction", "info"]
prefixes =  bad_prefix + added_prefixes + default_prefix
print(prefixes)

for website in websites :
    domain = (website.strip())
    for prefix in prefixes :
        mail = prefix + "@" + domain
        is_valid = validate_email(mail, verify=True, check_mx=True )
        if is_valid :
            if mail == bad_prefix[0] + "@" + domain : mail = "info@" + domain
            else : print (mail)
            break
