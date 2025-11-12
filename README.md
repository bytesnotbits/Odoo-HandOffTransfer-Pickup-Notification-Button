# Odoo-Sales-Order-Pickup-Notification-Button

A one-click “Ready for Pickup” notification from the Handoff step on Sales Order transfers, ideally email now and SMS later.

# Step 1 — Create Tracking Fields on Transfers (`stock.picking`)

We’ll add **four fields** that power the **Pickup Ready** button logic and audit trail.

---

## 1A — Open Studio on the Transfer Form

1. Go to **Inventory → Operations → Transfers**.  
2. Open any **Handoff transfer** (or any transfer—just for editing the view).  
3. Click the **⋮ (gear)** icon → **Studio** to open Studio on the transfer form.

---

## 1B — Add Fields (Model: Transfer `stock.picking`)

Create the following four fields:

### 🟩 Field 1 — Pickup Notified
- **Type:** Boolean  
- **Technical Name:** `x_studio_ready_notified`  
- **Label:** Pickup Notified  
- **Properties:** Read-only (updated by the server action)  
- **Placement:** In a small **“Notifications”** section on the form (not the header)

---

### 🟩 Field 2 — Pickup Notified On
- **Type:** Datetime  
- **Technical Name:** `x_studio_pickup_notified_on`  
- **Label:** Pickup Notified On  
- **Properties:** Read-only  
- **Placement:** Same **“Notifications”** section

---

### 🟩 Field 3 — Pickup Notified By
- **Type:** Many2one → Users (`res.users`)  
- **Technical Name:** `x_studio_pickup_notified_by`  
- **Label:** Pickup Notified By  
- **Properties:** Read-only  
- **Placement:** Same **“Notifications”** section

---

### 🟩 Field 4 — Notify Count
- **Type:** Integer  
- **Technical Name:** `x_studio_notify_count`  
- **Label:** Notify Count  
- **Widget:** **Badge** (if available → *Field Options → Widget → Badge*)  
- **Properties:** Read-only  
- **Placement:** Drag this field into the **header (top bar)** of the form, on the right side, so users see it as a counter next to the future button.

> 💡 **Tip:** If “Badge” isn’t listed in Studio widgets, leave it as an Integer for now. The counter will still increment; you can switch to Badge later.

---

## B1 — Add the Partner Field (Studio → Contacts)

1. Open **Contacts → any partner → Studio**.  
2. Add a **Text** field with the following properties:  
   - **Label:** Pickup Extra Emails  
   - **Technical Name:** `x_studio_notify_pickup_ready`  
   - **Help Text:** “Comma/semicolon/space-separated emails to notify when orders are ready for pickup.”
  
---

## Step 2
This step was intended to create an email template, but this template will be implemented into the server action. The current "Ready for Pickup" email template sent when the HandOff transfer is validated will be changed to reflect that the order has been picked up.

---

# Step 3 — Create the Server Action (Send Email Without a Template)

---

## 3A — Create the Server Action

1. Navigate to **Settings → Technical → Automation → Server Actions → New**  
2. Fill in the following details:

   - **Name:** `Notify Ready for Pickup (Email)`  
   - **Model:** `Transfer (stock.picking)`  
   - **Action To Do:** `Execute Python Code`  
   - **Python Code File:** `readyForPickupButton.py`

3. **Save** the Server Action.  
4. Click **Create Contextual Action** to add it as a button on the Transfer form.

---

## 3B — Result

That’s it for the backend logic.  
No email template is involved — so **nothing else can auto-fire this message** except your **custom “Notify Ready for Pickup” button**.

---

Step 4 — Add the “Notify Ready for Pickup” button on Handoff transfers
4A) Open Studio on a Handoff transfer

Go to Inventory → Operations → Transfers.

Open any Handoff transfer.

Click ⋮ (gear) → Studio to edit the form.

4B) Add the button

In the left palette, choose Buttons → drag a Header Button (or regular Form button if header isn’t available) onto the form.

Label: Notify Ready for Pickup

Type / Action: Execute Server Action

Server Action: select Notify Ready for Pickup (Email) (the one you just created).

Confirm before execution: enable and set message:
Send pickup notification now?

4C) Visibility (only on Handoff, not done/cancel)

In the button’s Visibility / Domain (sometimes labeled “Limit Visibility” or “Invisible If”), set this domain:

```[('picking_type_id', '=', 2), ('state', 'not in', ['done','cancel'])]```

This uses the Operation Type ID = 2, so renaming “Handoff” won’t matter.

Visibility / Domain:

```[('picking_type_id', '=', 2), ('state', 'not in', ['done','cancel']), ('x_notify_count', '>=', 1)]```

4E) Place the counter field near the button (optional)

If you want the team to see the count next to the button, drag x_notify_count near the button area (header or top of the form), and leave it read-only.
