
from lxml import etree as ET
from io import BytesIO
import ixbrl_parse.ixbrl
from ixbrl_parse.ixbrl import Period, Instant, Entity, Dimension
from ixbrl_parse.value import *

CT_NS = "http://www.hmrc.gov.uk/schemas/ct/comp/2021-01-01"
CORE_NS = "http://xbrl.frc.org.uk/fr/2021-01-01/core"

class Computation:
    def __init__(self, box, description):
        self.box = box
        self.description = description
        self.value = None
    def set(self, v):
        self.value = v
        return self

class Computations:

    def __init__(self, comps):
        tree = ET.parse(BytesIO(comps))
        self.ixbrl = ixbrl_parse.ixbrl.parse(tree)

    def get_context(self, ctxt, rel):

        if not rel in ctxt.children:
            raise RuntimeError("No context " + str(rel))

        return ctxt.children[rel]

    def value(self, v):
        return v.to_value().get_value()

    def period_context(self):

        # Find the period context with the latest end date
        p_ctxt = None
        t = None
        for rel, ctxt, lvl in self.ixbrl.context_iter():
            if isinstance(rel, Period):
                if not t or rel.end > t:
                    t = rel.end
                    p_ctxt = ctxt

        if p_ctxt is None:
            raise RuntimeError("Expected to find a period context")

        return p_ctxt

    def instant_context(self):

        # Find the instant context with the latest date
        i_ctxt = None
        t = None
        for rel, ctxt, lvl in self.ixbrl.context_iter():
            if isinstance(rel, Instant):
                if not t or rel.instant > t:
                    t = rel.instant
                    i_ctxt = ctxt

        if i_ctxt is None:
            raise RuntimeError("Expected to find an instant context")

        return i_ctxt

    def entity_context(self):

        # Find the entity context
        e_ctxt = None
        for rel, ctxt, lvl in self.ixbrl.context_iter():
            if isinstance(rel, Entity):
                e_ctxt = ctxt

        if e_ctxt is None:
            raise RuntimeError("Expected to find an entity context")

        return e_ctxt

    def company_instant_context(self):

        ctxt = self.get_context(
            self.instant_context(),
            Dimension(
                ET.QName(CT_NS, "BusinessTypeDimension"),
                ET.QName(CT_NS, "Company")
            )
        )

        return ctxt

    def company_period_context(self):

        ctxt = self.get_context(
            self.period_context(),
            Dimension(
                ET.QName(CT_NS, "BusinessTypeDimension"),
                ET.QName(CT_NS, "Company")
            )
        )

        return ctxt

    def trade_period_context(self):

        ctxt = self.get_context(
            self.period_context(),
            Dimension(
                ET.QName(CT_NS, "BusinessTypeDimension"),
                ET.QName(CT_NS, "Trade")
            )
        )

        ctxt = self.get_context(
            ctxt,
            Dimension(
                ET.QName(CT_NS, "LossReformDimension"),
                ET.QName(CT_NS, "Post-lossReform")
            )
        )

        ctxt = self.get_context(
            ctxt,
            Dimension(
                ET.QName(CT_NS, "TerritoryDimension"),
                ET.QName(CT_NS, "UK")
            )
        )

        return ctxt
    
    def management_expenses_context(self):

        ctxt = self.get_context(
            self.period_context(),
            Dimension(
                ET.QName(CT_NS, "BusinessTypeDimension"),
                ET.QName(CT_NS, "ManagementExpenses")
            )
        )

        return ctxt

    def start(self):
        
        val = self.company_instant_context().values[
            ET.QName(CT_NS, "StartOfPeriodCoveredByReturn")
        ]

        return self.value(val)

    def end(self):
        
        val = self.company_instant_context().values[
            ET.QName(CT_NS, "EndOfPeriodCoveredByReturn")
        ]

        return self.value(val)

    def company_name(self):
        
        val = self.company_instant_context().values[
            ET.QName(CT_NS, "CompanyName")
        ]

        return self.value(val)

    def tax_reference(self):
        
        val = self.company_instant_context().values[
            ET.QName(CT_NS, "TaxReference")
        ]

        return self.value(val)

    def company_number(self):
        
        return self.entity_context().entity.id

    def gross_profit_loss(self):
        
        val = self.period_context().values[
            ET.QName(CORE_NS, "GrossProfitLoss")
        ]

        return self.value(val)

    def turnover_revenue(self):
        
        val = self.period_context().values[
            ET.QName(CORE_NS, "TurnoverRevenue")
        ]

        return self.value(val)

    def adjusted_trading_profit(self):
        
        val = self.company_period_context().values[
            ET.QName(CT_NS, "AdjustedTradingProfitOfThisPeriod")
        ]

        return self.value(val)

    def net_trading_profits(self):
        
        val = self.company_period_context().values[
            ET.QName(CT_NS, "NetTradingProfits")
        ]

        return self.value(val)

    def net_chargeable_gains(self):
        
        val = self.company_period_context().values[
            ET.QName(CT_NS, "NetChargeableGains")
        ]

        return self.value(val)

    def profits_before_other_deductions_and_reliefs(self):
        
        val = self.company_period_context().values[
            ET.QName(CT_NS, "ProfitsBeforeOtherDeductionsAndReliefs")
        ]

        return self.value(val)

    def profits_before_charges_and_group_relief(self):
        
        val = self.company_period_context().values[
            ET.QName(CT_NS, "ProfitsBeforeChargesAndGroupRelief")
        ]

        return self.value(val)

    def total_profits_chargeable_to_corporation_tax(self):
        
        val = self.company_period_context().values[
            ET.QName(CT_NS, "TotalProfitsChargeableToCorporationTax")
        ]

        return self.value(val)

    def fy1(self):
        
        val = self.company_period_context().values[
            ET.QName(CT_NS, "FinancialYear1CoveredByTheReturn")
        ]

        return self.value(val)

    def fy2(self):
        
        val = self.company_period_context().values[
            ET.QName(CT_NS, "FinancialYear2CoveredByTheReturn")
        ]

        return self.value(val)

    def fy1_profit(self):
        
        val = self.company_period_context().values[
            ET.QName(CT_NS, "FY1AmountOfProfitChargeableAtFirstRate")
        ]

        return self.value(val)

    def fy2_profit(self):
        
        val = self.company_period_context().values[
            ET.QName(CT_NS, "FY2AmountOfProfitChargeableAtFirstRate")
        ]

        return self.value(val)

    def fy1_tax_rate(self):
        
        val = self.company_period_context().values[
            ET.QName(CT_NS, "FY1FirstRateOfTax")
        ]

        return self.value(val)

    def fy2_tax_rate(self):
        
        val = self.company_period_context().values[
            ET.QName(CT_NS, "FY2FirstRateOfTax")
        ]

        return self.value(val)

    def fy1_tax(self):
        
        val = self.company_period_context().values[
            ET.QName(CT_NS, "FY1TaxAtFirstRate")
        ]

        return self.value(val)

    def fy2_tax(self):
        
        val = self.company_period_context().values[
            ET.QName(CT_NS, "FY2TaxAtFirstRate")
        ]

        return self.value(val)

    def corporation_tax_chargeable(self):
        
        val = self.company_period_context().values[
            ET.QName(CT_NS, "CorporationTaxChargeable")
        ]

        return self.value(val)

    def tax_chargeable(self):
        
        val = self.company_period_context().values[
            ET.QName(CT_NS, "TaxChargeable")
        ]

        return self.value(val)

    def tax_payable(self):
        
        val = self.company_period_context().values[
            ET.QName(CT_NS, "TaxPayable")
        ]

        return self.value(val)

    def sme_rnd_expenditure_deduction(self):

        val = self.trade_period_context().values[
            ET.QName(CT_NS,
                     "AdjustmentsAdditionalDeductionForQualifyingRDExpenditureSME"
            )
        ]

        return self.value(val)

    def investment_allowance(self):

        val = self.management_expenses_context().values[
            ET.QName(CT_NS,
                     "MainPoolAnnualInvestmentAllowance"
            )
        ]

        return self.value(val)

    def type_of_company(self):
        return "0"

    def repayment(self):
        return False

    def claiming_earlier_period_relief(self):
        return False

    def making_more_than_one_return(self):
        return False

    def estimated_figures(self):
        return False

    def OLDvalues(self):

        return {
            "1": self.company_name(),
            "2": self.company_number(),
            "3": self.tax_reference(),
            "4": self.type_of_company(),
            "30": self.start(),
            "35": self.end(),
            "40": self.repayment(),            
            "50": self.making_more_than_one_return(),
            "55": self.estimated_figures(),
        }

    def values(self):
        return [
            Computation(1, "Company name").set(self.company_name()),
            Computation(2, "Company registration number").set(
                self.company_number()
            ),
            Computation(3, "Tax reference").set(self.tax_reference()),
            Computation(4, "Type of company").set(self.type_of_company()),
            Computation(30, "Start of return").set(self.start()),
            Computation(35, "End of return").set(self.end()),
            Computation(40, "Repayments this period").set(False),
            Computation(50, "Making more than one return now"),
            Computation(55, "Estimated figures"),
            Computation(60, "Company part of a group that is not small"),
            Computation(65, "Notice of disclosable avoidance schemes"),
            Computation(70, "Compensating adjustment claimed"),
            Computation(75, "Company qualifies for SME exemption"),
            Computation(
                80, "Attached accounts and computations for this period"
            ).set(True),
            Computation(
                85, "Attached accounts and computations for a different period"
            ),
            Computation(90, "Reason for not attaching accounts"),
            Computation(95, "CT600A - Loans and arrangements"),
            Computation(100, "CT600B - Controlled foreign companies"),
            Computation(105, "CT600C - Group & consortium"),
            Computation(110, "CT600D - Insurance"),
            Computation(115, "CT600E - CASCs"),
            Computation(120, "CT600F - Tonnage tax"),
            Computation(125, "CT600G - Northern Ireland"),
            Computation(130, "CT600H - Cross-border royalties"),
            Computation(135, "CT600I - Ring fence trades"),
            Computation(140, "CT600J - Tax avoidance schemes"),
            Computation(141, "CT600K - Restitution"),
            Computation(142, "CT600L - R&D"),
            Computation(143, "CT600M - Freeports"),
            Computation(145, "Total turnover from trade").set(
                self.turnover_revenue()
            ),
            Computation(150, "Banks and other financial concerns"),
            Computation(155, "Trading profits").set(
                self.net_trading_profits()
            ),
            Computation(160, "Trading losses brought forward against profits"),
            Computation(165, "Net trading profits").set(
                self.net_trading_profits()
            ),
            Computation(170, "Bank, building society or other interest, and profits from non-trading loan relationships"),
            Computation(172, "Box 170 net of carrying back deficit"),
            Computation(175, "Annual payments not otherwise charged to Corporation Tax and from which Income Tax has not been deducted"),
            Computation(180, "Non-exempt dividends or distributions from non-UK resident companies"),
            Computation(185, "Income from which Income Tax has been deducted"),
            Computation(190, "Income from a property business"),
            Computation(195, "Non-trading gains on intangible fixed assets"),
            Computation(200, "Tonnage Tax profits"),
            Computation(205, "Income not falling under any other heading"),
            Computation(210, "Gross chargeable gains"),
            Computation(215, "Allowable losses including losses brought forward"),
            Computation(220, "Net chargeable gains"),
            Computation(225, "Losses brought forward against certain investment income"),
            Computation(230, "Non-trade deficits on loan relationships (including interest), and derivative contracts (financial instruments) brought forward set against non-trading profits"),
            Computation(235, "Profits before other deductions and reliefs").set(
                self.profits_before_other_deductions_and_reliefs()
            ),
            Computation(240, "Losses on unquoted shares"),
            Computation(245, "Management expenses"),
            Computation(250, "UK property business losses for this or previous accounting period"),
            Computation(255, "Capital allowances for the purpose of management of the business"),
            Computation(260, "Non-trade deficits for this accounting period from loan relationships and derivative contracts (financial instruments)"),
            Computation(263, "Carried forward non-trade deficits from loan relationships and derivative contracts (financial instruments)"),
            Computation(265, "Non-trading losses on intangible fixed assets"),
            Computation(275, "Trading losses of this or a later accounting period"),
            Computation(280, "Put an X in box 280 if amounts carried back from later accounting periods are included in box 275"),
            Computation(285, "Trading losses carried forward and claimed against total profits"),
            Computation(290, "Non-trade capital allowances"),
            Computation(295, "Total of deductions and reliefs"),
            Computation(
                300, "Profits before qualifying donations and group relief"
            ).set(
                self.profits_before_charges_and_group_relief()
            ),
            Computation(305, "Qualifying donations"),
            Computation(310, "Group relief"),
            Computation(312, "Group relief for carried forward losses"),
            Computation(315, "Profits chargeable to Corporation Tax").set(
                self.total_profits_chargeable_to_corporation_tax()
            ),
            Computation(320, "Ring fence profits included"),
            Computation(325, "Northern Ireland profits included"),
            Computation(330, "FY1").set(self.fy1()),
            Computation(335, "FY1 Profit 1").set(self.fy1_profit()),
            Computation(340, "FY1 Rate of Tax 1").set(self.fy1_tax_rate()),
            Computation(345, "FY1 Tax 1").set(self.fy1_tax()),
            Computation(350, "FY1 Profit 2"),
            Computation(355, "FY1 Rate of Tax 2"),
            Computation(360, "FY1 Tax 2"),
            Computation(365, "FY1 Profit 3"),
            Computation(370, "FY1 Rate of Tax 3"),
            Computation(375, "FY1 Tax 3"),
            Computation(380, "FY2").set(self.fy2()),
            Computation(385, "FY2 Profit 1").set(self.fy2_profit()),
            Computation(390, "FY2 Rate of Tax 1").set(self.fy2_tax_rate()),
            Computation(395, "FY2 Tax 1").set(self.fy2_tax()),
            Computation(400, "FY2 Profit 2"),
            Computation(405, "FY2 Rate of Tax 2"),
            Computation(410, "FY2 Tax 2"),
            Computation(415, "FY2 Profit 3"),
            Computation(420, "FY2 Rate of Tax 3"),
            Computation(425, "FY2 Tax 3"),
            Computation(430, "Corporation Tax").set(
                self.corporation_tax_chargeable()
            ),
            Computation(435, "Marginal relief for ring fence trades"),
            Computation(440, "Corporation Tax chargeable").set(
                self.corporation_tax_chargeable()
            ),
            Computation(445, "Community Investment relief"),
            Computation(450, "Double Taxation Relief"),
            Computation(455, "Put an X in box 455 if box 450 includes an underlying Rate relief claim"),
            Computation(460, "Put an X in box 460 if box 450 includes any amount carried back from a later period"),
            Computation(465, "Advance Corporation Tax"),
            Computation(470, "Total reliefs and deduction in terms of tax"),
            Computation(471, "CJRS and Job Support Scheme received"),
            Computation(472, "CJRS and Job Support Scheme entitlement"),
            Computation(473, "CJRS overpayment already assessed or voluntary disclosed"),
            Computation(474, "Other Coronavirus overpayments"),
            Computation(475, "Net Corporation Tax liability").set(
                self.corporation_tax_chargeable()
            ),
            Computation(480, "Tax payable on loans and arrangements to participators"),
            Computation(485, "Put an X in box 485 if you completed box A70 in the supplementary pages CT600A"),
            Computation(490, "CFC tax payable"),
            Computation(495, "Bank Levy payable"),
            Computation(496, "Bank surcharge payable"),
            Computation(500, "CFC tax and bank Levy payable"),
            Computation(505, "Supplementary charge (ring fence trades) payable"),
            Computation(510, "Tax chargeable").set(
                self.tax_chargeable()
            ),
            Computation(515, "Income Tax deducted from gross income included in profits"),
            Computation(520, "Income Tax repayable to the company"),
            Computation(525, "Self-assessment of tax payable before restitution tax and coronavirus support scheme overpayments"),
            Computation(526, "Coronavirus support schemes overpayment now due"),
            Computation(527, "Restitution tax"),
            Computation(528, "Self-assessment of tax payable").set(
                self.tax_payable()
            ),
            Computation(530, "Research and Development credit")
            #.set(
#                self.sme_rnd_expenditure_deduction()
            #)
            ,
            Computation(535, "Not currently used"),
            Computation(540, "Creative tax credit"),
            Computation(
                545, "Total of R&D credit and creative tax credit"
            ),
            Computation(550, "Land remediation tax credit"),
            Computation(555, "Life assurance company tax credit"),
            Computation(560, "Total land remediation and life assurance company tax credit"),
            Computation(565, "Capital allowances first-year tax credit"),
            Computation(570, "Surplus Research and Development credits or creative tax credit payable"),
            Computation(575, "Land remediation or life assurance company tax credit payable"),
            Computation(580, "Capital allowances first-year tax credit payable       "),
            Computation(585, "Ring fence Corporation Tax included and 590 Ring fence supplementary charge included"),
            Computation(586, "NI Corporation Tax included"),
            Computation(595, "Tax already paid (and not already repaid)"),
            Computation(600, "Tax outstanding"),
            Computation(605, "Tax overpaid including surplus or payable credits"),
            Computation(610, "Group tax refunds surrendered to this company"),
            Computation(615, "Research and Development expenditure credits surrendered to this company"),
            Computation(616, "Export: Yes — goods"),
            Computation(617, "Export: Yes — services"),
            Computation(618, "Export: No — neither"),
            Computation(620, "Franked investment income/exempt ABGH distributions"),
            Computation(625, "Number of 51% group companies"),
            Computation(630, "should have made (whether it has or not) instalment payments as a large company under the Corporation Tax (instalment Payments) Regulations 1998"),
            Computation(631, "Should have made (whether it has or not) instalment payments as a very large company under the Corporation Tax (instalment Payments) Regulations 1998"),
            Computation(635, "is within a group payments arrangement for the period"),
            Computation(640, "has written down or sold intangible assets"),
            Computation(645, "has made cross-border royalty payments"),
            Computation(647, "Eat Out to Help Out Scheme: reimbursed discounts included as taxable income"),
            Computation(650, "Put an X in box 650 if the claim is made by a small or medium-sized enterprise (SME), including a SME subcontractor to a large company").set(True),
            Computation(655, "Put an X in box 655 if the claim is made by a large company"),
            Computation(660, "R&D enhanced expenditure").set(
                self.sme_rnd_expenditure_deduction()
            ),
            Computation(665, "Creative enhanced expenditure"),
            Computation(670, "R&D and creative enhanced expenditure").set(
                self.sme_rnd_expenditure_deduction()
            ),
            Computation(675, "R&D enhanced expenditure of a SME on work sub contracted to it by a large company"),
            Computation(680, "Vaccines research expenditure"),
            Computation(685, "Enter the total enhanced expenditure"),
            Computation(690, "Annual investment allowance").set(
                self.investment_allowance()
            ),
            Computation(691, "Machinery/plant super-deduction — Capital allowances"),
            Computation(692, "Machinery/plant super-deduction — Balancing charges"),
            Computation(693, "Machinery and plant — special rate allowance — Capital allowances"),
            Computation(694, "Machinery and plant — special rate allowance — Balancing charges"),

            Computation(695, "Machinery and plant — special rate pool - Capital allowance"),
            Computation(700, "Machinery and plant — special rate pool - Balancing charges"),

            Computation(705, "Machinery and plant — main pool - Capital allowance"),
            Computation(710, "Machinery and plant — main pool - Balancing charges"),
            Computation(711, "Structures and buildings - Capital allowances"),
            Computation(715, "Business premises renovation - Capital allowances"),
            Computation(720, "Business premises renovation - Balancing charges"),
            Computation(725, "Other allowances and charges - Capital allowances"),
            Computation(730, "Other allowances and charges - Balancing charges"),
            Computation(713, "Electric charge points - Capital allowances"),
            Computation(714, "Electric charge points - Balancing charges"),
            Computation(721, "Enterprise zones - Capital allowances"),
            Computation(722, "Enterprise zones - Balancing charges"),
            Computation(723, "Zero emissions goods vehicles - Capital allowances"),
            Computation(724, "Zero emissions goods vehicles - Balancing charges"),
            Computation(726, "Zero emissions cars - Capital allowances"),
            Computation(727, "Zero emissions cars - Balancing charges"),

            # Not included:
            Computation(735, "Annual Investment Allowance - Capital allowances"),
            
            Computation(736, "Structures and buildings"),
            Computation(740, "Business premises renovation - Capital allowances"),
            Computation(745, "Business premises renovation - Balancing charges"),

            Computation(741, "Machinery and plant — super-deduction - Capital allowances"),
            Computation(742, "Machinery and plant — super-deduction - Balancing charges"),
            Computation(743, "Machinery and plant — special rate allowance - Capital allowances"),
            Computation(744, "Machinery and plant — special rate allowance - Balancing charges"),
            Computation(750, "Other allowances and charges - Capital allowances"),
            Computation(755, "Other allowances and charges - Balancing charges"),
            Computation(737, "Electric charge points - Capital allowances"),
            Computation(738, "Electric charge points - Balancing charges"),

            Computation(746, "Enterprise Zones - Capital allowances"),
            Computation(747, "Enterprise Zones - Balancing charges"),

            Computation(748, "Zero emissions goods vehicles - Capital allowances"),
            Computation(749, "Zero emissions goods vehicles - Balancing charges"),
            Computation(751, "Zero emissions cars - Capital allowances"),
            Computation(752, "Zero emissions cars - Balancing charges"),

            # Qualifying expenditure
            Computation(760, "Machinery and plant on which first-year allowance is claimed"),
            Computation(765, "Designated environmentally friendly machinery and plant"),
            Computation(770, "Machinery and plant on long-life assets and integral features"),
            Computation(771, "Structures and buildings"),
            Computation(772, "Machinery and plant — super-deduction"),
            Computation(773, "Machinery and plant — special rate allowance"),
            Computation(775, "Other machinery and plant"),

            # Losses, deficits, excess amounts
            Computation(
                780, "Losses of trades carried on wholly or partly in the UK"
            ),
            Computation(785, "Losses of trades carried on wholly or partly in the UK (maximum available for surrender as group relief)"),
            Computation(790, "Losses of trades carried on wholly outside the UK (amount)"),
            Computation(795, "Non-trade deficits on loan relationships and derivative contracts (amount)"),
            Computation(800, "Non-trade deficits on loan relationships and derivative contracts (maximum available for surrender as group relief)"),
            Computation(805, "UK property business losses (amount)"),
            Computation(810, "UK property business losses (maximum available for surrender as group relief)"),
            Computation(815, "Overseas property business losses (amount)"),
            Computation(820, "Losses from miscellaneous transactions (amount)"),
            Computation(825, "Capital losses (amount)"),
            Computation(830, "Non-trading losses on intangible fixed assets (amount)"),
            Computation(835, "Non-trading losses on intangible fixed assets (maximum available for surrender as group relief)"),
            Computation(840, "Non-trade capital allowances (maximum available for surrender as group relief)"),
            Computation(845, "Qualifying donations (maximum available for surrender as group relief)"),
            Computation(850, "Management expenses (amount)855 Management expenses (maximum available for surrender as group relief)"),

            # Northern Ireland, leave blank
            Computation(856, "Amount of group relief claimed which relates to NI trading losses used against rest of UK/mainstream profits"),
            Computation(857, "Amount of group relief claimed which relates to NI trading losses used against NI trading profits"),
            Computation(858, "Amount of group relief claimed which relates to rest of UK/mainstream losses used against NI trading profits"),
            Computation(860, "Small Repayments"),
            Computation(865, "Repayment of Corporation Tax"),
            Computation(870, "Repayment of Income Tax"),
            Computation(875, "Payable Research and Development Tax Credit"),
            Computation(880, "Payable research and development expenditure credit"),
            Computation(885, "Payable creative tax credit"),
            Computation(890, "Payable land remediation or life assurance company tax credit"),
            Computation(895, "Payable capital allowances first-year tax credit"),
            Computation(900, "The following amount is to be surrendered"),
            Computation(905, "Joint notice is attached"),
            Computation(910, "Joint notice will follow"),
            Computation(915, "Please stop repayment of the following amount until we send you the Notice"),
            Computation(920, "Name of bank or building society"),
            Computation(925, "Branch sort code"),
            Computation(930, "Account number"),
            Computation(935, "Name of account"),
            Computation(940, "Building society reference"),
            Computation(945, "enter your status, for example company secretary or authorised agent"),
            Computation(950, "enter the name of your company"),
            Computation(955, "enter the name of the nominated person"),
            Computation(960, "enter the address of the nominated person"),
            Computation(965, "enter your reference for the nominated person"),
            Computation(970, "enter your name"),
            Computation(975, "Name"),
            Computation(980, "Date"),
            Computation(985, "Status"),
        ]

