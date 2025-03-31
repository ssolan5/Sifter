import json 
import os
import pdb
from typing import TypedDict

class ResourceRecord(TypedDict, total=True):
 
    instance_id: str
    instance_type: str
    vpc_id: list
    public_ip: list
    network_interfaces: dict
    access_key_details: dict


class AwsApiCallActionRecord(TypedDict, total=True):

    api_name: str
    caller_type: str
    error_code: str
    remote_ip_details: dict
    service_name: str
    affected_resources: dict


class ActionRecord(TypedDict, total=True):

    action_type: str
    aws_api_call_action: AwsApiCallActionRecord

 
class ServiceRecord(TypedDict, total=True):
 
    action: ActionRecord
    evidence: dict
    archived: bool
    resource_role: str
    service_name: str
 

class JSONRecord(TypedDict, total=True):
 
    account_id: str
    region: str
    created_at: str
    updated_at: str
    severity: int
    title: str 
    description: str # varchar(300) ??
    record_type: str
    resource: ResourceRecord
    service: ServiceRecord
    additional_data: dict


class JSONParser():

    # This class handles parsing the JSON file into TypedDictionaries that 
    # are then inserted into the PostGreSQL database after validating. 


    def __init__ (self,file_path):

        self.file_path = file_path
        self.json_dict = dict() 
        self.json_record_list = list()


    def check_key(self,json_d,key):
        if key in json_d:
            return True
        else:
            return False

 
    def prepare_json(self,record_item,json_record):

        # This method iterates over the dictionary, per each tuple 
        # and populates individual JSONRecord for the relevant JSON object  
 

        # For debugging purposes --
        # print(type(record_item))
        # print(str(record_item))
 
        match record_item[0]:

            case "AccountId":

                json_record["account_id"] = record_item[1] 

            case "Region": 

                json_record["region"] = record_item[1]

            case "CreatedAt":

                json_record["created_at"] = record_item[1]

            case "UpdatedAt":

                json_record["updated_at"] = record_item[1]

            case "Severity":

                json_record["severity"] = record_item[1]

            case "Title":

                json_record["title"] = record_item[1]

            case "Description":

                json_record["description"] = record_item[1]

            case "Type":

                json_record["record_type"] = record_item[1]

            case "Resource":

                resource_dict = dict(record_item[1])

                # TODO: Shift functionality for parsing the Resource 
                # elsewhere, this is stand-in code for it currently.

                # For debugging purposes --
                # breakpoint()

                if self.check_key(resource_dict,"InstanceDetails"):
                    json_record["instance_id"]=resource_dict["InstanceDetails"]["InstanceId"]
                    json_record["instance_type"]=resource_dict["InstanceDetails"]["InstanceType"]

                    if self.check_key(resource_dict,"NetworkInterfaces"):
                        json_record["public_ip"]=resource_dict["InstanceDetails"]["NetworkInterfaces"][0]["PublicIp"]

 
    def read_from_file(self):
 
        with open(self.file_path, "r") as file:
 
            self.json_dict = json.load(file)

            # For debugging purposes -- 
            # print(json.dumps(guard_duty_json, indent= 4))

            for record in self.json_dict:
 
                # For debugging purposes --
                # print(json.dumps(record, indent= 4))

                json_record = JSONRecord()
                # print(json_record)
 
                # Create a JSONRecord type here pertaining to one JSON
                # object and pass it to the prepare_json method. 
                # Each item here is a key value pair (<class 'tuple'>) for
                # one individual JSON object in the JSON file provided.

                dict(filter(lambda item: self.prepare_json(item,json_record),record.items()))
                
                # Appending the JSONRecord to the main list after populating
                self.json_record_list.append(json_record)



            for item in self.json_record_list:
                print(item)

'''

class ArgumentParser:

    # TODO: Adding some argument options here
    # takes an argumentparser object, but
    # have not decided upon options provided.
    
    def setup_arguments(parser):

        # TODO: Set up of command line options here 
        # including the help description



class SQL_DB:

    # TODO: This class handles connection to the PostGreSQL
    # database. Database connection is made available to all
    # instances of the SQL_DB class; need to consider setup
    
    # database_creds
    # database_port
    # database_host
    # database_connection

    def __init__():

    def insert_into_sql_db(self):


    def  write_to_sql_db(self):
    
    # TODO: The TypedDict records are to be passed to 
    # this method and it handles writing to the database.


    def read_from_sql_db(self):

'''

def main():

    jsonparse = JSONParser("../GuarddutyAlertsSampleData/Guardduty Sample Alert Data.json")
    jsonparse.read_from_file()
    
    # TODO: Handle the text based UI interface here for SQL querying and printing results. 

 
if __name__ == "__main__":
    main()
