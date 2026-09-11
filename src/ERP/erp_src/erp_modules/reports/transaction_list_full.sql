-- combine double entries posted in journal_entry, ar and ap
set search_path to ocean_stream;

drop function if exists transaction_list(char(6),int, int, date, date, char(5), char(5))
	start_date_p date, end_date_p date);

create or replace function transaction_list_full(
						company_code_p char(6) --p mean parameter
						, general_ledger_number_start_p int-- between 100000-999999
						, general_ledger_number_end_p int-- between 100000-999999
						, start_date_p date
						, end_date_p date
						, p_cost_centre char(5)
						, p_wbs_code char(5)
						)
	return table(company_code char(6)
				, entry_type_id varchar(3)
				, entry_id int
				, transaction_date date
				, general_ledger_number int(6)
				, cost_centre char(5)
				, wbs_code char(5)
				, debit_credit
				, currency_id
				, amount numeric)

as 
  $$

	select * from (
		-- double entries from je
		select je.company_code, 
				je.entry_type_id, 
				je.je_id as entry_id,
				jei.transaction_date as date,
				jei.general_ledger_number,
				jei.cc_id as cost_centre,
				jei.wbs_code,
				jei.debit_credit,
				jei.currency_id,
				jei.amount
		from journal_entry_item jei
		inner join journal_entry je
		on je.je_id = jei.je_id
		where je.company_code = 'US001'
		and jei.transaction_date between '2021-03-01' and '2021-03-31'
		-- double entries from ar_invoice
		union all
		select ar.company_code, 
				ar.entry_type_id,
				ar.rie_id as entry_id,
				ar.date,
				aii.general_ledger_number,
				aii.cc_id as cost_centre,
				''::char(5) as wbs_code,
				aii.debit_credit,
				aii.currency_id,
				aii.amount	
		from ar_invoice as ar
		inner join ar_invoice_item aii
		on ar.rie_id = aii.rie_id
		where ar.company_code = 'US001'
		and ar.date between '2021-03-01' and '2021-03-31'
		-- double entries from ar_receipt
		union all
		select arr.company_code,
				arr.entry_type_id,
				arr.rre_id as entry_id,
				arr.date,
				ari.general_ledger_number,
				''::char(6) cost_centre,
				''::char(5)	wbs_code,
				ari.debit_credit,
				ari.currency_id,
				ari.amount
		from ar_receipt arr
		inner join ar_receipt_item ari
		on arr.rre_id = ari.rre_id
		where arr.company_code = 'US001'
		and arr.date between '2021-03-01' and '2021-03-31'
		-- double entries from ap_invoice
		union all
		select ap.company_code,
				ap.entry_type_id,
				ap.pie_id as entry_id,
				ap.date,
				api.general_ledger_number,
				api.cc_id as cost_centre,
				api.wbs_code,
				api.debit_credit,
				api.currency_id,
				api.amount
		from ap_invoice as ap
		inner join ap_invoice_item as api
		on ap.pie_id = api.pie_id
		where ap.company_code = 'US001'
		and ap.date between '2021-03-01' and '2021-03-31'
		-- double entries from ap_payment
		union all
		select app.company_code,
				app.entry_type_id,
				app.ppe_id,
				app.date,
				api.general_ledger_number,
				''::char(6) cost_centre,
				''::char(5)	wbs_code,
				api.debit_credit,
				api.currency_id,
				api.amount
		from ap_payment as app
		inner join ap_payment_item as api
		on app.ppe_id = api.ppe_id
		where app.company_code = 'US001'
		and app.date between '2021-03-01' and '2021-03-31'
	) tmp
	order by entry_type_id, entry_id, debit_credit

$$ language sql;
