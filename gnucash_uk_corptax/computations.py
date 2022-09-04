
from lxml import etree as ET
from io import BytesIO
import ixbrl_parse.ixbrl
from ixbrl_parse.ixbrl import Period, Instant, Entity, Dimension
from ixbrl_parse.value import *

CT_NS = "http://www.hmrc.gov.uk/schemas/ct/comp/2021-01-01"
CORE_NS = "http://xbrl.frc.org.uk/fr/2021-01-01/core"

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

