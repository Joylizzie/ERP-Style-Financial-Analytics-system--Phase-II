/* 1.This function retrieve all transanctions from je, ar_invoice_item, ar_receipt_item,ap_invoice_item, ap_payment_item
   2. Can be filtered by company_code, general_ledger_number, start_date, end_date
  
*/
set search_path to ocean_stream;

drop function if exists func_trans_lst_detail(char(5),integer, integer,  integer,  date, date);

create or replace function func_trans_lst_detail(
                company_code_p char(5), 
                general_ledger_number_sp integer,
                general_ledger_number_ep integer, 
                currency_id integer,
                start_date_p date, 
                end_date_p date) 
   returns table(company_code char(6),
                entry_type_id char(3),
				        entry_id integer,
                t_date date,
                general_ledger_number integer,
                revenue_cost varchar(40),
                cost_centre char(5),
                wbs_code char(5),
                profit_centre varchar(30),
                debit_credit varchar(6),
                currency_id integer,
                amount numeric)
as
 $$
  -- select tmp3.company_code, 
  --        tmp3.revenue_cost,
  --        tmp3.profit_centre_name,
  --        tmp3.currency_id,         
  --        sum(amount) 
  -- from (
    (select tmp1.company_code, 
           tmp1.entry_type_id,
           tmp1.entry_id,
           tmp1.t_date,
           tmp1.general_ledger_number,
           sub.sub_coacat_name as revenue_cost,
           tmp1.cost_centre,
           tmp1.wbs_code,
           pc.pc_name as profit_centre_name,
           tmp1.debit_credit,
           tmp1.currency_id,
           tmp1.amount
    from
        (
        select je.company_code, 
		        je.entry_type_id, 
		        je.je_id as entry_id,
		        jei.transaction_date as t_date,
		        jei.general_ledger_number,
		        jei.cc_id as cost_centre,
		        jei.wbs_code,
		        jei.debit_credit,
		        jei.currency_id,
		        jei.amount
        from journal_entry_item jei
        inner join journal_entry je
        on je.je_id = jei.je_id
        where je.company_code = company_code_p
            and jei.transaction_date between start_date_p and end_date_p
            and jei.general_ledger_number between general_ledger_number_sp and general_ledger_number_ep
        -- double entries from ar_invoice
        union all
        select ar.company_code, 
		        ar.entry_type_id,
		        ar.rie_id as entry_id,
		        ar.date as t_date,
		        aii.general_ledger_number,
		        aii.cc_id as cost_centre,
		        ''::char(5) as wbs_code,
		        aii.debit_credit,
		        aii.currency_id,
		        aii.amount	
        from ar_invoice as ar
        inner join ar_invoice_item aii
        on ar.rie_id = aii.rie_id
        where ar.company_code = company_code_p
          and aii.general_ledger_number between general_ledger_number_sp and general_ledger_number_ep
          and ar.date between start_date_p and end_date_p
        -- double entries from ar_receipt
        union all
        select arr.company_code,
		        arr.entry_type_id,
		        arr.rre_id as entry_id,
		        arr.date as t_date,
		        ari.general_ledger_number,
		        ''::char(6) cost_centre,
		        ''::char(5)	wbs_code,
		        ari.debit_credit,
		        ari.currency_id,
		        ari.amount
        from ar_receipt arr
        inner join ar_receipt_item ari
        on arr.rre_id = ari.rre_id
        where arr.company_code = company_code_p
         and ari.general_ledger_number between general_ledger_number_sp and general_ledger_number_ep
         and arr.date between start_date_p and end_date_p
        -- double entries from ap_invoice
        union all
        select ap.company_code,
		        ap.entry_type_id,
		        ap.pie_id as entry_id,
		        ap.date as t_date,
		        api.general_ledger_number,
		        api.cc_id as cost_centre,
		        api.wbs_code,
		        api.debit_credit,
		        api.currency_id,
		        api.amount
        from ap_invoice as ap
        inner join ap_invoice_item as api
        on ap.pie_id = api.pie_id
        where ap.company_code = company_code_p
          and api.general_ledger_number between general_ledger_number_sp and general_ledger_number_ep
          and ap.date between start_date_p and end_date_p
        -- double entries from ap_payment
        union all
        select app.company_code,
		        app.entry_type_id,
		        app.ppe_id,
		        app.date as t_date,
		        appi.general_ledger_number,
		        ''::char(6) cost_centre,
		        ''::char(5)	wbs_code,
		        appi.debit_credit,
		        appi.currency_id,
		        appi.amount
        from ap_payment as app
        inner join ap_payment_item as appi
        on app.ppe_id = appi.ppe_id
        where app.company_code = company_code_p
         and appi.general_ledger_number between general_ledger_number_sp and general_ledger_number_ep
         and app.date between start_date_p and end_date_p
        ) tmp1
    inner join cost_centres ccs
    on tmp1.cost_centre = ccs.cc_id
    inner join chart_of_accounts coa 
    on tmp1.general_ledger_number = coa.general_ledger_number
    inner join sub_coa_categories sub
    on coa.sub_coacat_id = sub.sub_coacat_id
    inner join profit_centres pc
    on pc.pc_id = ccs.pc_id
	order by tmp1.entry_type_id, tmp1.entry_id, tmp1.debit_credit)
  union all
    (select tmp2.company_code, 
           tmp2.entry_type_id,
           tmp2.entry_id,
           tmp2.t_date,
           tmp2.general_ledger_number,
           sub.sub_coacat_name as revenue_cost,
           tmp2.cost_centre,
           tmp2.wbs_code,
           pc.pc_name as profit_centre_name,
           tmp2.debit_credit,
           tmp2.currency_id,
           tmp2.amount
    from
        (
        select je.company_code, 
		        je.entry_type_id, 
		        je.je_id as entry_id,
		        jei.transaction_date as t_date,
		        jei.general_ledger_number,
		        jei.cc_id as cost_centre,
		        jei.wbs_code,
		        jei.debit_credit,
		        jei.currency_id,
		        jei.amount
        from journal_entry_item jei
        inner join journal_entry je
        on je.je_id = jei.je_id
        where je.company_code = company_code_p
            and jei.transaction_date between start_date_p and end_date_p
            and jei.general_ledger_number between general_ledger_number_sp and general_ledger_number_ep
        -- double entries from ar_invoice
        union all
        select ar.company_code, 
		        ar.entry_type_id,
		        ar.rie_id as entry_id,
		        ar.date as t_date,
		        aii.general_ledger_number,
		        aii.cc_id as cost_centre,
		        ''::char(5) as wbs_code,
		        aii.debit_credit,
		        aii.currency_id,
		        aii.amount	
        from ar_invoice as ar
        inner join ar_invoice_item aii
        on ar.rie_id = aii.rie_id
        where ar.company_code = company_code_p
          and aii.general_ledger_number between general_ledger_number_sp and general_ledger_number_ep
          and ar.date between start_date_p and end_date_p
        -- double entries from ar_receipt
        union all
        select arr.company_code,
		        arr.entry_type_id,
		        arr.rre_id as entry_id,
		        arr.date as t_date,
		        ari.general_ledger_number,
		        ''::char(6) cost_centre,
		        ''::char(5)	wbs_code,
		        ari.debit_credit,
		        ari.currency_id,
		        ari.amount
        from ar_receipt arr
        inner join ar_receipt_item ari
        on arr.rre_id = ari.rre_id
        where arr.company_code = company_code_p
         and ari.general_ledger_number between general_ledger_number_sp and general_ledger_number_ep
         and arr.date between start_date_p and end_date_p
        -- double entries from ap_invoice
        union all
        select ap.company_code,
		        ap.entry_type_id,
		        ap.pie_id as entry_id,
		        ap.date as t_date,
		        api.general_ledger_number,
		        api.cc_id as cost_centre,
		        api.wbs_code,
		        api.debit_credit,
		        api.currency_id,
		        api.amount
        from ap_invoice as ap
        inner join ap_invoice_item as api
        on ap.pie_id = api.pie_id
        where ap.company_code = company_code_p
          and api.general_ledger_number between general_ledger_number_sp and general_ledger_number_ep
          and ap.date between start_date_p and end_date_p
        -- double entries from ap_payment
        union all
        select app.company_code,
		        app.entry_type_id,
		        app.ppe_id,
		        app.date as t_date,
		        appi.general_ledger_number,
		        ''::char(6) cost_centre,
		        ''::char(5)	wbs_code,
		        appi.debit_credit,
		        appi.currency_id,
		        appi.amount
        from ap_payment as app
        inner join ap_payment_item as appi
        on app.ppe_id = appi.ppe_id
        where app.company_code = company_code_p
         and appi.general_ledger_number between general_ledger_number_sp and general_ledger_number_ep
         and app.date between start_date_p and end_date_p
        ) tmp2
    inner join wbs
    on tmp2.wbs_code = wbs.wbs_code
    inner join chart_of_accounts coa 
    on tmp2.general_ledger_number = coa.general_ledger_number
    inner join sub_coa_categories sub
    on coa.sub_coacat_id = sub.sub_coacat_id
    inner join profit_centres pc
    on wbs.pc_id = pc.pc_id   
    order by tmp2.entry_type_id, tmp2.entry_id, tmp2.debit_credit)
--     ) tmp3
--  group by tmp3.company_code, 
-- --           tmp3.entry_type_id,
-- --           tmp3.entry_id,
-- --           tmp3.t_date,
-- --           tmp3.general_ledger_number,
--            tmp3.revenue_cost,
-- --           tmp3.cost_centre,
-- --           tmp3.wbs_code,
--            tmp3.profit_centre_name,
-- --           tmp3.debit_credit,
--           tmp3.currency_id
;
 
 $$ language sql;


/* 
-- not part of the function, if you want to call the function

 select * from transaction_list('US001', 100001, 999999, '2021-03-01', '2021-03-31');
 
*/
