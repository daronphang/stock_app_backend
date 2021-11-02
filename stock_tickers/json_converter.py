import json
import os

basedir = os.path.abspath(os.path.dirname(__file__))
os.chdir(basedir)

final_dict = {}

with open('nasdaq_tickers.txt', 'r') as file:
    exchange_list = []
    for line in file:
        string_list = line.split('|')
        dict = {
            "ticker": string_list[0].strip(),
            "name": string_list[1].split('-')[0].strip()
        }
        exchange_list.append(dict)

    final_dict['US'] = exchange_list


with open('sgx_tickers.txt', 'r') as file:
    exchange_list = []
    for line in file:
        string_list = line.split('	')
        dict = {
            "ticker": string_list[1].strip(),
            "name": string_list[0].strip()
        }
        exchange_list.append(dict)
    final_dict['SG'] = exchange_list

json_file = open('stock_tickers.json', 'w')
json.dump(final_dict, json_file, indent=2, sort_keys=False)
