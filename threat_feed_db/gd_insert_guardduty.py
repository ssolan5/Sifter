import json 
import os
import pdb
from typing import TypedDict

# As I am writing these classes I am realizing that since I am following a 
# strict naming convention -___- for the keys and the record types i should 
# have just written a script in python that takes one item of the json file and
# have it generate the classes -_____-

# But I guess typing these out is also soothing 

class PrivateIpAddressRecord(TypedDict, total=True):
    
    private_dns_name: str
    private_ip_address: str


class SecurityGroupRecord(TypedDict, total=True):

    group_id: str
    group_name: str


class NetworkInterfaceRecord(TypedDict, total=True):
   
    ipv6_addresses: list
    network_interface_id: str
    private_dns_name: str
    private_ip_address: str
    private_ip_addresses: list[PrivateIpAddressRecord] 
    public_dns_name: str
    public_ip: str
    security_groups: list[SecurityGroupRecord] 
    subnet_id: str
    vpc_id: str


class IamInstanceProfileRecord(TypedDict, total=True):
    
    arn: str
    _id: str


class TagRecord(TypedDict, total=True):
    
    key: str
    value: str


class ProductRecord(TypedDict, total=True):
 
    code: str
    product_type: str


class InstanceDetailsRecord(TypedDict, total=True):
   
    availability_zone: str
    iam_instance_profile: IamInstanceProfileRecord
    image_description: str
    image_id: str
    instance_id: str
    instance_state: str
    instance_type: str
    outpost_arn: str
    network_interfaces: list[NetworkInterfaceRecord]
    platform: str
    product_codes: list[ProductRecord]
    tags: list[TagRecord] 
       

class AccessKeyDetailsRecord(TypedDict, total=True):
 
    access_key_id: str
    principle_id: str
    user_name: str
    user_type: str


class ResourceRecord(TypedDict, total=True):
     
    access_key_details: AccessKeyDetailsRecord
    instance_details: InstanceDetailsRecord
    resource_type: str


class RemoteIpDetailsRecord(TypedDict, total=True):

    city: dict
    country: dict
    geo_location: dict
    ip_address_v4: str
    ip_address_v6: str
    organization: dict


class AwsApiCallActionRecord(TypedDict, total=True):

    api_name: str
    caller_type: str
    error_code: str
    remote_ip_details: RemoteIpDetailsRecord
    service_name: str
    affected_resources: dict


class ActionRecord(TypedDict, total=True):

    action_type: str
    aws_api_call_action: AwsApiCallActionRecord


class AdditionalInfoRecord(TypedDict, total=True):

    value: dict
    _type: str


class ServiceRecord(TypedDict, total=True):
 
    action: ActionRecord
    evidence: dict
    archived: bool
    count: str
    detector_id: str
    event_first_seen: str
    event_last_seen: str
    resource_role: str
    service_name: str
    additional_info: AdditionalInfoRecord


# This TypedDictionary represents one depth level into the JSON object, the next depth is
# represented through a different TypedDictionary which this class definition takes as a member
# variable. The TypedDictionaries are there to preserve the structure of the JSON Object obtained
# from the AWS Api as much as possible for further refinement and insertion into the database.

class JSONRecord(TypedDict, total=True):
 
    account_id: str 
    arn: str
    created_at: str
    description: str # varchar(300) ??
    _id: str
    region: str
    resource: ResourceRecord
    schema_version: str
    service: ServiceRecord
    severity: int
    title: str 
    _type: str
    updated_at: str


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


    def prepare_action_json(self, action_item, action_record):

        match action_item[0]:

            case "ActionType":

                action_record["action_type"] = action_item[1]

            case "AwsApiCallAction":

                aws_api_call_action_record = AwsApiCallActionRecord()

                dict(filter(lambda item: self.prepare_aws_api_call_action_json(item, aws_api_call_action_record),action_item[1].items()))

                action_record["aws_api_call_action"] = aws_api_call_action_record

    
    def prepare_remote_ip_details_json(self, remote_ip_details_item, remote_ip_details_record):

        match remote_ip_details_item[0]:

            case "City":

                remote_ip_details_record["city"] = remote_ip_details_item[1]

            case "Country":
                
                remote_ip_details_record["country"] = remote_ip_details_item[1]

            case "GeoLocation":
                
                remote_ip_details_record["geo_location"] = remote_ip_details_item[1]

            case "IpAddressV4":

                remote_ip_details_record["ip_address_v4"] = remote_ip_details_item[1]

            case "IpAddressV6":

                remote_ip_details_record["ip_address_v6"] = remote_ip_details_item[1]

            case "Organization":

                remote_ip_details_record["organization"] = remote_ip_details_item[1]


    def prepare_aws_api_call_action_json(self, aws_api_call_action_item, aws_api_call_action_record):

        match aws_api_call_action_item[0]:

            case "Api":
                
                aws_api_call_action_record["api"] = aws_api_call_action_item[1]

            case "CallerType":

                aws_api_call_action_record["caller_type"] = aws_api_call_action_item[1]

            case "ErrorCode":

                aws_api_call_action_record["error_code"] = aws_api_call_action_item[1]

            case "RemoteIpDetails":

                remote_ip_details_record = RemoteIpDetailsRecord()

                dict(filter(lambda item: self.prepare_remote_ip_details_json(item,remote_ip_details_record),aws_api_call_action_item[1].items()))

                aws_api_call_action_record["remote_ip_details"] = remote_ip_details_record


            case "ServiceName":

                aws_api_call_action_record["service_name"] = aws_api_call_action_item[1]

            case "AffectedResources":

                aws_api_call_action_record["affected_resources"] = aws_api_call_action_item[1]


    def prepare_product_codes_json(self,product_item,product_record):

        match product_item[0]:

            case "Code":
                
                product_record["code"] = product_item[1]

            case "ProductType":

                product_record["product_type"] = product_item[1]


    def prepare_additional_info_json(self, additional_info_item, additional_info_record):

        match additional_info_item[0]:

            case "Value":

                additional_info_record["value"] = additional_info_item[1]

            case "Type":

                additional_info_record["_type"] = additional_info_item[1]


    def prepare_service_json(self, service_item, service_record):

        match service_item[0]:

            case "Action":

                action_record = ActionRecord()

                dict(filter(lambda item: self.prepare_action_json(item,action_record),service_item[1].items()))

                service_record["action"] = action_record

            case "Evidence":

                service_record["evidence"] = service_item[1]

            case "Archived":

                service_record["archived"] = service_item[1]

            case "Count":

                service_record["count"] = service_item[1]

            case "DetectorId":

                service_record["detector_id"] = service_item[1]

            case "EventFirstSeen":

                service_record["event_first_seen"] = service_item[1]

            case "EventLastSeen":

                service_record["event_last_seen"] = service_item[1]

            case "ResourceRole":

                service_record["resource_role"] = service_item[1]

            case "ServiceName":

                service_record["service_name"] = service_item[1]

            case "AdditionalInfo":

                additional_info_record = AdditionalInfoRecord()

                dict(filter(lambda item: self.prepare_additional_info_json(item,additional_info_record),service_item[1].items()))

                service_record["additional_info"] = service_item[1]


    def prepare_private_ip_addresses_json(self, private_ip_address_item, private_ip_address_record):
        
        match private_ip_address_item[0]:

            case "PrivateDnsName":
                
                private_ip_address_record["private_dns_name"] = private_ip_address_item[1]
            
            case "PrivateIpAddress":

                private_ip_address_record["private_ip_address"] = private_ip_address_item[1]


    def prepare_security_groups_json(self, security_group_item, security_group_record):

        match security_group_item[0]:

            case "GroupId":
                
                security_group_record["group_id"] = security_group_item[1]

            case "GroupName":
                
                security_group_record["group_name"] = security_group_item[1]


    def prepare_network_interface_json(self, network_interface_item, network_interface_record):

        match network_interface_item[0]:

            case "Ipv6Addresses":

                network_interface_record["ipv6_address"] = network_interface_item[1]

            case "NetworkInterfaceId":

                network_interface_record["network_interface_id"] = network_interface_item[1]

            case "PrivateDnsName":

                network_interface_record["private_dns_name"] = network_interface_item[1]

            case "PrivateIpAddress":

                network_interface_record["private_ip_address"] = network_interface_item[1]

            case "PrivateIpAddresses":

                private_ip_addresses_list = list()

                for private_ip_addresses_item in network_interface_item[1]:

                    private_ip_address_record = PrivateIpAddressRecord()
                    
                    list(filter(lambda item: self.prepare_private_ip_addresses_json(item,private_ip_address_record),private_ip_addresses_item.items()))

                    private_ip_addresses_list.append(private_ip_address_record);

                network_interface_record["private_ip_addresses"] = private_ip_addresses_list

            case "PublicDnsName":

                network_interface_record["public_dns_name"] = network_interface_item[1]

            case "PublicIp":

                network_interface_record["public_ip"] = network_interface_item[1]

            case "SecurityGroups":

                security_groups_list = list()

                for security_group_item in network_interface_item[1]:

                    security_group_record = SecurityGroupRecord()
                    
                    list(filter(lambda item: self.prepare_security_groups_json(item,security_group_record),security_group_item.items()))
                    
                    security_groups_list.append(security_group_record)

                network_interface_record["security_groups"] = security_groups_list

            case "SubnetId":

                network_interface_record["subnet_id"] = network_interface_item[1]

            case "VpcId":

                network_interface_record["vpc_id"] = network_interface_item[1]



    def prepare_access_key_details_json(self,access_key_details_item,access_key_details_record):

        match access_key_details_item[0]:

            case "AccessKeyId":

                access_key_details_record["access_key_id"] = access_key_details_item[1]

            case "PrincipleId":

                access_key_details_record["principle_id"] = access_key_details_item[1]

            case "UserName":

                access_key_details_record["user_name"] = access_key_details_item[1]

            case "UserType":

                access_key_details_record["user_type"] = access_key_details_item[1]


    def prepare_tag_json(self,tag_item,tag_record):

        match tag_item[0]:

            case "Key":
                
                tag_record["key"] = tag_item[1]

            case "Value":

                tag_record["value"] = tag_item[1]


    def prepare_iam_instance_profile_json(self,iam_instance_profile_item,iam_instance_profile_record):

        match iam_instance_profile_item[0]:

            case "Arn":
                
                iam_instance_profile_record["arn"] = iam_instance_profile_item[1]
            
            case "Id":
                
                iam_instance_profile_record["_id"] = iam_instance_profile_item[1]


    def prepare_instance_details_json(self,instance_details_item,instance_details_record):

        match instance_details_item[0]:

            case "AvailabilityZone":

                instance_details_record["availability_zone"] = instance_details_item[1]

            case "IamInstanceProfile":

                iam_instance_profile_record = IamInstanceProfileRecord()

                dict(filter(lambda item: self.prepare_iam_instance_profile_json(item,iam_instance_profile_record), instance_details_item[1].items()))

                instance_details_record["iam_instance_profile"] = iam_instance_profile_record

            case "ImageDescription":

                instance_details_record["image_description"] = instance_details_item[1]

            case "ImageId":
                
                instance_details_record["image_id"] = instance_details_item[1]

            case "InstanceState":
                
                instance_details_record["instance_state"] = instance_details_item[1]

            case "InstanceType":
                
                instance_details_record["instance_type"] = instance_details_item[1]

            case "OutpostArn":
                
                instance_details_record["outpost_arn"] = instance_details_item[1]

            case "NetworkInterfaces":

                network_interfaces_list = list()

                for network_interface in instance_details_item[1]:

                    network_interface_record = NetworkInterfaceRecord()

                    list(filter(lambda item: self.prepare_network_interface_json(item, network_interface_record),network_interface.items()))

                    network_interfaces_list.append(network_interface_record)

                instance_details_record["network_interfaces"] = network_interfaces_list

            case "Platform":

                instance_details_record["platform"] = instance_details_item[1]

            case "ProductCodes":

                product_list = list()

                for product_item in instance_details_item[1]:

                    product_record = ProductRecord()

                    list(filter(lambda item: self.prepare_product_codes_json(item,product_record),product_item.items()))

                    product_list.append(product_record)

                instance_details_record["product_codes"] = product_list

            case "Tags":

                tags_list = list()

                for tag_item in instance_details_item[1]:

                    tag_record = TagRecord()

                    list(filter(lambda item: self.prepare_tag_json(item, tag_record), tag_item.items()))

                    tags_list.append(tag_record)

                instance_details_record["tags"] = tags_list

    
    def prepare_resource_json(self,resource_item,resource_record):

        # This method iterates on the resource_item tuple

        # For debugging purposes --
        # print(type(resource_item))
        # print(resource_item)

        match resource_item[0]:

            case "AccessKeyDetails":

                access_key_details_record = AccessKeyDetailsRecord()

                dict(filter(lambda item: self.prepare_access_key_details_json(item,access_key_details_record),resource_item[1].items()))

                resource_record["access_key_details"] = access_key_details_record


            case "InstanceDetails":

                instance_details_record = InstanceDetailsRecord()
                dict(filter(lambda item: self.prepare_instance_details_json(item,instance_details_record),resource_item[1].items()))

                resource_record["instance_details"] = instance_details_record

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

            case "Arn":
            
                json_record["arn"] = record_item[1]

            case "CreatedAt":

                json_record["created_at"] = record_item[1]

            case "Description":

                json_record["description"] = record_item[1]

            case "Id":

                json_record["_id"] = record_item[1]

            case "Region": 

                json_record["region"] = record_item[1]

            case "Resource":

                resource_dict = dict(record_item[1])
                
                resource_record = ResourceRecord()

                dict(filter(lambda item: self.prepare_resource_json(item,resource_record),resource_dict.items()))

                json_record["resource"] = resource_record

            case "SchemaVersion":

                json_record["schema_version"] = record_item[1]

            case "Service":

                service_record = ServiceRecord()

                dict(filter(lambda item: self.prepare_service_json(item, service_record),record_item[1].items()))

                json_record["service"] = service_record

            case "Severity":

                json_record["severity"] = record_item[1]

            case "Title":

                json_record["title"] = record_item[1]

            case "Type":

                json_record["_type"] = record_item[1]

            case "UpdatedAt":

                json_record["updated_at"] = record_item[1]

 
    def read_from_file(self):
 
        with open(self.file_path, "r") as file:
 
            self.json_dict = json.load(file)

            for record in self.json_dict:
 
                # For debugging purposes --
                # print(json.dumps(record, indent= 4))

                json_record = JSONRecord()
 
                # Create a JSONRecord type here pertaining to one JSON
                # object and pass it to the prepare_json method. 
                # Each item here is a key value pair (<class 'tuple'>) for
                # one individual JSON object in the JSON file provided.

                dict(filter(lambda item: self.prepare_json(item,json_record),record.items()))
                

                # Appending the JSONRecord to the main list after populating
                self.json_record_list.append(json_record)


            for item in self.json_record_list:
                print(self.json_record_list)

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
