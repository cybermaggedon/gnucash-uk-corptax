#!/usr/bin/env python3

from lxml import etree as ET
from io import BytesIO
import datetime
import base64

from ixbrl_parse.ixbrl import *
from ixbrl_parse.value import *

nsmap = {
    "http://www.hmrc.gov.uk/schemas/ct/comp/2021-01-01": "ct-comp",
    "http://www.hmrc.gov.uk/schemas/ct/dpl/2021-01-01": "dpl",
    "http://xbrl.frc.org.uk/fr/2021-01-01/core": "uk-core"
}

ct_ns = "http://www.govtalk.gov.uk/taxation/CT/5"

# Presents a date in the appropriate format for CT XML
def to_date(d):
    return str(d)

# Presents cash in the appropriate format for CT XML
def to_money(v):
    return "%.2f" % float(v)

# Iterates over a context and all child, extracting values as k,v pairs.
def get_all_context_values(ctxt):

    for name, value in ctxt.values.items():
        if name.namespace in nsmap:
            n = nsmap[name.namespace] + ":" + name.localname
            yield n, value.to_value().get_value()
        else:
            raise RuntimeError("Namespace %s not known" % name.namespace)

    for rel, sctxt in ctxt.children.items():
        for k, v in get_all_context_values(sctxt):
            yield k, v

# Gets a set of values dict from an iXBRL document.
def get_values(comps):

    # Parse doc
    tree = ET.parse(BytesIO(comps))
    i = parse(tree)

    # Find the period context with the latest end date
    p_ctxt = None
    t = None
    for rel, ctxt, lvl in i.context_iter():
        if isinstance(rel, Period):
            if not t or rel.end > t:
                t = rel.end
                p_ctxt = ctxt

    # Find the instant context with the latest date
    i_ctxt = None
    t = None
    for rel, ctxt, lvl in i.context_iter():
        if isinstance(rel, Instant):
            if not t or rel.instant > t:
                t = rel.instant
                i_ctxt = ctxt

    # Find the entity context
    e_ctxt = None
    for rel, ctxt, lvl in i.context_iter():
        if isinstance(rel, Entity):
            e_ctxt = ctxt

    # Shouldn't happen, only if we were fed an invalid doc
    if not p_ctxt: raise RuntimeError("No period context found.")
    if not i_ctxt: RuntimeError("No instant context found.")
    if not e_ctxt: raise RuntimeError("No entity context found.")

    d = {}

    # Loop over period context and all children, get values
    for k, v in get_all_context_values(p_ctxt):
        d[k] = v

    # Loop over instant context and all children, get values
    for k, v in get_all_context_values(i_ctxt):
        d[k] = v

    # Company number from entity
    d["uk-core:UKCompaniesHouseRegisteredNumber"] = e_ctxt.entity.id

    return d

def to_values(comps):
    return get_values(comps)

def to_return(comps, accts, params, atts):

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

