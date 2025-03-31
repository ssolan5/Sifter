import json 
import os
import pdb
from typing import TypedDict

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

class ResourceRecord(TypedDict, total=True):
    
    instance_id: str
    instance_type: str
    vpc_id: list
    public_ip: list
    network_interfaces: dict
    access_key_details: dict


class ServiceRecord(TypedDict, total=True):
     
    action: ActionRecord
    evidence: dict
    archived: bool
    resource_role: str
    service_name: str
    



class JSONParser():

    # now define a list of the typeddict here 
    # or in init

    
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
        

        # Each record_item would be a key value pair
        # We create a switch case to fill up one
        # JSONRecord item 
       
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

            case "Resource":

                resource_dict = dict(record_item[1])

                # print(str(resource_dict.keys()))
                # breakpoint()

                if self.check_key(resource_dict,"InstanceDetails"):
                    json_record["instance_id"]=resource_dict["InstanceDetails"]["InstanceId"]
                    json_record["instance_type"]=resource_dict["InstanceDetails"]["InstanceType"]

                    if self.check_key(resource_dict,"NetworkInterfaces"):
                        json_record["public_ip"]=resource_dict["InstanceDetails"]["NetworkInterfaces"][0]["PublicIp"]

            case "Title":

                json_record["title"] = record_item[1]

            case "Description":

                json_record["description"] = record_item[1]

            case "Type":

                json_record["record_type"] = record_item[1]

 
    def read_from_file(self):
        
        with open(self.file_path, "r") as file:
 
            self.json_dict = json.load(file)
            # print(json.dumps(guard_duty_json, indent= 4))

            # for loop for each record
            for record in self.json_dict:
 
                # print(json.dumps(record, indent= 4))
                # create a JSONRecord type here pertaining to one record
                # pass it to the prepare_json function and it iterates
                # over the dictionary, per each tuple and fills up the JSONRecord 
                
                json_record = JSONRecord()
                # print(json_record)
                
                dict(filter(lambda item: self.prepare_json(item,json_record),record.items()))
                self.json_record_list.append(json_record)

                # append the JSONRecord to the main list after

            for item in self.json_record_list:
                print(item)

'''

class ArgumentParser:

    # add argument options here
    # takes an argumentparser object
    
    def setup_arguments(parser):
        # set up the options here 
        # including the help

    def 


class SQL_DB:

    # we do the connection to the database
    # in this class, i would like to make it so
    # that the connection is available to all
    # instances of the sql_db class
    
    database_creds
    database_port
    database_host
    database_connection

    # wondering if it would be good to use a 
    # typeddict for defining each individual sql records 
    # object for insertion; the difficulty would be in 
    # unwrapping and placing it in the parameterized queries
    # so whatever is the easiest way to refer to each 
    # individual column in the record while writing the sql 
    # query which is then passed to the sql insert wrapper
    # provided by the postgres connector library

    def __init__():

    def insert_into_sql_db(self):


    def  write_to_sql_db(self):
    # the json records to this class


    def read_from_sql_db(self):

'''

def main():

    jsonparse = JSONParser("../GuarddutyAlertsSampleData/Guardduty Sample Alert Data.json")
    jsonparse.read_from_file()
    
    # handle the text based UI interface from here for querying 

   
if __name__ == "__main__":
    main()
