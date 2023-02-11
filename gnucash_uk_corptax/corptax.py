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

class InputBundle:

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

    def date(self, num):
        val = self.form_values["ct600"][num]
        if val is None: return ""
        return str(val)

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

    def get_return(self):

        comp_ixbrl = base64.b64encode(self.comps).decode("utf-8")
        accounts_ixbrl = base64.b64encode(self.accts).decode("utf-8")

        class Box:
            def __init__(self, id, kind=None):
                self.kind = kind
                self.id = id

            def present(self, obj):
                if self.id in obj.form_values["ct600"]:

                    value = obj.form_values["ct600"][self.id]
                    if value == None:
                        return False

                    return True

                return False

            def fetch(self, obj):
                return obj.form_values["ct600"][self.id]

            def get(self, obj):
                value = self.fetch(obj)

                if self.kind == "yesno":
                    return "yes" if value else "no"

                if self.kind == "money":
                    return "%.2f" % value

                if self.kind == "pounds":
                    return "%.2f" % int(value)

                if self.kind == "yes":
                    return "yes" if value else "FIXME"

                if self.kind == "date":
                    return str(value)

                if self.kind == "year":
                    return str(value)

                if self.kind == "companytype":
                    return "%02d" % value

                return value

        class Fixed(Box):
            def __init__(self, value, kind=None):
                self.value = value
                self.kind = kind

            def present(self, obj):
                return True

            def fetch(self, obj):
                return self.value


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
                    "ThisPeriodComputations": Box(80, kind="yesno"),
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
                "Total": Box(145, kind="pounds"),
                "OtherFinancialConcerns": Box(150, kind="pounds"),
            },
            "CompanyTaxCalculation": {
                "Income": {
                    "Trading": {
                        "Profits": Box(155, kind="pounds"),
                        "LossesBroughtForward": Box(160, kind="pounds"),
                        "NetProfits": Box(165, kind="pounds"),
                    },
                    "NonTradingLoanProfitsAndGains": Box(170, kind="pounds"),
                    "IncomeStatedNet": Box(172, kind="yesno"),
                    "NonLoanAnnuitiesAnnualPaymentsDiscounts": Box(175, kind="pounds"),
                    "NonUKdividends": Box(180, kind="pounds"),
                    "DeductedIncome": Box(185, kind="pounds"),
                    "PropertyBusinessIncome": Box(190, kind="pounds"),
                    "NonTradingGainsIntangibles": Box(195, kind="pounds"),
                    "TonnageTaxProfits": Box(200, kind="pounds"),
                    "OtherIncome": Box(205, kind="pounds"),
                },
                "ChargeableGains": {
                    "GrossGains": Box(210, kind="pounds"),
                    "AllowableLosses": Box(215, kind="pounds"),
                    "NetChargeableGains": Box(220, kind="pounds"),
                },
                "LossesBroughtForward": Box(225, kind="pounds"),
                "NonTradeDeficitsOnLoans": Box(230, kind="pounds"),
                "ProfitsBeforeOtherDeductions": Box(235, kind="pounds"),
                "DeductionsAndReliefs": {
                    "UnquotedShares": Box(240, kind="pounds"),
                    "ManagementExpenses": Box(245, kind="pounds"),
                    "UKpropertyBusinessLosses": Box(250, kind="pounds"),
                    "CapitalAllowances": Box(255, kind="pounds"),
                    "NonTradeDeficits": Box(260, kind="pounds"),
                    "CarriedForwardNonTradeDeficits": Box(263, kind="pounds"),
                    "NonTradingLossIntangibles": Box(265, kind="pounds"),
                    "TradingLosses": Box(275, kind="pounds"),
                    "TradingLossesCarriedBack": Box(280, kind="yesno"),
                    "TradingLossesCarriedForward": Box(285, kind="pounds"),
                    "NonTradeCapitalAllowances": Box(290, kind="pounds"),
                    "Total": Box(295, kind="pounds"),
                },
                "ChargesAndReliefs": {
                    "ProfitsBeforeDonationsAndGroupRelief": Box(
                        300, kind="pounds"
                    ),
                    "QualifyingDonations": Box(305, kind="pounds"),
                    "GroupRelief": Box(310, kind="pounds"),
                    "GroupReliefForCarriedForwardLosses": Box(312, kind="pounds"),
                },
                "ChargeableProfits": Box(315, kind="pounds"),
                "RingFenceProfitsIncluded": Box(320, kind="pounds"),
                "NorthernIrelandProfitsIncluded": Box(325, kind="pounds"),
                "CorporationTaxChargeable": {
                    "FinancialYearOne": {
                        "Year": Box(330, kind="year"),
                        "Details": {
                            "Profit": Box(335, kind="pounds"),
                            "TaxRate": Box(340, kind="rate"),
                            "Tax": Box(345, kind="money")
                        }
                    },
                    "FinancialYearTwo": {
                        "Year": Box(380, kind="year"),
                        "Details": {
                            "Profit": Box(385, kind="pounds"),
                            "TaxRate": Box(390, kind="rate"),
                            "Tax": Box(395, kind="money")
                        }
                    },
                },
                "CorporationTax": Box(430, kind="money"),
                "MarginalReliefForRingFenceTrades": Box(435, kind="money"),
                "NetCorporationTaxChargeable": Box(440, kind="money"),
                "TaxReliefsAndDeductions": {
                    "CommunityInvestmentRelief": Box(445, kind="money"),
                    "DoubleTaxation": {
                        "DoubleTaxationRelief": Box(450, kind="money"),
                        "UnderlyingRate": Box(455, kind="yesno"),
                        "AmountCarriedBack": Box(460, kind="yes"),
                    },
                    "AdvancedCorporationTax": Box(465, kind="money"),
                    "TotalReliefsAndDeductions": Box(470, kind="money"),
                },
                "CJRS": {
                    "CJRSreceived": Box(471, kind="money"),
                    "CJRSdue": Box(472, kind="money"),
                    "CJRSoverpaymentAlreadyAssessed": Box(473, kind="money"),
                    "JobRetentionBonusOverpayment": Box(474, kind="money"),
                },
            },
            "CalculationOfTaxOutstandingOrOverpaid": {
                "NetCorporationTaxLiability": Box(475, kind="money"),
                "LoansToParticipators": Box(480, kind="money"),
                "CT600AreliefDue": Box(485, kind="yesno"),
                "CFCtaxPayable": Box(490, kind="money"),
                "BankLevyPayable": Box(495, kind="money"),
                "BankSurchargePayable": Box(496, kind="money"),
                "CFCandBankLevyTotal": Box(500, kind="money"),
                "SupplementaryCharge": Box(505, kind="money"),
                "TaxChargeable": Box(510, kind="money"),
                "IncomeTax": {
                    "DeductedIncomeTax": Box(515, kind="money"),
                    "TaxRepayable": Box(520, kind="money"),
                },
                "TaxPayable": Box(525, kind="money"),
                "CJRSoverpaymentsNowDue": Box(526, kind="money"),
                "RestitutionTax": Box(527, kind="money"),
                "TaxPayableIncludingRestitutionTax": Box(528, kind="money"),
            },
            "TaxReconciliation": {
                "ResearchAndDevelopmentCredit": Box(530, kind="money"),
                "VaccineCredit": Box(535, kind="money"),
                "CreativeCredit": Box(540, kind="money"),
                "ResearchAndDevelopmentVaccineOrCreativeTaxCredit":  Box(545, kind="money"),
                "LandRemediationCredit": Box(550, kind="money"),
                "LifeAssuranceCompanyCredit": Box(555, kind="money"),
                "LandOrLifeCredit": Box(560, kind="money"),
                "CapitalAllowancesFirstYearCredit": Box(565, kind="money"),
                "SurplusResearchAndDevelopmentCreditsOrCreativeCreditPayable": Box(570, kind="money"),
                "LandOrLifeCreditPayable": Box(575, kind="money"),
                "CapitalAllowancesFirstYearCreditPayable": Box(580, kind="money"),
                "RingFenceCorpTaxIncluded": Box(585, kind="money"),
                "NIcorporationTaxIncluded": Box(586, kind="money"),
                "RingFenceSupplementaryChargeIncluded": Box(590, kind="money"),
                "TaxAlreadyPaid": Box(595, kind="money"),
                "TaxOutstandingOrOverpaid": {
                    "TaxOutstanding": Box(600, kind="money"),
                    "TaxOverpaid": Box(605, kind="money"),
                },
                "RefundsSurrendered": Box(610, kind="money"),
                "RandDExpenditureCreditsSurrendered": Box(615, kind="money"),
            },
            "IndicatorsAndInformation": {
                "FrankedInvestmentIncome": Box(620, kind="pounds"),
                "NumberOf51groupCompanies": Box(625),
                "InstalmentPayments": Box(630, kind="yes"),
                "VeryLargeQIPs": Box(631, kind="yes"),
                "GroupPayment": Box(635, kind="yes"),
                "IntangibleAssets": Box(640, kind="yes"),
                "CrossBorderRoyalty": Box(645, kind="yes"),
                "EatOutToHelpOutScheme": Box(647, kind="pounds"),
            },
            "EnhancedExpenditure": {
                "SMEclaim": Box(650, kind="yes"),
                "LargeCompanyClaim": Box(655, kind="yes"),
                "RandDEnhancedExpenditure": Box(660, kind="pounds"),
                "CreativeEnhancedExpenditure": Box(665, kind="pounds"),
                "RandDAndCreativeEnhancedExpenditure": Box(670, kind="pounds"),
                "SMEclaimAsLargeCompany": Box(675, kind="pounds"),
                "VaccineResearch": Box(680, kind="pounds"),
            },
            "LandRemediationEnhancedExpenditure": Box(685, kind="pounds"),
            "AllowancesAndCharges": {
                "AIACapitalAllowancesInc": Box(690, kind="pounds"),
                "MachineryAndPlantSpecialRatePool": {
                    "BalancingCharges": Box(695, kind="pounds"),
                    "CapitalAllowances": Box(700, kind="pounds"),
                },
                "MachineryAndPlantMainPool": {
                    "BalancingCharges": Box(705, kind="pounds"),
                    "CapitalAllowances": Box(710, kind="pounds"),
                },
                "StructuresAndBuildingsCapitalAllowances": Box(711, kind="pounds"),
                "ElectricChargePoints": {
                    "BalancingCharges": Box(713, kind="pounds"),
                    "CapitalAllowances": Box(714, kind="pounds"),
                },
                "BusinessPremisesRenovationIncluded": {
                    "BalancingCharges": Box(715, kind="pounds"),
                    "CapitalAllowances": Box(720, kind="pounds"),
                },
                "EnterpriseZones": {
                    "BalancingCharges": Box(721, kind="pounds"),
                    "CapitalAllowances": Box(722, kind="pounds"),
                },
                "ZeroEmissionsGoodsVehicles": {
                    "BalancingCharges": Box(723, kind="pounds"),
                    "CapitalAllowances": Box(724, kind="pounds"),
                },
                "ZeroEmissionsCars": {
                    "BalancingCharges": Box(726, kind="pounds"),
                    "CapitalAllowances": Box(727, kind="pounds"),
                },
                "Others": {
                    "BalancingCharges": Box(725, kind="pounds"),
                    "CapitalAllowances": Box(730, kind="pounds"),
                },
            },
            "NotIncluded": {
                "AIACapitalAllowancesNotInc": Box(735, kind="pounds"),
                "StructuresAndBuildingsCapitalAllowances": Box(736, kind="pounds"),
                "ElectricChargePoints": {
                    "BalancingCharges": Box(737, kind="pounds"),
                    "CapitalAllowances": Box(738, kind="pounds"),
                },
                "BusinessPremisesRenovationNotIncluded": {
                    "BalancingCharges": Box(740, kind="pounds"),
                    "CapitalAllowances": Box(745, kind="pounds"),
                },
                "EnterpriseZones": {
                    "BalancingCharges": Box(746, kind="pounds"),
                    "CapitalAllowances": Box(747, kind="pounds"),
                },
                "ZeroEmissionsGoodsVehicles": {
                    "BalancingCharges": Box(748, kind="pounds"),
                    "CapitalAllowances": Box(749, kind="pounds"),
                },
                "ZeroEmissionsCars": {
                    "BalancingCharges": Box(751, kind="pounds"),
                    "CapitalAllowances": Box(752, kind="pounds"),
                },
                "OtherAllowancesAndCharges": {
                    "BalancingCharges": Box(750, kind="pounds"),
                    "CapitalAllowances": Box(755, kind="pounds"),
                },
            },
            "QualifyingExpenditure": {
                "MachineryAndPlantExpenditure": Box(760, kind="pounds"),
                "DesignatedEnvironmentallyFriendlyMachineryAndPlant": Box(765, kind="pounds"),
                "MachineryAndPlantLongLife": Box(770, kind="pounds"),
                "StructuresAndBuildings": Box(771, kind="pounds"),
                "OtherMachineryAndPlant": Box(775, kind="pounds"),
            },
            "LossesDeficitsAndExcess": {
                "AmountArising": {
                    "LossesOfTradesUK": {
                        "Arising": Box(780, kind="pounds"),
                        "SurrenderMaximum": Box(785, kind="pounds"),
                    },
                    "LossesOfTradesOutsideUK": Box(790, kind="pounds"),
                    "Loans": {
                        "Arising": Box(795, kind="pounds"),
                        "SurrenderMaximum": Box(800, kind="pounds"),
                    },
                    "UKpropertyBusinessLosses": {
                        "Arising": Box(805, kind="pounds"),
                        "SurrenderMaximum": Box(810, kind="pounds"),
                    },
                    "OverseasPropertyBusinessLosses": Box(815, kind="pounds"),
                    "MiscLosses": Box(820, kind="pounds"),
                    "CapitalLosses": Box(825, kind="pounds"),
                    "NonTradingLossesIntangibles": {
                        "Arising": Box(830, kind="pounds"),
                        "SurrenderMaximum": Box(835, kind="pounds"),
                    },
                },
                "ExcessAmounts": {
                    "NonTradeCapital": Box(840, kind="pounds"),
                    "QualifyingDonations": Box(845, kind="pounds"),
                    "ManagementExpenses": {
                        "Arising": Box(850, kind="pounds"),
                        "SurrenderMaximum": Box(855, kind="pounds"),
                    },
                }
            },
            "NorthernIrelandInformation": {
                "NIagainstUK": Box(856, kind="pounds"),
                "NIagainstNI": Box(857, kind="pounds"),
                "UKagainstNI": Box(858, kind="pounds"),
            },
            "OverpaymentsAndRepayments": {
                "OwnRepaymentsLowerLimit": Box(860, kind="pounds"),
                "RepaymentsForThePeriodCoveredByThisReturn": {
                    "CorporationTax": Box(865, kind="money"),
                    "IncomeTax": Box(870, kind="money"),
                    "RandDTaxCredit": Box(875, kind="money"),
                    "RandDExpenditureCredit": Box(880, kind="money"),
                    "CreativeCredit": Box(885, kind="money"),
                    "LandRemediationCredit": Box(890, kind="money"),
                    "PayableCapitalAllowancesFirstYearCredit": Box(895, kind="money"),
                },
                "Surrender": {
                    "Amount": Box(900, kind="money"),
                    "JointNotice": {
                        "Attached": Box(905, kind="yes"),
                        "WillFollow": Box(910, kind="yes"),
                    },
                    "StopUntilNotice": Box(915, kind="money"),
                },
                "BankAccountDetails": {
                    "BankName": Box(920),
                    "SortCode": Box(925),
                    "AccountNumber": Box(930),
                    "AccountName": Box(935),
                    "BuildingSocReference": Box(940),
                    
                },
                "PaymentToPerson": {
                    "Recipient": Box(955),
                    "Address": {

                        # FIXME
                        "Line": Box(960),
                        "Line": "FIXME",

                        # FIXME: AdditionalLine
                        # FIXME: PostCode

                    },
                    "NomineeReference": Box(965),
                },
            },
            "Declaration": {
                "AcceptDeclaration": Fixed("yes"),
                "Name": Box(975),
                "Status": Box(985),
            },
            "AttachedFiles": {
                "XBRLsubmission": {
                    "Computation": {
                        "Instance": {
                            "EncodedInlineXBRLDocument": Fixed(comp_ixbrl),
                        }
                    },
                    "Accounts": {
                        "Instance": {
                            "EncodedInlineXBRLDocument": Fixed(accounts_ixbrl),
                        }
                    }
                }
            }
        }

        def addit(obj, tree):

            for key, value in tree.items():

                if type(value) == dict:

                    obj2 = {}
                    addit(obj2, value)
                    if len(obj2.keys()) > 0:
                        obj[key] = obj2

                elif isinstance(value, Box):
                    if value.present(self):
                        obj[key] = value.get(self)

                elif type(value) == list:
                    obj[key] = []

                    for elt in value:

                        if isinstance(elt, Box):
                            obj[key].append(elt.get(self))
                        else:

                            obj2 = {}
                            addit(obj2, elt)
                            obj[key].append(obj2)

        ctr = {}
        addit(ctr, mapping)

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

