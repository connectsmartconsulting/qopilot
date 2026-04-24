# Acme FinTech customer service chatbot

Acme is a 150-person Ontario lending company. We operate consumer personal loans
and small-business working-capital loans across Canada. We are regulated by OSFI
under guideline E-23, and we have customers in the United States and Europe.

The chatbot is built on GPT-4o via the OpenAI API. It answers product questions
(loan types, rates, eligibility), handles basic account lookups via a tool-use
integration with our core banking API, and escalates complex cases to human
agents. It does not provide personalised financial advice. It does not execute
transactions.

The chatbot is scoped strictly to Acme products. Off-topic questions should be
declined. Customer PII (name, account number, SIN) may appear in session context
through the account-lookup tool. We have a data retention policy of 30 days for
conversation transcripts.

We plan to expand to a European customer base in Q3 2026, which triggers EU AI
Act Article 15 obligations for the system.
