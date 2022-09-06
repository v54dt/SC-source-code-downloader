import requests
import json
import os
import configparser
import pandas
import re


def read_contract_address_file(file):
    df = pandas.read_csv(file)
    address_list = df[df.columns[0]].tolist()
    return address_list

def call_api(address):
    request_url = config['etherscan']['api_endpoint'] + '?module=contract&action=getsourcecode&address=' + address + '&apikey=' + \
                  config['etherscan']['api_key']
    res = requests.get(request_url)
    source_code_str = res.json()['result'][0]['SourceCode']
    source_code_name = res.json()['result'][0]['ContractName']
    if(isSingleFileContract(source_code_str)):
        string_to_file(source_code_str,source_code_name,address)
    else:
        prog = re.compile("^[{]{2}(.|\r\n)*[}]{2}$")
        if(prog.match(source_code_str)):
            source_code_object = json.loads(source_code_str[1:len(source_code_str) - 1])["sources"]
        else:
            source_code_object = json.loads(source_code_str)
        parse_object_and_write_file(source_code_object,address)

def parse_object_and_write_file(source_code_object, address):
    sources_dict = source_code_object
    # print(sources_dict)
    # print(sources_dict['contracts/pools/PoolToken.sol']['content'])
    for k in sources_dict:
        # print(k)
        # print(sources_dict[k]['content'])
        filename = "contract_" + address + "/" + k
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, "w") as f:
            f.write(sources_dict[k]['content'])

def string_to_file(source_code_str,source_code_name,address):
    filename = "contract_" + address +"/" + source_code_name+".sol";
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, "w") as f:
        f.write(source_code_str)

def isSingleFileContract(source_code_string):
    return(
        source_code_string.find("pragma")==0 or
        source_code_string.find("//")==0 or
        source_code_string.find("\r\n")==0 or
        source_code_string.find("/*")==0
    )


if __name__ == '__main__':
    config = configparser.ConfigParser()
    config = configparser.ConfigParser()

    config.read('config.ini')
    k =0
    address_list = read_contract_address_file('address.csv')
    for i in address_list:
        k = k+1
        r = call_api(i)

        if(k==100):
            break

