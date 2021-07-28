#!/usr/bin/env python3

import xml.etree.ElementTree as ET
import datetime
import base64
from . ixbrl import get_values, to_date, to_money, to_whole_money

ct_ns = "http://www.govtalk.gov.uk/taxation/CT/5"
ET.register_namespace("ct", ct_ns)

def to_return(comps, accts, params, atts):

    comps_doc = ET.fromstring(comps)
    
    x = get_values(comps_doc)

    comp_ixbrl = base64.b64encode(comps.encode("utf-8")).decode("utf-8")
    accounts_ixbrl = base64.b64encode(accts.encode("utf-8")).decode("utf-8")

    ret = {
        "CompanyTaxReturn": {
            "CompanyInformation": {
                "CompanyName": x["ct-comp:CompanyName"],
                "RegistrationNumber": x["uk-core:UKCompaniesHouseRegisteredNumber"],
                "Reference": x["ct-comp:TaxReference"],
                "CompanyType": params.get("company-type"),
                "PeriodCovered": {
                    "From": to_date(x["ct-comp:StartOfPeriodCoveredByReturn"]),
                    "To": to_date(x["ct-comp:EndOfPeriodCoveredByReturn"]),
                }
            },
            "ReturnInfoSummary": {
                "ThisPeriod": "yes",
                "Accounts": {
                    "ThisPeriodAccounts": "yes"
                },
                "Computations": {
                    "ThisPeriodComputations": "yes"
                },
                "SupplementaryPages": {
                }
            },
            "Turnover": {
                "Total": to_money(x["uk-core:TurnoverRevenue"])
            },
            "CompanyTaxCalculation": {
                "Income": {
                    "Trading": {
                        "Profits": to_money(x["ct-comp:AdjustedTradingProfitOfThisPeriod"]),
                        "NetProfits": to_money(x["ct-comp:NetTradingProfits"])                    
                    },
#                    "NonTradingLoanProfitsAndGains": to_money(0),
                },
                "ChargeableGains": {
                    "NetChargeableGains": to_money(x["ct-comp:NetChargeableGains"])
                },
                "ProfitsBeforeOtherDeductions": to_money(x["ct-comp:ProfitsBeforeOtherDeductionsAndReliefs"]),
                "DeductionsAndReliefs": {
                    "ManagementExpenses": to_money(x["ct-comp:TotalManagementExpenses"]),
                    "Total": to_money(x["ct-comp:TotalDeductionsAndReliefs"])
                },
                "ChargesAndReliefs": {
                    "ProfitsBeforeDonationsAndGroupRelief": to_money(x["ct-comp:ProfitsBeforeChargesAndGroupRelief"])
                },
                "ChargeableProfits": to_money(x["ct-comp:TotalProfitsChargeableToCorporationTax"]),
                "CorporationTaxChargeable": {
                    "FinancialYearOne": {
                        "Year": x["ct-comp:FinancialYear1CoveredByTheReturn"],
                        "Details": {
                            "Profit": to_money(x["ct-comp:FY1AmountOfProfitChargeableAtFirstRate"]),
                            "TaxRate": to_money(x["ct-comp:FY1FirstRateOfTax"]),
                            "Tax": to_money(x["ct-comp:FY1TaxAtFirstRate"])
                        }
                    },
                    "FinancialYearTwo": {
                        "Year": x["ct-comp:FinancialYear2CoveredByTheReturn"],
                        "Details": {
                            "Profit": to_money(x["ct-comp:FY2AmountOfProfitChargeableAtFirstRate"]),
                            "TaxRate": to_money(x["ct-comp:FY2FirstRateOfTax"]),
                            "Tax": to_money(x["ct-comp:FY2TaxAtFirstRate"])
                        }
                    }
                },
                "CorporationTax": to_money(x["ct-comp:CorporationTaxChargeable"]),
                "NetCorporationTaxChargeable": to_money(x["ct-comp:CorporationTaxChargeable"])
            },
            "CalculationOfTaxOutstandingOrOverpaid": {
                "NetCorporationTaxLiability": to_money(x["ct-comp:CorporationTaxChargeable"]),
                "TaxChargeable": to_money(x["ct-comp:TaxChargeable"]),
                "TaxPayable": to_money(x["ct-comp:TaxPayable"])
            },
            "EnhancedExpenditure": {
                "SMEclaim": "yes",
                "RandDEnhancedExpenditure": to_money(x["ct-comp:AdjustmentsAdditionalDeductionForQualifyingRDExpenditureSME"]),
                "RandDAndCreativeEnhancedExpenditure": to_money(x["ct-comp:AdjustmentsAdditionalDeductionForQualifyingRDExpenditureSME"])
            },
            "AllowancesAndCharges": {
                "AIACapitalAllowancesInc": to_money(x["ct-comp:MainPoolAnnualInvestmentAllowance"]),
            },
            "Declaration": {
                "AcceptDeclaration": "yes",
                "Name": params.get("declaration-name"),
                "Status": params.get("declaration-status")
            },
            "AttachedFiles": {
                "XBRLsubmission": {
                    "Computation": {
                        "Instance": {
                            "EncodedInlineXBRLDocument": comp_ixbrl
                        }
                    },
                    "Accounts": {
                        "Instance": {
                            "EncodedInlineXBRLDocument": accounts_ixbrl
                        }
                    }
                }
            }
        }
    }

    ret = {
        "IRenvelope": {
            "IRheader": {
                "Keys": {
                    "Key": x["ct-comp:TaxReference"]
                },
                "PeriodEnd": to_date(x["ct-comp:EndOfPeriodCoveredByReturn"]),
                "Principal": {
                    "Contact": {
                        "Name": {
                            "Ttl": params.get("title"),
                            "Fore": params.get("first-name"),
                            "Sur": params.get("second-name")
                        },
                        "Email": params.get("email"),
                        "Telephone": {
                            "Number": params.get("phone")
                        }
                    }
                },
                "IRmark": "",
                "Sender": "Company"
            },
            "CompanyTaxReturn": ret["CompanyTaxReturn"]
        }
    }

    if len(ret.keys()) != 1:
        raise RuntimeError("Oops")

    relt_name = list(ret.keys())[0]
    root = ET.Element("{%s}%s" % (ct_ns, relt_name))

    relt = ret[relt_name]

    def add(root, relt):

        for name in relt:

            tag = "{%s}%s" % (ct_ns, name)
            value = relt[name]

            if isinstance(relt[name], dict):
                sub = ET.SubElement(root, tag)
                add(sub, value)
            else:
                ET.SubElement(root, tag).text = str(value)

    add(root, relt)

    # This is all very hacky

    # CompanyTaxReturn needs an attribute
    root.find(".//{%s}CompanyTaxReturn[1]" % ct_ns).set(
        "ReturnType", "new"
    )

    # Key needs a UTR type attribute
    root.find(".//{%s}Key[1]" % ct_ns).set(
        "Type", "UTR"
    )

    attf_elt = root.find(".//{%s}AttachedFiles" % ct_ns)

    for k, v in atts.items():
        att_text = base64.b64encode(v).decode("utf-8")
        att_elt = ET.SubElement(attf_elt, "{%s}Attachment" % ct_ns)
        att_elt.set("Type", "other")
        att_elt.set("Format", "pdf")
        att_elt.set("Filename", k)
        att_elt.text = att_text

    return ET.ElementTree(root)

