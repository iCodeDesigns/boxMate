import subprocess
from py4j.java_gateway import JavaGateway

def start_java():
    # Note: I assume that my_library.jar contains the library you want to expose with your CLI program.
    ARGS = ['java', '-jar', '/media/ahmed/Work/MashreqArabia/Internship/BoxMate/EtaInvoiceSubmission_Model_adflib.jar', 'arkleap.apps.ar.inv.model.SignatureInvoice']
    p = subprocess.Popen(ARGS)
    
    gateway = JavaGateway()
    converter = gateway.entry_point #get instance of converter
    json_data = {
    "documents": [
        {
            "issuer": {
                "type": "B",
                "id": "100324932",
                "name": "Dreem",
                "address": {
                    "branchID": "0",
                    "country": "EG",
                    "governate": "Cairo",
                    "regionCity": "Nasr City",
                    "street": "580 Clementina Key",
                    "buildingNumber": "Bldg. 0",
                    "postalCode": "68030",
                    "floor": "1",
                    "room": "123",
                    "landmark": "7660 Melody Trail",
                    "additionalInformation": "beside Townhall"
                }
            },
            "receiver": {
                "type": "B",
                "id": "313717919",
                "name": "Receiver",
                "address": {
                    "country": "EG",
                    "governate": "Egypt",
                    "regionCity": "Mufazat al Ismlyah",
                    "street": "580 Clementina Key",
                    "buildingNumber": "Bldg. 0",
                    "postalCode": "68030",
                    "floor": "1",
                    "room": "123",
                    "landmark": "7660 Melody Trail",
                    "additionalInformation": "Egypt"
                }
            },
            "documentType": "I",
            "documentTypeVersion": "0.9",
            "dateTimeIssued": "2021-02-18T12:52:30Z",
            "taxpayerActivityCode": "1079",
            "internalID": "AR-00021",
            "purchaseOrderReference": "P-233-A6375",
            "purchaseOrderDescription": "purchase Order description",
            "salesOrderReference": "Sales Order description",
            "salesOrderDescription": "Sales Order description",
            "proformaInvoiceNumber": "SomeValue",
            "totalDiscountAmount": 13.258,
            "totalSalesAmount": 662.9,
            "netAmount": 649.642,
            "taxTotals": [],
            "totalAmount": 2215.08914,
            "extraDiscountAmount": 5.0,
            "totalItemsDiscountAmount": 5.0,
            "invoiceLines": [
                {
                    "description": "Fruity Machine",
                    "itemType": "EGS",
                    "itemCode": "EG-100324932-11111",
                    "unitType": "EA",
                    "quantity": 7.0,
                    "internalCode": "FSPM001",
                    "salesTotal": 662.9,
                    "total": 2220.08914,
                    "valueDifference": 7.0,
                    "totalTaxableFees": 618.69212,
                    "netTotal": 649.642,
                    "itemsDiscount": 5.0,
                    "unitValue": {
                        "amountEGP": 94.7,
                        "amountSold": 4.735,
                        "currencyExchangeRate": 20.0,
                        "currencySold": "USD"
                    },
                    "discount": {
                        "rate": 2.0,
                        "amount": 13.258
                    },
                    "taxableItems": [
                        {
                            "taxType": "T1",
                            "amount": 204.67639,
                            "subType": "V001",
                            "rate": 14.0
                        },
                        {
                            "taxType": "T2",
                            "amount": 156.64009,
                            "subType": "Tbl01",
                            "rate": 12.0
                        },
                        {
                            "taxType": "T3",
                            "amount": 30.0,
                            "subType": "Tbl02",
                            "rate": 0.0
                        },
                        {
                            "taxType": "T4",
                            "amount": 32.2321,
                            "subType": "W001",
                            "rate": 5.0
                        },
                        {
                            "taxType": "T5",
                            "amount": 90.94988,
                            "subType": "ST01",
                            "rate": 14.0
                        },
                        {
                            "taxType": "T6",
                            "amount": 60.0,
                            "subType": "ST02",
                            "rate": 0.0
                        },
                        {
                            "taxType": "T7",
                            "amount": 64.9642,
                            "subType": "Ent01",
                            "rate": 10.0
                        },
                        {
                            "taxType": "T8",
                            "amount": 90.94988,
                            "subType": "RD01",
                            "rate": 14.0
                        },
                        {
                            "taxType": "T9",
                            "amount": 77.95704,
                            "subType": "SC01",
                            "rate": 12.0
                        },
                        {
                            "taxType": "T10",
                            "amount": 64.9642,
                            "subType": "Mn01",
                            "rate": 10.0
                        },
                        {
                            "taxType": "T11",
                            "amount": 90.94988,
                            "subType": "MI01",
                            "rate": 14.0
                        },
                        {
                            "taxType": "T12",
                            "amount": 77.95704,
                            "subType": "OF01",
                            "rate": 12.0
                        },
                        {
                            "taxType": "T13",
                            "amount": 64.9642,
                            "subType": "ST03",
                            "rate": 10.0
                        },
                        {
                            "taxType": "T14",
                            "amount": 90.94988,
                            "subType": "ST04",
                            "rate": 14.0
                        },
                        {
                            "taxType": "T15",
                            "amount": 77.95704,
                            "subType": "Ent03",
                            "rate": 12.0
                        },
                        {
                            "taxType": "T16",
                            "amount": 64.9642,
                            "subType": "RD03",
                            "rate": 10.0
                        },
                        {
                            "taxType": "T17",
                            "amount": 64.9642,
                            "subType": "SC03",
                            "rate": 10.0
                        },
                        {
                            "taxType": "T18",
                            "amount": 90.94988,
                            "subType": "Mn03",
                            "rate": 14.0
                        },
                        {
                            "taxType": "T19",
                            "amount": 77.95704,
                            "subType": "MI03",
                            "rate": 12.0
                        },
                        {
                            "taxType": "T20",
                            "amount": 64.9642,
                            "subType": "OF03",
                            "rate": 10.0
                        }
                    ]
                }
            ]
        }
    ]
}
    x = converter.getFullSignedDocument(json_data,"Dreem" , "08268939")
    print(x)
    print('Java Started: {0}'.format(p.pid))

start_java()