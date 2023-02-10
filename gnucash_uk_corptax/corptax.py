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
        return {}

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

        obj = {}

        class Box:
            def __init__(self, id, kind=None):
                self.kind = kind
                self.id = id
            def present(self, obj):
                if self.id in obj.form_values["ct600"]:
                    return True
                return False
            def get(self, obj):
                value = obj.form_values["ct600"][self.id]

                if self.kind == "yesno":
                    return "Yes" if value else "No"

                if self.kind == "yes":
                    return "Yes" if value else "FIXME"

                if self.kind == "date":
                    return str(value)

                if self.kind == "year":
                    return str(value)

                if self.kind == "companytype":
                    return "%02d" % value

                return value

        mapping = {
            "CompanyInformation": {
                "CompanyName": Box(1),
                "RegistrationNumber": Box(2),
                "Reference": Box(3),
                "CompanyType": Box(4, kind="companytype"),
                "NorthernIreland": {
                    "NItradingActivity": Box(5, kind="yesno"),
                    "SME": Box(6, kind="yesno"),
                    "NIemployer": Box(7, kind="yesno"),
                    "SpecialCircumstances": Box(8, kind="yesno"),
                },
                "PeriodCovered": {
                    "From": Box(30, kind="date"),
                    "To": Box(35, kind="date"),
                }
            },
            "ReturnInfoSummary": {
                "ThisPeriod": Box(40, kind="yesno"),
                "EarlierPeriod": Box(45, kind="yesno"),
                "MultipleReturns": Box(50, kind="yesno"),
                "ProvisionalFigures": Box(55, kind="yesno"),
                "PartOfNonSmallGroup": Box(60, kind="yesno"),
                "RegisteredAvoidanceScheme": Box(65, kind="yesno"),
                "TransferPricing": {
                    "Adjustment": Box(70, kind="yesno"),
                    "SME": Box(75, kind="yesno"),
                },
                "Accounts": {
                    "ThisPeriodAccounts": Box(80, kind="yesno"),
                    "DifferentPeriod": Box(85, kind="yesno"),
                    "NoAccountsReason": Box(90),
                },
                "Computations": {
                    "ThisPeriodAccounts": Box(80, kind="yesno"),
                    "DifferentPeriod": Box(85, kind="yesno"),
                    "NoComputationsReason": Box(90),
                },
                "SupplementaryPages": {
                    "CT600A": Box(95, kind="yesno"),
                    "CT600B": Box(100, kind="yesno"),
                    "CT600C": Box(105, kind="yesno"),
                    "CT600D": Box(110, kind="yesno"),
                    "CT600E": Box(115, kind="yesno"),
                    "CT600F": Box(120, kind="yesno"),
                    "CT600G": Box(125, kind="yesno"),
                    "CT600H": Box(130, kind="yesno"),
                    "CT600I": Box(135, kind="yesno"),
                    "CT600J": Box(140, kind="yesno"),
                    "CT600K": Box(141, kind="yesno"),
                    "CT600L": Box(142, kind="yesno"),
                }
            },
            "Turnover": {
                "Total": Box(145),
                "OtherFinancialConcerns": Box(150),
            },
            "CompanyTaxCalculation": {
                "Income": {
                    "Trading": {
                        "Profits": Box(155),
                        "LossesBroughtForward": Box(160),
                        "NetProfits": Box(165),
                        "NonTradingLoanProfitsAndGains": Box(170),
                        "IncomeStatedNet": Box(172, kind="yesno"),
                    },
                    "NonLoanAnnuitiesAnnualPaymentsDiscounts": Box(175),
                    "NonUKdividends": Box(180),
                    "DeductedIncome": Box(185),
                    "PropertyBusinessIncome": Box(190),
                    "NonTradingGainsIntangibles": Box(195),
                    "TonnageTaxProfits": Box(200),
                    "OtherIncome": Box(205),
                },
                "ChargeableGains": {
                    "GrossGains": Box(210),
                    "AllowableLosses": Box(215),
                    "NetChargeableGains": Box(220),
                },
                "LossesBroughtForward": Box(225),
                "NonTradeDeficitsOnLoans": Box(230),
                "ProfitsBeforeOtherDeductions": Box(235),
                "DeductionsAndReliefs": {
                    "UnquotedShares": Box(240),
                    "ManagementExpenses": Box(245),
                    "UKpropertyBusinessLosses": Box(250),
                    "CapitalAllowances": Box(255),
                    "NonTradeDeficits": Box(260),
                    "CarriedForwardNonTradeDeficits": Box(263),
                    "NonTradingLossIntangibles": Box(265),
                    "TradingLosses": Box(275),
                    "TradingLossesCarriedBack": Box(280, kind="yesno"),
                    "TradingLossesCarriedForward": Box(285),
                    "NonTradeCapitalAllowances": Box(290),
                    "Total": Box(295),
                },
                "ChargesAndReliefs": {
                    "ProfitsBeforeDonationsAndGroupRelief": Box(300),
                    "QualifyingDonations": Box(305),
                    "GroupRelief": Box(310),
                    "GroupReliefForCarriedForwardLosses": Box(312),
                },
                "ChargeableProfits": Box(315),
                "RingFenceProfitsIncluded": Box(320),
                "NorthernIrelandProfitsIncluded": Box(325),
                "CorporationTaxChargeable": {
                    "FinancialYearOne": {
                        "Year": Box(330, kind="year"),
                        "Details": [
                            {
                                "Profit": Box(335),
                                "TaxRate": Box(340),
                                "Tax": Box(345)
                            }
                        ]
                    },
                    "FinancialYearTwo": {
                        "Year": Box(380, kind="year"),
                        "Details": [
                            {
                                "Profit": Box(385),
                                "TaxRate": Box(390),
                                "Tax": Box(395)
                            }
                        ]
                    },
                },
                "CorporationTax": {
                    "MarginalReliefForRingFenceTrades": Box(435),
                    "NetCorporationTaxChargeable": Box(440),
                    "TaxReliefsAndDeductions": {
                        "CommunityInvestmentRelief": Box(445),
                        "DoubleTaxation": {
                            "DoubleTaxationRelief": Box(450),
                            "UnderlyingRate": Box(455, kind="yesno"),
                            "AmountCarriedBack": Box(460),
                            "AdvancedCorporationTax": Box(465),
                        },
                        "TotalReliefsAndDeductions": Box(470),
                    },
                    "CJRS": {
                        "CJRSreceived": Box(471),
                        "CJRSdue": Box(472),
                        "CJRSoverpaymentAlreadyAssessed": Box(473),
                        "JobRetentionBonusOverpayment": Box(474),
                    },
                },
            },
            "CalculationOfTaxOutstandingOrOverpaid": {
                "NetCorporationTaxLiability": Box(475),
                "LoansToParticipators": Box(480),
                "CT600AreliefDue": Box(485, kind="yesno"),
                "CFCtaxPayable": Box(490),
                "BankLevyPayable": Box(495),
                "BankSurchargePayable": Box(496),
                "CFCandBankLevyTotal": Box(500),
                "SupplementaryCharge": Box(505),
                "TaxChargeable": Box(510),
                "IncomeTax": {
                    "DeductedIncomeTax": Box(515),
                    "TaxRepayable": Box(520),
                },
                "TaxPayable": Box(525),
                "CJRSoverpaymentsNowDue": Box(526),
                "RestitutionTax": Box(527),
                "TaxPayableIncludingRestitutionTax": Box(528),
            },
            "TaxReconciliation": {
                "ResearchAndDevelopmentCredit": Box(530),
                "VaccineCredit": Box(535),
                "CreativeCredit": Box(540),
                "ResearchAndDevelopmentVaccineOrCreativeTaxCredit":  Box(545),
                "LandRemediationCredit": Box(550),
                "LifeAssuranceCompanyCredit": Box(555),
                "LandOrLifeCredit": Box(560),
                "CapitalAllowancesFirstYearCredit": Box(565),
                "SurplusResearchAndDevelopmentCreditsOrCreativeCreditPayable": Box(570),
                "LandOrLifeCreditPayable": Box(575),
                "CapitalAllowancesFirstYearCreditPayable": Box(580),
                "RingFenceCorpTaxIncluded": Box(585),
                "NIcorporationTaxIncluded": Box(586),
                "RingFenceSupplementaryChargeIncluded": Box(590),
                "TaxAlreadyPaid": Box(595),
                "TaxOutstandingOrOverpaid": {
                    "TaxOutstanding": Box(600),
                    "TaxOverpaid": Box(605),
                },
                "RefundsSurrendered": Box(610),
                "RandDExpenditureCreditsSurrendered": Box(615),
            },
            "IndicatorsAndInformation": {
                "FrankedInvestmentIncome": Box(620),
                "NumberOf51groupCompanies": Box(625),
                "InstalmentPayments": Box(630, kind="yes"),
                "VeryLargeQIPs": Box(631, kind="yes"),
                "GroupPayment": Box(635, kind="yes"),
                "IntangibleAssets": Box(640, kind="yes"),
                "CrossBorderRoyalty": Box(645, kind="yes"),
                "EatOutToHelpOutScheme": Box(647),
            },
            "EnhancedExpenditure": {
                "SMEclaim": Box(650, kind="yes"),
                "LargeCompanyClaim": Box(655, kind="yes"),
                "RandDEnhancedExpenditure": Box(660),
                "CreativeEnhancedExpenditure": Box(665),
                "RandDAndCreativeEnhancedExpenditure": Box(670),
                "SMEclaimAsLargeCompany": Box(675),
                "VaccineResearch": Box(680),
                "LandRemediationEnhancedExpenditure": Box(685),
            },
            "AllowancesAndCharges": {
                "AIACapitalAllowancesInc": Box(690),
                "MachineryAndPlantSpecialRatePool": {
                    "BalancingCharges": Box(695),
                    "CapitalAllowances": Box(700),
                },
                "MachineryAndPlantMainPool": {
                    "BalancingCharges": Box(705),
                    "CapitalAllowances": Box(710),
                },
                "StructuresAndBuildingsCapitalAllowances": Box(711),
                "ElectricChargePoints": {
                    "BalancingCharges": Box(713),
                    "CapitalAllowances": Box(714),
                },
                "BusinessPremisesRenovationIncluded": {
                    "BalancingCharges": Box(715),
                    "CapitalAllowances": Box(720),
                },
                "EnterpriseZones": {
                    "BalancingCharges": Box(721),
                    "CapitalAllowances": Box(722),
                },
                "ZeroEmissionsGoodsVehicles": {
                    "BalancingCharges": Box(723),
                    "CapitalAllowances": Box(724),
                },
                "ZeroEmissionsCars": {
                    "BalancingCharges": Box(726),
                    "CapitalAllowances": Box(727),
                },
                "Others": {
                    "BalancingCharges": Box(725),
                    "CapitalAllowances": Box(730),
                },
            },
            "NotIncluded": {
                "AIACapitalAllowancesNotInc": Box(735),
                "StructuresAndBuildingsCapitalAllowances": Box(736),
                "ElectricChargePoints": {
                    "BalancingCharges": Box(737),
                    "CapitalAllowances": Box(738),
                },
                "BusinessPremisesRenovationIncluded": {
                    "BalancingCharges": Box(740),
                    "CapitalAllowances": Box(745),
                },
                "EnterpriseZones": {
                    "BalancingCharges": Box(746),
                    "CapitalAllowances": Box(747),
                },
                "ZeroEmissionsGoodsVehicles": {
                    "BalancingCharges": Box(748),
                    "CapitalAllowances": Box(749),
                },
                "ZeroEmissionsCars": {
                    "BalancingCharges": Box(751),
                    "CapitalAllowances": Box(752),
                },
                "OtherAllowancesAndCharges": {
                    "BalancingCharges": Box(750),
                    "CapitalAllowances": Box(755),
                },
            },
        }

        def addit(obj, tree):
            for key, value in tree.items():

                if type(value) == dict:
                    if key not in obj:
                        obj[key] = {}
                    addit(obj[key], value)

                if type(value) == Box:
                    if value.present(self):
                        obj[key] = value.get(self)

                if type(value) == list:
                    obj[key] = []
                    for elt in value:
                        obj2 = {}
                        addit(obj2, elt)
                        obj[key].append(obj2)

        addit(obj, mapping)

        return obj

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

        return ctr

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

