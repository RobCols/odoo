import csv
import unidecode
import json
import re


PROVINCE_MAP = {
    'Antwerpen': 'l10n_be.state_be_van',
    'Brussel (19 gemeenten)': 'state_be_bru',
    'Henegouwen': 'l10n_be.state_be_wht',
    'Limburg': 'l10n_be.state_be_vli',
    'Luik': 'l10n_be.state_be_wlg',
    'Luxemburg': 'l10n_be.state_be_wlx',
    'Namen': 'l10n_be.state_be_wna',
    'Oost-Vlaanderen': 'l10n_be.state_be_vov',
    'Vlaams-Brabant': 'l10n_be.state_be_vbr',
    'Waals-Brabant': 'l10n_be.state_be_wbr',
    'West-Vlaanderen': 'l10n_be.state_be_vwv',
    '': ''
}


with open('zipcodes.csv', mode='r') as csv_file:
    csv_reader = csv.DictReader(csv_file)
    new_csv = []
    for row in csv_reader:
        idpattern = re.compile(re.compile('[\W_]+'))
        new_csv.append(
            {
                'id': row['Postcode'] + '_' + idpattern.sub('', unidecode.unidecode(row['Plaatsnaam']).title()),
                'zipcode': row['Postcode'],
                'name': row['Plaatsnaam'].title(),
                'country_id/id': "base.be",
                'state_id/id': PROVINCE_MAP[row['Provincie'].strip()]
            }
        )
    with open('res.city.csv', 'w') as new_file:
        writer = csv.DictWriter(new_file, fieldnames=new_csv[0].keys())
        writer.writeheader()
        for data in new_csv:
            writer.writerow(data)