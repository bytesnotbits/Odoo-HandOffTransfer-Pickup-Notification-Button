# --- Guardrails: only on Handoff (Operation Type ID = 2), assigned = true, not done/cancel ---
if not record.picking_type_id or record.picking_type_id.id != 2:

if record.state in ('done', 'cancel'):
    raise UserError("This transfer is already validated or cancelled.")

# Require 'Ready' (assigned) before notifying
if record.state != 'assigned':
    raise UserError("Transfer must be in Ready state (assigned) before notifying.")

so = record.sale_id

# --- Collect follower emails (zero maintenance path) ---
emails = set()
for partner in record.message_partner_ids:
    if partner.email:
        emails.add(partner.email.strip().lower())

# --- Helper: parse extra emails (no imports) ---
def extract_emails(raw):
    if not raw:
        return []
    txt = raw.replace(',', ' ').replace(';', ' ').replace('\n', ' ').replace('\t', ' ')
    parts = [p.strip() for p in txt.split(' ') if p.strip()]
    out = []
    for p in parts:
        # Handle "Name <email@domain>" formats
        if '<' in p and '>' in p:
            start = p.find('<') + 1
            end = p.find('>', start)
            if end > start:
                p = p[start:end]
        e = p.strip().lower()
        if '@' in e and e.count('@') == 1 and '.' in e.split('@')[-1] and not e.endswith('.'):
            out.append(e)
    return out

# --- Collect extra emails from Customer + Delivery Address (your Studio field) ---
extra_sources = []

if so and so.partner_id and 'x_notify_pickup_ready' in so.partner_id._fields:
    extra_sources.append((so.partner_id.x_notify_pickup_ready or ''))

shipping = getattr(so, 'partner_shipping_id', False) if so else False
if shipping and 'x_notify_pickup_ready' in shipping._fields:
    extra_sources.append((shipping.x_notify_pickup_ready or ''))

for src in extra_sources:
    for e in extract_emails(src):
        emails.add(e)

# If we somehow have no emails, stop with a friendly error
if not emails:
    raise UserError("No recipient emails found. Add followers with emails or fill the 'Notify Pickup Ready' field on the Customer/Delivery Address.")

# --- (Optional) subscribe Customer & Ship-to for audit/portal ---
to_follow = []
if so:
    for p in (so.partner_id, shipping):
        if p and p.id not in record.message_partner_ids.ids:
            to_follow.append(p.id)
if to_follow:
    record.message_subscribe(partner_ids=to_follow)

# --- Compose the email (no template needed) ---
order_ref = (so.name if so else (record.origin or record.name))
subject = f"Your order {order_ref} is ready for pickup"

body_html = f"""
<p>Hello,</p>
<p>Your order <strong>{order_ref}</strong> is ready for pickup.</p>
<p>Thank you,<br/>{record.company_id.name}</p>
"""

# Send via mail.mail to the deduped list
Mail = env['mail.mail']
mail_values = {
    'subject': subject,
    'body_html': body_html,
    'email_to': ','.join(sorted(emails)),
    'email_from': (record.company_id.email or env.user.email_formatted),
    'auto_delete': False,
}
mail = Mail.create(mail_values)
mail.send()

# --- Audit: increment counter and stamp who/when ---
count = (record.x_notify_count or 0) + 1
record.write({
    'x_ready_notified': True,
    'x_ready_notified_on': fields.Datetime.now(),
    'x_ready_notified_by': env.user.id,
    'x_notify_count': count,
})

# --- Chatter note with recipients ---
record.message_post(
    body=f"Ready for Pickup notification sent (#{count}) to: {', '.join(sorted(emails))}",
    message_type='comment',
    subtype_xmlid='mail.mt_note',
)
