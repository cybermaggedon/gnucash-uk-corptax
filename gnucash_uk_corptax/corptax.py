#!/usr/bin/env python3

from lxml import etree as ET
import base64
from gnucash_uk_corptax.computations import Computations

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
def get_comps(comps):
    c = Computations(comps)
    return c

def to_values(comps):

    c = get_comps(comps)

    values = c.values()
    return values

    return {
        "start": c.start(),
        "end": c.end(),
        "company_name": c.company_name(),
        "tax_reference": c.tax_reference(),
        "company_number": c.company_number(),
        "gross_profit_loss": c.net_trading_profits(),
        "turnover_revenue": c.turnover_revenue(),
        "adjusted_trading_profit": c.adjusted_trading_profit(),
        "net_trading_profits": c.net_trading_profits(),
        "net_chargeable_gains": c.net_chargeable_gains(),
        "profits_before__deductions_and_reliefs": c.profits_before_other_deductions_and_reliefs(),
        "profits_before_charges_and_group_relief": c.profits_before_charges_and_group_relief(),
        "total_profits_chargeable_to_corporation_tax": c.total_profits_chargeable_to_corporation_tax(),
        "fy1": c.fy1(),
        "fy2": c.fy2(),
        "fy1_profit": c.fy1_profit(),
        "fy2_profit": c.fy2_profit(),
        "fy1_tax_rate": c.fy1_tax_rate(),
        "fy2_tax_rate": c.fy2_tax_rate(),
        "fy1_tax": c.fy1_tax(),
        "fy2_tax": c.fy2_tax(),
        "corporation_tax_chargeable": c.corporation_tax_chargeable(),
        "tax_chargeable": c.tax_chargeable(),
        "tax_payable": c.tax_payable(),
        "sme_rnd_expenditure_deduction": c.sme_rnd_expenditure_deduction(),
        "investment_allowance": c.investment_allowance(),
    }
    
def company_info(params, x):
    return {
        "CompanyName": x.company_name(),
        "RegistrationNumber": x.company_number(),
        "Reference": x.tax_reference(),
        "CompanyType": params.get("company-type"),
        "PeriodCovered": {
            "From": to_date(x.start()),
            "To": to_date(x.end()),
        }
    }

def return_info(x):
    return {
        "ThisPeriod": "yes",
        "Accounts": {
            "ThisPeriodAccounts": "yes"
        },
        "Computations": {
            "ThisPeriodComputations": "yes"
        },
        "SupplementaryPages": {
        }
    }

def company_tax_calculation(x):
    return {
        "Income": {
            "Trading": {
                "Profits": to_money(x.adjusted_trading_profit()),
                "NetProfits": to_money(x.net_trading_profits()),
            },
        },
        "ChargeableGains": {
            "NetChargeableGains": to_money(x.net_chargeable_gains()),
        },
        "ProfitsBeforeOtherDeductions": to_money(x.profits_before_other_deductions_and_reliefs()),
        "ChargesAndReliefs": {
            "ProfitsBeforeDonationsAndGroupRelief": to_money(x.profits_before_charges_and_group_relief()),
        },
        "ChargeableProfits": to_money(x.total_profits_chargeable_to_corporation_tax()),
        "CorporationTaxChargeable": {
            "FinancialYearOne": {
                "Year": x.fy1(),
                "Details": {
                    "Profit": to_money(x.fy1_profit()),
                    "TaxRate": to_money(x.fy1_tax_rate()),
                    "Tax": to_money(x.fy1_tax()),
                }
            },
            "FinancialYearTwo": {
                "Year": x.fy2(),
                "Details": {
                    "Profit": to_money(x.fy2_profit()),
                    "TaxRate": to_money(x.fy2_tax_rate()),
                    "Tax": to_money(x.fy2_tax()),
                }
            }
        },
        "CorporationTax": to_money(x.corporation_tax_chargeable()),
        "NetCorporationTaxChargeable": to_money(x.corporation_tax_chargeable()),
    }

def tax_outstanding(x):
    return {
        "NetCorporationTaxLiability": to_money(x.corporation_tax_chargeable()),
        "TaxChargeable": to_money(x.tax_chargeable()),
        "TaxPayable": to_money(x.tax_payable()),
    }

def attached_files(comps, accts):

    comp_ixbrl = base64.b64encode(comps).decode("utf-8")
    accounts_ixbrl = base64.b64encode(accts).decode("utf-8")

    return {
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

def turnover(x):
    return {
        "Total": to_money(x.turnover_revenue()),
    }

def allowances_and_charges(x):
    return {
        "AIACapitalAllowancesInc": to_money(x.investment_allowance()),
    }

def declaration(params):
    return {
        "AcceptDeclaration": "yes",
        "Name": params.get("declaration-name"),
        "Status": params.get("declaration-status")
    }

def company_tax_return(params, x, comps, accts):
    return {
        "CompanyInformation": company_info(params, x),
        "ReturnInfoSummary": return_info(x),
        "Turnover": turnover(x),
        "CompanyTaxCalculation": company_tax_calculation(x),
        "CalculationOfTaxOutstandingOrOverpaid": tax_outstanding(x),    
        "EnhancedExpenditure": {},
        "AllowancesAndCharges": allowances_and_charges(x),
        "Declaration": declaration(params),
        "AttachedFiles": attached_files(comps, accts)
    }

def irheader(params, x):
    return {
        "Keys": {
            "Key": x.tax_reference(),
        },
        "PeriodEnd": to_date(x.end()),
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
    }

def enhanced_expenditure(x):
    rnd = x.sme_rnd_expenditure_deduction()
    return {
        "SMEclaim": "yes",
        "RandDEnhancedExpenditure": to_money(rnd),
        "RandDAndCreativeEnhancedExpenditure": to_money(rnd),
    }        

def to_return(comps, accts, params, atts):

    x = get_comps(comps)

    cret = company_tax_return(params, x, comps, accts)

    rnd = x.sme_rnd_expenditure_deduction()
    if rnd > 0:
        cret["EnhancedExpenditure"] = enhanced_expenditure(x)

    ret = {
        "IRenvelope": {
            "IRheader": irheader(params, x),
            "CompanyTaxReturn": cret
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

