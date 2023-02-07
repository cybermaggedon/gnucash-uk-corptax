
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
            Computation(40, "Repayments this period"),
            Computation(50, "Making more than one return now"),
            Computation(55, "Estimated figures"),

            60 Company part of a group that is not small
65 Notice of disclosable avoidance schemes
70 Compensating adjustment claimed
75 Company qualifies for SME exemption
80, 85 and 90 Accounts and computations
145 Total turnover from trade
150 Banks, building societies, insurance companies and other financial concerns
155 Trading profits
160 Trading losses brought forward set against trading profits
165 Net trading profits
170 and 172 Bank, building society or other interest, and profits from non-trading loan relationships
175 Annual payments not otherwise charged to Corporation Tax and from which Income Tax has not been deducted
180 Non-exempt dividends or distributions from non-UK resident companies
185 Income from which Income Tax has been deducted
190 Income from a property business
195 Non-trading gains on intangible fixed assets
200 Tonnage Tax profits
205 Income not falling under any other heading
210 Gross chargeable gains
215 Allowable losses including losses brought forward
220 Net chargeable gains
225 Losses brought forward against certain investment income
230 Non-trade deficits on loan relationships (including interest), and derivative contracts (financial instruments) brought forward set against non-trading profits
235 Profits before other deductions and reliefs
240 Losses on unquoted shares
245 Management expenses
250 UK property business losses for this or previous accounting period
255 Capital allowances for the purpose of management of the business
260 Non-trade deficits for this accounting period from loan relationships and derivative contracts (financial instruments)
263 Carried forward non-trade deficits from loan relationships and derivative contracts (financial instruments)
265 Non-trading losses on intangible fixed assets
275 Trading losses of this or a later accounting period
280 Put an X in box 280 if amounts carried back from later accounting periods are included in box 275
285 Trading losses carried forward and claimed against total profits
290 Non-trade capital allowances
295 Total of deductions and reliefs
300 Profits before qualifying donations and group relief
305 Qualifying donations
310 Group relief

312 Group relief for carried forward losses
            
315 Profits chargeable to Corporation Tax
            
320 Ring fence profits included
325 Northern Ireland profits included

Boxes 330 to 425



430 Corporation Tax
435 Marginal relief for ring fence trades
440 Corporation Tax chargeable
       445 Community Investment relief

450 Double Taxation Relief
455 Put an X in box 455 if box 450 includes an underlying Rate relief claim
460 Put an X in box 460 if box 450 includes any amount carried back from a later period
465 Advance Corporation Tax
            
470 Total reliefs and deduction in terms of tax

471 CJRS and Job Support Scheme received
472 CJRS and Job Support Scheme entitlement
473 CJRS overpayment already assessed or voluntary disclosed
        474 Other Coronavirus overpayments


Box 526 Coronavirus support schemes overpayment now due: £8,000

475 Net Corporation Tax liability

480 Tax payable on loans and arrangements to participators

485 Put an X in box 485 if you completed box A70 in the supplementary pages CT600A


490 CFC tax payable
495 Bank Levy payable
            496 Bank surcharge payable
            500 CFC tax and bank Levy payable
            505 Supplementary charge (ring fence trades) payable
510 Tax chargeable
515 Income Tax deducted from gross income included in profits
520 Income Tax repayable to the company

525 Self-assessment of tax payable before restitution tax and coronavirus support scheme overpayments
526 Coronavirus support schemes overpayment now due

527 Restitution tax
528 Self-assessment of tax payable

            530 Research and Development credit
            535
540 Creative tax credit
545 Total of Research and Development credit and creative tax credit
550 Land remediation tax credit

555 Life assurance company tax credit

560 Total land remediation and life assurance company tax credit

       565 Capital allowances first-year tax credit     
570 Surplus Research and Development credits or creative tax credit payable
575 Land remediation or life assurance company tax credit payable

     580 Capital allowances first-year tax credit payable       
585 Ring fence Corporation Tax included and 590 Ring fence supplementary charge included
           586 NI Corporation Tax included
595 Tax already paid (and not already repaid)

600 Tax outstanding

605 Tax overpaid including surplus or payable credits

610 Group tax refunds surrendered to this company
615 Research and Development expenditure credits surrendered to this company

616 Yes — goods
617 Yes — services
618 No — neither

620 Franked investment income/exempt ABGH distributions
625 Number of 51% group companies

630 should have made (whether it has or not) instalment payments as a large company under the Corporation Tax (instalment Payments) Regulations 1998

631 Should have made (whether it has or not) instalment payments as a very large company under the Corporation Tax (instalment Payments) Regulations 1998


635 is within a group payments arrangement for the period

640 has written down or sold intangible assets

645 has made cross-border royalty payments
            
            647 Eat Out to Help Out Scheme: reimbursed discounts included as taxable income

650 Put an X in box 650 if the claim is made by a small or medium-sized enterprise (SME), including a SME subcontractor to a large company

655 Put an X in box 655 if the claim is made by a large company


            660 R&D enhanced expenditure
665 Creative enhanced expenditure

670 R&D and creative enhanced expenditure
675 R&D enhanced expenditure of a SME on work sub contracted to it by a large company

680 Vaccines research expenditure
685 Enter the total enhanced expenditure
            
            690 Annual investment allowance
691 and 692 Machinery and plant — super-deduction

693 and 694 Machinery and plant — special rate allowance
          695 and 700 Machinery and plant — special rate pool
705 and 710 Machinery and plant — main pool

711 Structures and buildings
715 and 720 Business premises renovation
725 and 730 Other allowances and charges
713 and 714 Electric charge points
721 and 722 Enterprise zones

723 and 724 Zero emissions goods vehicles

726 and 727 Zero emissions cars
735 Annual Investment Allowance
            
736 Structures and buildings

740 and 745 Business premises renovation



741 and 742 Machinery and plant — super-deduction
      743 and 744 Machinery and plant — special rate allowance      
           750 and 755 Other allowances and charges
737 and 738 Electric charge points
746 and 747 Enterprise Zones

748 and 749 Zero emissions goods vehicles

751 and 752 Zero emissions cars
         760 Machinery and plant on which first-year allowance is claimed
765 Designated environmentally friendly machinery and plant

770 Machinery and plant on long-life assets and integral features
771 Structures and buildings
772 Machinery and plant — super-deduction

773 Machinery and plant — special rate allowance

775 Other machinery and plant


780 Losses of trades carried on wholly or partly in the UK (amount)
            785 Losses of trades carried on wholly or partly in the UK (maximum available for surrender as group relief)


790 Losses of trades carried on wholly outside the UK (amount)
            
795 Non-trade deficits on loan relationships and derivative contracts (amount)
800 Non-trade deficits on loan relationships and derivative contracts (maximum available for surrender as group relief)

805 UK property business losses (amount)
            
810 UK property business losses (maximum available for surrender as group relief)
815 Overseas property business losses (amount)


            820 Losses from miscellaneous transactions (amount)


825 Capital losses (amount)


830 Non-trading losses on intangible fixed assets (amount)

835 Non-trading losses on intangible fixed assets (maximum available for surrender as group relief)











840 Non-trade capital allowances (maximum available for surrender as group relief)
845 Qualifying donations (maximum available for surrender as group relief)
            
850 Management expenses (amount)855 Management expenses (maximum available for surrender as group relief)


Leave this section (boxes 856 to 858) blank.
860 Small Repayments


            
865 Repayment of Corporation Tax


870 Repayment of Income Tax

875 Payable Research and Development Tax Credit

            
880 Payable research and development expenditure credit
885 Payable creative tax credit

890 Payable land remediation or life assurance company tax credit




895 Payable capital allowances first-year tax credit

            900 The following amount is to be surrendered


            
905 Joint notice is attached
910 Joint notice will follow
            
915 Please stop repayment of the following amount until we send you the Notice
920 Name of bank or building society

925 Branch sort code

930 Account number


935 Name of account



          940 Building society reference

            

            

    945: enter your status, for example company secretary or authorised agent
    950: enter the name of your company
    955: enter the name of the nominated person
    960: enter the address of the nominated person
    965: enter your reference for the nominated person
    970: enter your name
975 Name
980 Date
985 Status
