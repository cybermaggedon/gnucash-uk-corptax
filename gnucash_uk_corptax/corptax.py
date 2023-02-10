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

class CorptaxReturn:
    def __init__(self, comps, accts, form_values, params, atts):
        self.comps = comps
        self.accts = accts
        self.form_values = form_values
        self.params = params
        self.atts = atts

    def box(self, num):
        val = self.form_values["ct600"][num]
        if val is None: return ""
        return val

    def money(self, num):
        val = self.form_values["ct600"][num]
        if val is None: return 0
        return "%.2f" % float(val)

    def date(self, num):
        val = self.form_values["ct600"][num]
        if val is None: return ""
        return str(val)

    def company_info(self):
        return {
            "CompanyName": self.box(1),
            "RegistrationNumber": self.box(2),
            "Reference": self.box(3),
            "CompanyType": self.box(4),
            "PeriodCovered": {
                "From": self.date(30),
                "To": self.date(35),
            }
        }

    def turnover(self):
        return {
            "Total": self.money(145),
        }

    def company_tax_calculation(self):
        return {
            "Income": {
                "Trading": {
                    "Profits": self.money(155),
                    "NetProfits": self.money(165),
                },
            },
            "ChargeableGains": {
                "NetChargeableGains": self.money(220),
            },
            "ProfitsBeforeOtherDeductions": self.money(235),
            "ChargesAndReliefs": {
                "ProfitsBeforeDonationsAndGroupRelief": self.money(300),
            },
            "ChargeableProfits": self.money(315),
            "CorporationTaxChargeable": {
                "FinancialYearOne": {
                    "Year": self.box(330),
                    "Details": {
                        "Profit": self.money(335),
                        "TaxRate": self.money(340),
                        "Tax": self.money(345),
                    }
                },
                "FinancialYearTwo": {
                    "Year": self.box(380),
                    "Details": {
                        "Profit": self.money(385),
                        "TaxRate": self.money(390),
                        "Tax": self.money(395),
                    }
                }
            },
            "CorporationTax": self.money(430),
            "NetCorporationTaxChargeable": self.money(440),
        }

    def return_info(self):
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

    def irheader(self):
        return {
            "Keys": {
                "Key": self.box(3),
            },
            "PeriodEnd": self.date(35),
            "Principal": {
                "Contact": {
                    "Name": {
                        "Ttl": self.params.get("title"),
                        "Fore": self.params.get("first-name"),
                        "Sur": self.params.get("second-name")
                    },
                    "Email": self.params.get("email"),
                    "Telephone": {
                        "Number": self.params.get("phone")
                    }
                }
            },
            "IRmark": "",
            "Sender": "Company"
        }

    def tax_outstanding(self):
        return {
            "NetCorporationTaxLiability": self.money(440),
            "TaxChargeable": self.money(510),
            "TaxPayable": self.money(528),
        }

    def allowances_and_charges(self):
        return {
            "AIACapitalAllowancesInc": self.money(690),
        }

    def declaration(self):
        return {
            "AcceptDeclaration": "yes",
            "Name": self.params.get("declaration-name"),
            "Status": self.params.get("declaration-status")
        }

    def attached_files(self):

        comp_ixbrl = base64.b64encode(self.comps).decode("utf-8")
        accounts_ixbrl = base64.b64encode(self.accts).decode("utf-8")

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
    
    def enhanced_expenditure(self):

        if self.box(670) > 0:
            return {
                "SMEclaim": "yes",
                "RandDEnhancedExpenditure": self.money(660),
                "RandDAndCreativeEnhancedExpenditure": self.money(670),
            }
        else:
            return {}

    def get_return(self):

        ctr = {
            "CompanyInformation": self.company_info(),
            "ReturnInfoSummary": self.return_info(),
            "Turnover": self.turnover(),
            "CompanyTaxCalculation": self.company_tax_calculation(),
            "CalculationOfTaxOutstandingOrOverpaid": self.tax_outstanding(),
            "EnhancedExpenditure": self.enhanced_expenditure(),
            "AllowancesAndCharges": self.allowances_and_charges(),
            "Declaration": self.declaration(),
            "AttachedFiles": self.attached_files()
        }

        ret = {
            "IRenvelope": {
                "IRheader": self.irheader(),
                "CompanyTaxReturn": ctr
            }
        }


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

        # CompanyTaxReturn needs an attribute
        root.find(".//{%s}CompanyTaxReturn[1]" % ct_ns).set(
            "ReturnType", "new"
        )

        # Key needs a UTR type attribute
        root.find(".//{%s}Key[1]" % ct_ns).set(
            "Type", "UTR"
        )

        attf_elt = root.find(".//{%s}AttachedFiles" % ct_ns)

        return ET.ElementTree(root)

