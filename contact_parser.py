"""
Author: John Fishbein
Date: February 6, 2021

Contact Converter: Convert Spreadsheet with first name, last name, email, and phone number 
to a contact file that can be instantly turned into Apple contacts.

To use, run the following command
python3 contact_parser.py -i {csv}
where {csv} is replaced with the path to the csv file you wish to convert.  

This will create an apple vCard file with all contacts. Optionally, you may rename the output vCard file using the -o command line argument.
"""

import os
import re
import pandas as pd
from argparse import ArgumentParser, RawDescriptionHelpFormatter

email_re = '[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
phone_re = '^(?:\+?1[- ]?)?\(?([0-9]{3})\)?[- ]?([0-9]{3})[- ]?([0-9]{4})$'
vcard_format = """BEGIN:VCARD
VERSION:3.0
EMAIL:{email}
TEL;TYPE=cell,voice:{number}
FN:{fname} {lname}
END:VCARD
"""


def get_args(argv=None):
    """Return parsed command-line arguments."""
    shortdesc = __import__('__main__').__doc__.split("\n")[0]
    parser = ArgumentParser(formatter_class=RawDescriptionHelpFormatter,
                            description=shortdesc
                           )
    parser.add_argument('-i',
                        '--input',
                        type=str,
                        required=True,
                        help='Path to input CSV file containing contact data'
                       )
    parser.add_argument('-o',
                        '--output',
                        default='contact_file.vcf',
                        type=str,
                        help='Name of output file to store formatted contacts.  Must end in ".vcf"'
                       )
    args = parser.parse_args()
    return args


def verify_row(row):
    """Takes in a row from the table of contact info and returns true if email and phone are formatted properly"""
    valid = True
    if not re.search(phone_re, row['phone']):
        print(f"Bad Phone Number for {row['first name']} {row['last name']}")
        valid = False
    if not re.search(email_re, row['email']):
        print(f"Bad Email for {row['first name']} {row['last name']}")
        valid = False
    
    return valid




def main():
    args = get_args()
    
    # Verify that the provided input file is a valid csv
    if not os.path.isfile(args.input):
        raise ValueError(f"Input file {args.input} is not a valid file path")
    if args.input[-4:] != '.csv':
        raise ValueError(f"Must provide a CSV file as input")
    if args.output[-4:] != '.vcf':
        raise ValueError(f"Output file must end with '.vcf'")


    
    contact_info = pd.read_csv(args.input)
    contact_info.columns = map(str.lower, contact_info.columns)
    
    # Verify that the provided csv contains the necessary columns
    required_cols = ['First name', 'Last name', 'Email', 'Phone']
    if not all([col.lower() in contact_info.columns for col in required_cols]):
        raise ValueError(f"Input CSV file must include the following columns: {required_cols}")


    output = ''
    num_contacts_added = 0
    for i in range(len(contact_info)):
        row = contact_info.iloc[i]
        if not verify_row(row):
            print("Skipping {row['first name']} {row['last name']}")
        output += vcard_format.format(email=row['email'], 
                                      number=row['phone'], 
                                      fname=row['first name'], 
                                      lname=row['last name']
                                     )
        num_contacts_added += 1

    print(f"Successfully generated contact file for {num_contacts_added} people")

    if os.path.isfile(args.output):
        overwrite = input(f"Overwrite file {args.output}? (Y or N): ")
    else:
        overwrite = 'y'
    
    if overwrite.lower() == 'y':
        with open(args.output, 'w') as fp:
            print(output, file=fp)
        print(f"{num_contacts_added} contacts successfully published to file {args.output}")
    else:
        print("Results not written to file")




if __name__ == '__main__':
    main()
