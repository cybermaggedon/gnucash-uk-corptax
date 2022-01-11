#!/usr/bin/env python3

from lxml import etree as ET
from io import BytesIO
import datetime
import base64

#from . ixbrl import get_values, to_date, to_money, to_whole_money
from ixbrl_parse.ixbrl import *
from ixbrl_parse.value import *

nsmap = {
    "http://www.hmrc.gov.uk/schemas/ct/comp/2021-01-01": "ct-comp",
    "http://www.hmrc.gov.uk/schemas/ct/dpl/2021-01-01": "dpl",
    "http://xbrl.frc.org.uk/fr/2021-01-01/core": "uk-core"
}

ct_ns = "http://www.govtalk.gov.uk/taxation/CT/5"

def to_date(d):
    return str(d)

def to_money(v):
    return "%.2f" % float(v)

def get(root, localname):
    for name, value in root.values.items():
        if name.localname == localname:
            yield value
    for reln, ctxt in root.children.items():
        for res in get(ctxt, localname):
            yield res

def get1(root, localname):
    for v in get(root, localname):
        return v
    raise RuntimeError("Not found")

def getperiod(root, s, e):

    for rel, ctxt in root.children.items():
        if isinstance(rel, Instant): continue
        if isinstance(rel, Entity):
            return getperiod(ctxt, s, e)
        if isinstance(rel, Period):
            if s == rel.start and e == rel.end:
                return ctxt

    return None

def getvalues(root, s, e, prefix=""):


    for name, value in root.values.items():

        if name.namespace in nsmap:
            n = nsmap[name.namespace] + ":" + name.localname
            yield prefix + n, value.to_value().get_value()
        else:
            raise RuntimeError("Namespace %s not known" % name.namespace)

    for rel, ctxt in root.children.items():

        if isinstance(rel, Instant):
            for name, value in getvalues(ctxt, s, e, prefix):
                yield name, value

        if isinstance(rel, Entity):

            yield (
                "uk-core:UKCompaniesHouseRegisteredNumber",
                rel.id
            )
                  
            for name, value in getvalues(ctxt, s, e, prefix):
                yield name, value

        if isinstance(rel, Period):
            if s == rel.start and e == rel.end:
                for name, value in getvalues(ctxt, s, e, prefix):
                    yield name, value

        if isinstance(rel, Dimension):
            pref = prefix + rel.value.localname + "/"
            pref = ""
            for name, value in getvalues(ctxt, s, e, pref):
                yield name, value

def get_values(comps):

    tree = ET.parse(BytesIO(comps))
    i = parse(tree)

    start = get1(i.root, "StartOfPeriodCoveredByReturn").to_value().get_value()
    end = get1(i.root, "EndOfPeriodCoveredByReturn").to_value().get_value()

    d = {}
    for n, v in getvalues(i.root, start, end):
        d[n] = v

    return d

def to_values(comps):
    return get_values(comps)

def to_return(comps, accts, params, atts):

#    comps_doc = ET.fromstring(comps)
    
    x = get_values(comps)

    comp_ixbrl = base64.b64encode(comps).decode("utf-8")
    accounts_ixbrl = base64.b64encode(accts).decode("utf-8")

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
    root = ET.Element(
        "{%s}%s" % (ct_ns, relt_name),
        nsmap={"ct": ct_ns}
    )

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

