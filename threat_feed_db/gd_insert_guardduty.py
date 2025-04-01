import json 
import os
import pdb
from typing import TypedDict

# As I am writing these classes I am realizing that since I am following a 
# strict naming convention -___- for the keys and the record types i should 
# have just written a script in python that takes one item of the json file and
# have it generate the classes -_____-

# But I guess typing these out is also soothing 

class PrivateIpAddressesRecord(TypedDict, total=True):
    
    private_dns_name: str
    private_ip_address: str


class SecurityGroupsRecord(TypedDict, total=True):

    group_id: str
    group_name: str


class NetworkInterfaceRecord(TypedDict, total=True):
   
    ipv6_addresses: list
    network_interface_id: str
    private_dns_name: str
    private_ip_address: str
    private_ip_addresses: list[PrivateIpAddressesRecord] 
    public_dns_name: str
    public_ip: str
    security_groups: list[SecurityGroupsRecord] 

class IamInstanceProfile(TypedDict, total=True):
    
    arn: str
    _id: str

class InstanceDetailsRecord(TypedDict, total=True):
   
    availability_zone: str
    iam_instance_profile: IamInstanceProfile
    image_description: str
    image_id: str
    instance_id: str
    instance_state: str
    instance_type: str
    outpost_arn: str
    network_interfaces: list[NetworkInterfaceRecord] 


class AccessKeyDetailsRecord(TypedDict, total=True):
 
    access_key_id: str
    principle_id: str
    user_name: str
    user_type: str


class TagsRecord(TypedDict, total=True):
    
    key: str
    value: str


class ProductRecord(TypedDict, total=True):
 
    code: str
    product_type: str


class ResourceRecord(TypedDict, total=True):
     
    access_key_details: AccessKeyDetailsRecord
    instance_details: InstanceDetailsRecord
    platform: str
    product_codes: list[ProductRecord]
    tags: list[TagsRecord] 
    resource_type: str


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
 

# This TypedDictionary represents one depth level into the JSON object, the next depth is
# represented through a different TypedDictionary which this class definition takes as a member
# variable. The TypedDictionaries are there to preserve the structure of the JSON Object obtained
# from the AWS Api as much as possible for further refinement and insertion into the database.

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
    _type: str


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

    def prepare_product_codes_json(self,product_item,product_record):

        match product_item[0]:

            case "Code":
                
                product_record["code"] = product_item[1]

            case "ProductType":

                product_record["product_type"] = product_item[1]

    def prepare_access_key_details_json(self,access_key_details_item,access_key_details_record):

        match access_key_details_item[0]:

            case "AccessKeyId":

                access_key_details_records["access_key_id"] = access_key_details_item[1]

            case "PrincipleId":

                access_key_details_records["principle_id"] = access_key_details_item[1]

            case "UserName":

                access_key_details_records["user_name"] = access_key_details_item[1]

            case "UserType":

                access_key_details_records["user_type"] = access_key_details_item[1]

    def prepare_tag_json(self,tag_item,tag_record):

        match tag_item[0]:

            case "Key":
                
                tag_record["key"] = tag_item[1]

            case "Value":

                tag_record["value"] = tag_item[1]

   


    
    def prepare_resource_json(self,resource_item,resource_record):

        # This method iterates of the resource_item tuple

        # For debugging purposes --
        # print(type(resource_item))
        # print(resource_item)

        match resource_item[0]:

            case "AccessKeyDetails":
                resource_record["access_key_details"] = resource_item[1]

            case "InstanceDetails":
                resource_record["instance_details"] = resource_item[1]

            case "Platform":
                resource_record["platform"] = resource_item[1]

            case "ProductCodes":
                resource_record["product_codes"] = resource_item[1]

            case "Tags":
                resource_record["tags"] = resource_item[1]

            case "ResourceType":
                resource_record["resource_type"] = resource_item[1]

 
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

                json_record["_type"] = record_item[1]

            case "Resource":

                resource_dict = dict(record_item[1])
                
                resource_record = ResourceRecord()

                dict(filter(lambda item: self.prepare_resource_json(item,resource_record),resource_dict.items()))
                json_record["resource"] = resource_record

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
