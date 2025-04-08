import json 
import os
import pdb
import psycopg2
from psycopg2.extensions import parse_dsn,AsIs
from psycopg2 import sql
from typing import TypedDict


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


    def __init__ (self,file_path,sql_db):

        self.file_path = file_path
        
        self.json_dict = dict() 
        self.json_record_list = list()
        
        self.sql_db = sql_db

        # The key for each <class "dictitem"> should be the primary key and 
        # the value should be a dict with column names and values wrt the
        # corresponding primary key i.e record
        
        self.sql_record = dict()


    def initialize_sql_record(self, primary_key):

        self.sql_record[primary_key] = list()


    def insert_sql_record(self, primary_key, colname, value):

        if primary_key in self.sql_record.keys():

            self.sql_record[primary_key].append(tuple([colname,value]))


    def check_key(self,json_d,key):

        if key in json_d:
            
            return True
        
        else:
        
            return False


    def prepare_action_json(self, action_item, action_record, primary_key):

        match action_item[0]:

            case "ActionType":

                action_record["action_type"] = action_item[1]

            case "AwsApiCallAction":

                aws_api_call_action_record = AwsApiCallActionRecord()

                dict(filter(lambda item: self.prepare_aws_api_call_action_json(item, aws_api_call_action_record, primary_key),action_item[1].items()))

                action_record["aws_api_call_action"] = aws_api_call_action_record

    
    def prepare_remote_ip_details_json(self, remote_ip_details_item, remote_ip_details_record, primary_key):

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


    def prepare_aws_api_call_action_json(self, aws_api_call_action_item, aws_api_call_action_record, primary_key):

        match aws_api_call_action_item[0]:

            case "Api":
                
                aws_api_call_action_record["api"] = aws_api_call_action_item[1]

            case "CallerType":

                aws_api_call_action_record["caller_type"] = aws_api_call_action_item[1]

            case "ErrorCode":

                aws_api_call_action_record["error_code"] = aws_api_call_action_item[1]

            case "RemoteIpDetails":

                remote_ip_details_record = RemoteIpDetailsRecord()

                dict(filter(lambda item: self.prepare_remote_ip_details_json(item,remote_ip_details_record, primary_key),aws_api_call_action_item[1].items()))

                aws_api_call_action_record["remote_ip_details"] = remote_ip_details_record

            case "ServiceName":

                aws_api_call_action_record["service_name"] = aws_api_call_action_item[1]

            case "AffectedResources":

                aws_api_call_action_record["affected_resources"] = aws_api_call_action_item[1]


    def prepare_product_codes_json(self,product_item,product_record, primary_key):

        match product_item[0]:

            case "Code":
                
                product_record["code"] = product_item[1]

            case "ProductType":

                product_record["product_type"] = product_item[1]


    def prepare_additional_info_json(self, additional_info_item, additional_info_record, primary_key):

        match additional_info_item[0]:

            case "Value":

                additional_info_record["value"] = additional_info_item[1]

            case "Type":

                additional_info_record["_type"] = additional_info_item[1]


    def prepare_service_json(self, service_item, service_record, primary_key):

        match service_item[0]:

            case "Action":

                action_record = ActionRecord()

                dict(filter(lambda item: self.prepare_action_json(item,action_record,primary_key),service_item[1].items()))

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

                dict(filter(lambda item: self.prepare_additional_info_json(item,additional_info_record, primary_key),service_item[1].items()))

                service_record["additional_info"] = service_item[1]


    def prepare_private_ip_addresses_json(self, private_ip_address_item, private_ip_address_record, primary_key):
        
        match private_ip_address_item[0]:

            case "PrivateDnsName":
                
                private_ip_address_record["private_dns_name"] = private_ip_address_item[1]
            
            case "PrivateIpAddress":

                private_ip_address_record["private_ip_address"] = private_ip_address_item[1]


    def prepare_security_groups_json(self, security_group_item, security_group_record, primary_key):

        match security_group_item[0]:

            case "GroupId":
                
                security_group_record["group_id"] = security_group_item[1]

            case "GroupName":
                
                security_group_record["group_name"] = security_group_item[1]


    def prepare_network_interface_json(self, network_interface_item, network_interface_record, primary_key):

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
                    
                    list(filter(lambda item: self.prepare_private_ip_addresses_json(item,private_ip_address_record,primary_key),private_ip_addresses_item.items()))

                    private_ip_addresses_list.append(private_ip_address_record);

                network_interface_record["private_ip_addresses"] = private_ip_addresses_list

            case "PublicDnsName":

                network_interface_record["public_dns_name"] = network_interface_item[1]

            case "PublicIp":

                network_interface_record["public_ip"] = network_interface_item[1]

                self.insert_sql_record(primary_key,"public_ip",network_interface_item[1])

            case "SecurityGroups":

                security_groups_list = list()

                for security_group_item in network_interface_item[1]:

                    security_group_record = SecurityGroupRecord()
                    
                    list(filter(lambda item: self.prepare_security_groups_json(item,security_group_record, primary_key),security_group_item.items()))
                    
                    security_groups_list.append(security_group_record)

                network_interface_record["security_groups"] = security_groups_list

            case "SubnetId":

                network_interface_record["subnet_id"] = network_interface_item[1]

            case "VpcId":

                network_interface_record["vpc_id"] = network_interface_item[1]
                
                self.insert_sql_record(primary_key,"vpc_id",network_interface_item[1])


    def prepare_access_key_details_json(self,access_key_details_item,access_key_details_record,primary_key):

        match access_key_details_item[0]:

            case "AccessKeyId":

                access_key_details_record["access_key_id"] = access_key_details_item[1]

            case "PrincipleId":

                access_key_details_record["principle_id"] = access_key_details_item[1]

            case "UserName":

                access_key_details_record["user_name"] = access_key_details_item[1]

            case "UserType":

                access_key_details_record["user_type"] = access_key_details_item[1]


    def prepare_tag_json(self,tag_item,tag_record,primary_key):

        match tag_item[0]:

            case "Key":
                
                tag_record["key"] = tag_item[1]

            case "Value":

                tag_record["value"] = tag_item[1]


    def prepare_iam_instance_profile_json(self,iam_instance_profile_item,iam_instance_profile_record,primary_key):

        match iam_instance_profile_item[0]:

            case "Arn":
                
                iam_instance_profile_record["arn"] = iam_instance_profile_item[1]

                self.insert_sql_record(primary_key,"iam_arn",iam_instance_profile_item[1])
            
            case "Id":
                
                iam_instance_profile_record["_id"] = iam_instance_profile_item[1]

                self.insert_sql_record(primary_key,"iam_id",iam_instance_profile_item[1])
            


    def prepare_instance_details_json(self,instance_details_item,instance_details_record,primary_key):

        match instance_details_item[0]:

            case "AvailabilityZone":

                instance_details_record["availability_zone"] = instance_details_item[1]

            case "IamInstanceProfile":

                iam_instance_profile_record = IamInstanceProfileRecord()

                dict(filter(lambda item: self.prepare_iam_instance_profile_json(item,iam_instance_profile_record, primary_key), instance_details_item[1].items()))

                instance_details_record["iam_instance_profile"] = iam_instance_profile_record

            case "ImageDescription":

                instance_details_record["image_description"] = instance_details_item[1]

            case "ImageId":
                
                instance_details_record["image_id"] = instance_details_item[1]

            case "InstanceState":
                
                instance_details_record["instance_state"] = instance_details_item[1]

            case "InstanceType":
                
                instance_details_record["instance_type"] = instance_details_item[1]

                self.insert_sql_record(primary_key,"instance_type",instance_details_item[1])

            case "InstanceId":
                
                instance_details_record["instance_id"] = instance_details_item[1]

                self.insert_sql_record(primary_key,"instance_id",instance_details_item[1])
            
            case "OutpostArn":
                
                instance_details_record["outpost_arn"] = instance_details_item[1]

            case "NetworkInterfaces":

                network_interfaces_list = list()

                for network_interface in instance_details_item[1]:

                    network_interface_record = NetworkInterfaceRecord()

                    list(filter(lambda item: self.prepare_network_interface_json(item, network_interface_record, primary_key),network_interface.items()))

                    network_interfaces_list.append(network_interface_record)

                instance_details_record["network_interfaces"] = network_interfaces_list

            case "Platform":

                instance_details_record["platform"] = instance_details_item[1]

            case "ProductCodes":

                product_list = list()

                for product_item in instance_details_item[1]:

                    product_record = ProductRecord()

                    list(filter(lambda item: self.prepare_product_codes_json(item,product_record, primary_key),product_item.items()))

                    product_list.append(product_record)

                instance_details_record["product_codes"] = product_list

            case "Tags":

                tags_list = list()

                for tag_item in instance_details_item[1]:

                    tag_record = TagRecord()

                    list(filter(lambda item: self.prepare_tag_json(item, tag_record, primary_key), tag_item.items()))

                    tags_list.append(tag_record)

                instance_details_record["tags"] = tags_list

    
    def prepare_resource_json(self,resource_item,resource_record,primary_key):

        # This method iterates on the resource_item tuple

        # For debugging purposes --
        # print(type(resource_item))
        # print(resource_item)

        match resource_item[0]:

            case "AccessKeyDetails":

                access_key_details_record = AccessKeyDetailsRecord()

                dict(filter(lambda item: self.prepare_access_key_details_json(item,access_key_details_record, primary_key),resource_item[1].items()))

                resource_record["access_key_details"] = access_key_details_record


            case "InstanceDetails":

                instance_details_record = InstanceDetailsRecord()

                dict(filter(lambda item: self.prepare_instance_details_json(item,instance_details_record, primary_key),resource_item[1].items()))

                resource_record["instance_details"] = instance_details_record

            case "ResourceType":

                resource_record["resource_type"] = resource_item[1]

                self.insert_sql_record(primary_key,"resource_type",resource_item[1])

 
    def prepare_json(self, record_item, json_record, primary_key):

        # This method iterates over the dictionary, per each tuple 
        # and populates individual JSONRecord for the relevant JSON object  
 
        match record_item[0]:

            case "AccountId":

                json_record["account_id"] = record_item[1] 

                self.insert_sql_record(primary_key,"account_id",record_item[1])

            case "Arn":
            
                json_record["arn"] = record_item[1]

                # self.insert_sql_record(primary_key,"arn",record_item[1])

            case "CreatedAt":

                json_record["created_at"] = record_item[1]

                self.insert_sql_record(primary_key,"created_at",record_item[1])

            case "Description":

                json_record["description"] = record_item[1]

                self.insert_sql_record(primary_key,"description",record_item[1])

            case "Id":

                json_record["_id"] = record_item[1]
                
                self.insert_sql_record(primary_key,"id",record_item[1])

            case "Region": 

                json_record["region"] = record_item[1]

                self.insert_sql_record(primary_key,"region",record_item[1])

            case "Resource":

                resource_dict = dict(record_item[1])
                
                resource_record = ResourceRecord()

                dict(filter(lambda item: self.prepare_resource_json(item,resource_record,primary_key),resource_dict.items()))

                json_record["resource"] = resource_record

            case "SchemaVersion":

                json_record["schema_version"] = record_item[1]

                # self.insert_sql_record(primary_key,"schema_version",record_item[1])

            case "Service":

                service_record = ServiceRecord()

                dict(filter(lambda item: self.prepare_service_json(item, service_record, primary_key),record_item[1].items()))

                json_record["service"] = service_record

            case "Severity":

                json_record["severity"] = record_item[1]
                
                self.insert_sql_record(primary_key,"severity",record_item[1])


            case "Title":

                json_record["title"] = record_item[1]

                self.insert_sql_record(primary_key,"title",record_item[1])


            case "Type":

                json_record["_type"] = record_item[1]

                # self.insert_sql_record(primary_key,"alert_type",record_item[1])


            case "UpdatedAt":

                json_record["updated_at"] = record_item[1]

                self.insert_sql_record(primary_key,"updated_at",record_item[1])


 
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

                self.initialize_sql_record(record["Id"])
                dict(filter(lambda item: self.prepare_json(item,json_record,record["Id"]),record.items()))

            
                # Appending the JSONRecord to the main list after populating
                self.json_record_list.append(json_record)


            self.sql_db.write_into_sql_db(self.sql_record)


            # for record in self.sql_record.items():
            #     print(record)

            # print(type(self.sql_record))


            # for item in self.json_record_list:
            #    print(self.json_record_list)

'''

class ArgumentParser:

    # TODO: Adding some argument options here
    # takes an argumentparser object, but
    # have not decided upon options provided.
    
    def setup_arguments(parser):

        # TODO: Set up of command line options here 
        # including the help description

'''

class SQL_DB:

    
    def __init__(self):
        
        self.database_host = "localhost"
        self.database_port = "5432"
        self.database_user = "postgres"
        self.database_pass = "password"
        self.database_name = "gd_security_alerts"

        self.dsn_string = " dbname=" + self.database_name + "      \
                            user=" + self.database_user + "        \
                            password=" + self.database_pass + "    \
                            host=" + self.database_host + "        \
                            port=" + self.database_port

        # print(parse_dsn(self.dsn_string))

        try:

            self.database_connection = psycopg2.connect(self.dsn_string)
        
        except psycopg2.Error as e:

            print("Unable to connect to the database")

        else:
            with self.database_connection:
                with self.database_connection.cursor() as cursor:
                    try:

                        cursor.execute("CREATE TABLE guardduty_alerts ("      \
                                            "gd_id VARCHAR(255) PRIMARY KEY," \
                                            "account_id VARCHAR(255),"        \
                                            "region VARCHAR(100),"            \
                                            "created_at TIMESTAMP,"           \
                                            "updated_at TIMESTAMP,"           \
                                            "severity INT,"                   \
                                            "public_ip VARCHAR(50),"          \
                                            "instance_id VARCHAR(255),"       \
                                            "instance_type VARCHAR(100),"     \
                                            "iam_arn VARCHAR(255),"           \
                                            "iam_id VARCHAR(255),"            \
                                            "vpc_id VARCHAR(255),"            \
                                            "title VARCHAR(255),"             \
                                            "resource_type VARCHAR(100),"     \
                                            "description VARCHAR,"            \
                                            "additional_data JSONB);")
                    
                    except psycopg2.Error as e:

                        print("PostGreSQL Error "+ str(e))
                        
                        if "Relation already exists" in str(e):
                            try:
                                # Reinitializing the table as we are creating a new
                                # SQL_DB object that takes in a new file entirely.
                                # The other alternative method is to just add to the 
                                # same database 

                                '''
                                cursor.execute("DROP TABLE guardduty_alerts;")
                                
                                cursor.execute("CREATE TABLE guardduty_alerts ("      \
                                                    "gd_id VARCHAR(255) PRIMARY KEY," \
                                                    "account_id VARCHAR(255),"        \
                                                    "region VARCHAR(100),"            \
                                                    "created_at TIMESTAMP,"           \
                                                    "updated_at TIMESTAMP,"           \
                                                    "severity INT,"                   \
                                                    "public_ip VARCHAR(50),"          \
                                                    "instance_id VARCHAR(255),"       \
                                                    "instance_type VARCHAR(100),"     \
                                                    "iam_arn VARCHAR(255),"           \
                                                    "iam_id VARCHAR(255),"            \
                                                    "vpc_id VARCHAR(255),"            \
                                                    "title VARCHAR(255),"             \
                                                    "resource_type VARCHAR(100),"     \
                                                    "description VARCHAR,"            \
                                                    "additional_data JSONB);")
                                '''
                                print("We are adding into the same Database contents of a new file")

                            except psycopg2.Error as e:

                                print("Table guardduty_alerts could not be reinitialized to accept a new file")

            self.database_connection.close()


    def write_into_sql_db(self,sql_record):

        print("Writing into the table")
        modified_sql_record = dict()

        for key in sql_record:
            
            ip_list = list()
            vpc_list = list()
            ip_dict = dict()
            vpc_dict = dict()


            # The data structure sql_record is a Dictionary, i.e key value pairs
            # Each individual value in sql_record corresponds to one record being
            # placed in the database. The key is the Primary Key in sql_record, and 
            # the value is a list of tuples. Each tuple represents column name and 
            # value for that column

            record = sql_record[key]

            for column_item in record:
                
                # Each record is a list of tuples with column_item representing
                # one tuple in the list 
                
                if column_item[0]=="public_ip":
                    
                    ip_list.append(column_item[1])

            for column_item in record:
                
                # Each record is a list of tuples with column_item representing
                # one tuple in the list 

                if column_item[0]=="vpc_id":
                    
                    vpc_list.append(column_item[1])

            ip_dict = { "public_ip" : ip_list }
            vpc_dict = { "vpc_id" : vpc_list }

            record = [ item for item in record if item[0]!="public_ip" and item[0]!="vpc_id" ]
            
            record.append(ip_dict)
            record.append(vpc_dict)

            modified_sql_record[key] = record


        # Attempting to connect with the database and obtain a cursor object


        try:

            self.database_connection = psycopg2.connect(self.dsn_string)

        except psycopg2.Error as e:

            print("Unable to connect to the database")

        else:
            with self.database_connection:
                with self.database_connection.cursor() as cursor:
                    try:

                        for key in modified_sql_record:

                            # Initializing all records. First query sets up primary key column in database 

                            query = cursor.mogrify(sql.SQL("""INSERT INTO %(table)s (%(colname)s) VALUES (%(pkey)s)  \
                                                           """),{ 'table' : AsIs("guardduty_alerts"), 'colname' : AsIs('gd_id'), 'pkey' : str(key) })
                            cursor.execute(query)

                            for item in modified_sql_record[key]:

                                # For each record, with Primary Key as id, we add all the columns after encoding for the database. 
                                # Preparing parameterized queries

                                if type(item) is tuple:

                                    if item[0]!="id":
                                            
                                        query = cursor.mogrify("""UPDATE %(table)s SET %(colname)s = %(value)s WHERE gd_id=%(pkey)s \
                                                    """,{'table' : AsIs("guardduty_alerts"), 'colname': AsIs(str(item[0])), 'value' : str(item[1]), 'pkey' : str(key)})
                                    

                                elif type(item) is  dict:

                                    if "public_ip" in item:

                                        ip_item = item["public_ip"]

                                        if len(ip_item)!= 0 :

                                            query = cursor.mogrify("""UPDATE %(table)s SET %(colname)s = %(value)s  WHERE gd_id=%(pkey)s \
                                                                   """,{'table' : AsIs("guardduty_alerts"), 'colname': AsIs("public_ip"), 'value' : str(ip_item[0]), 'pkey' : str(key)}) 

                                    elif "vpc_id" in item:

                                        vpc_item = item["vpc_id"]

                                        if len(vpc_item)!= 0:

                                            query = cursor.mogrify("""UPDATE %(table)s SET %(colname)s = %(value)s  WHERE gd_id=%(pkey)s \
                                                                   """,{'table' : AsIs("guardduty_alerts"), 'colname': AsIs("vpc_id"), 'value' : str(vpc_item[0]), 'pkey' : str(key)})
                                    
                                cursor.execute(query)
                    
                    except psycopg2.Error as e:

                        # TODO : Write a check for database already existing 
                        # but for now this suffices --

                        if "duplicate key value violates unique constraint" in str(e):
                        
                            print("Database already populated with values for these primary keys")
                        
                        else:
                            
                            print("Database Error :" + str(e))


            self.database_connection.close()


    # def  write_to_sql_db(self):
    
    # TODO: The TypedDict records are to be passed to 
    # this method and it handles writing to the database.


    def print_sql_results(self,results):

        
        print("-----------------------------------------------------------")
        
        print("SQL query returned " + str(len(results)) + " records")
        
        print("-----------------------------------------------------------")
 
        for record in results:

            print(record)
            print("-----------------------------------------------------------")
    

    def read_from_sql_db(self,options):

        # TODO: Retrieve all high security alerts
        # SELECT * FROM guardduty_alerts WHERE severity > 5

        # TODO: Count of alerts per Region 
        # SELECT COUNT(*) FROM guardduty_alerts GROUP BY region

        # TODO: Find alerts by specific IP address
        # SELECT * FROM guardduty_alerts WHERE ipaddress='<insert ip address here>'

        # TODO: Extract Title and Description from JSON Data
        # SELECT title,description FROM guardduty_alerts

        # TODO: Detect IAM Users involved in Alerts
        # SELECT iam_id,iam_arn FROM guardduty_alerts


        try:

            self.database_connection = psycopg2.connect(self.dsn_string)

        except psycopg2.Error as e:

            print("Unable to connect to the database")
        
        else:
                        
            if type(options) is list:
                option = options[0]
                ipaddress = options[1]
            else:
                option = options

            with self.database_connection:
                with self.database_connection.cursor() as cursor:
                    try:

                        match option:

                            case 1:

                                query = cursor.mogrify(sql.SQL("""SELECT * FROM %(table)s WHERE severity > 7  \
                                                           """),{ 'table' : AsIs("guardduty_alerts") })

                                cursor.execute(query)
                                results = cursor.fetchall()

                                self.print_sql_results(results)

                            case 2:

                                query = cursor.mogrify(sql.SQL("""SELECT DISTINCT COUNT(*) FROM  %(table)s GROUP BY region  \
                                                           """),{ 'table' : AsIs("guardduty_alerts") })

                                cursor.execute(query)
                                results = cursor.fetchall()

                                self.print_sql_results(results)

                            case 3:

                                query = cursor.mogrify(sql.SQL("""SELECT * FROM %(table)s WHERE public_ip=(%(ipaddress)s)  \
                                                               """),{ 'table' : AsIs("guardduty_alerts"), 'ipaddress' : str(ipaddress) })
                                cursor.execute(query)
                                results = cursor.fetchall()

                                self.print_sql_results(results)

                            case 4:

                                query = cursor.mogrify(sql.SQL("""SELECT title, description FROM %(table)s  \
                                                           """),{ 'table' : AsIs("guardduty_alerts") })
                                cursor.execute(query)
                                results = cursor.fetchall()

                                self.print_sql_results(results)

                            case 5:

                                query = cursor.mogrify(sql.SQL("""SELECT iam_arn,iam_id FROM %(table)s  \
                                                           """),{ 'table' : AsIs("guardduty_alerts") })
                                cursor.execute(query)
                                results = cursor.fetchall()

                                self.print_sql_results(results)

                    except psycopg2.Error as e:

                        print("Database Error : " + str(e))



            self.database_connection.close()

def main():
    
    sql_db = SQL_DB()
    
    jsonparse = JSONParser("../GuarddutyAlertsSampleData/Guardduty Sample Alert Data.json",sql_db)
    jsonparse.read_from_file()

    # TODO: Handle giving the option to start the database from the textual interface
    # TODO: Handle the text based UI interface here for SQL querying and printing results. 
    # TODO: Handle loading of external AWS Guard Duty alerts JSON file into the database

    option = 0

    welcome_string = " Select the following command line options\n"                   \
                     " 1. SQL Query for selecting high severity (>7) alerts\n"        \
                     " 2. SQL Query for counting alerts per region\n"                 \
                     " 3. SQL Query for selecting alerts per ip address\n"            \
                     " 4. SQL Query for selecting Title and Descriptions of alerts\n" \
                     " 5. SQL Query for selecting IAM users involved with alerts\n"   \
                     " 6. Add new entries to the existing table guardduty_alerts\n"   \
                     " 7. Exit menu and close database gracefully...Goodbye! \n"


    while option != 7:
        
        print(welcome_string)
        
        option = int(input("Please enter your option here ----->"))

        if option > 7:
        
            print("-----------------------------------------------------------")

            print("User has entered the wrong option, please try again!\n")
            
            print("-----------------------------------------------------------")

            continue

        else:

            match option:
                
                case 1:

                    print("-----------------------------------------------------------")

                    sql_db.read_from_sql_db(option)

                    print("-----------------------------------------------------------")

                case 2:

                    print("-----------------------------------------------------------")

                    sql_db.read_from_sql_db(option)

                    print("-----------------------------------------------------------")

                case 3:

                    print("-----------------------------------------------------------")

                    options = list()
                    options.append(option)
                    options.append(input("Please enter the ip address to query the database with:"))

                    sql_db.read_from_sql_db(options)

                    print("-----------------------------------------------------------")

                case 4:

                    print("-----------------------------------------------------------")

                    sql_db.read_from_sql_db(option)

                    print("-----------------------------------------------------------")

                case 5:

                    print("-----------------------------------------------------------")

                    sql_db.read_from_sql_db(option)

                    print("-----------------------------------------------------------")

                case 6:

                    print("-----------------------------------------------------------")

                    jsonparse_1 = JSONParser("../GuarddutyAlertsSampleData-1/Guardduty Sample Alert Data.json",sql_db)
                    jsonparse_1.read_from_file()


                    print("-----------------------------------------------------------")



                case 7:

                    print("-----------------------------------------------------------")

                    # os.system("dropdb gd_security_alerts")
                    os.system("pg_ctl -D ../.tmp/db stop")
                    os._exit(os.EX_OK)

                    print("-----------------------------------------------------------")


                case _:

                    print("-----------------------------------------------------------")

                    print("User has entered the wrong option, please try again!\n")
                    continue

                    print("-----------------------------------------------------------")



if __name__ == "__main__":
    main()
