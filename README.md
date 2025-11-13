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
- **Model:** Transfer
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
***

# Step 4 — Add the “Notify Ready for Pickup” Button on Handoff Transfers

We’ll now add the button that triggers your server action directly from the Handoff transfer form.

---

## 4A — Open Studio on a Handoff Transfer

1.  Go to **Inventory → Operations → Transfers**.
2.  Open any **Handoff transfer**.
3.  Click the **⋮ (gear)** icon → **Studio** to edit the form.

---

## 4B — Add the Button

1.  In the left palette, choose **Buttons** → drag a **Header Button** (or a regular Form button if the header isn’t available) onto the form.
2.  Configure the button as follows:
    *   **Label:** `Notify Ready for Pickup`
    *   **Type / Action:** `Execute Server Action`
    *   **Server Action:** `Notify Ready for Pickup (Email)` (the one you created in Step 3)
    *   **Confirm Before Execution:** ✅ Enable
        *   **Confirmation Message:** `Send pickup notification now?`

---

## 4C — Set Button Visibility (Only on Handoff, Not Done/Cancel)

In the button’s **Visibility / Domain** section (sometimes labeled *“Limit Visibility”* or *“Invisible If”*), set this domain:

```python
[('picking_type_id', '=', 2), ('state', 'not in', ['done','cancel'])]
```

This ensures the button only appears on Handoff transfers that are not yet completed or cancelled. It uses Operation Type ID = 2, so renaming “Handoff” will not affect it.

---

## 4D — Optional: Show Button Only After First Notification Sent

If you prefer to display the button only after at least one notification has been sent, use this extended domain instead:

```python
[('picking_type_id', '=', 2), ('state', 'not in', ['done','cancel']), ('x_studio_notify_count', '>=', 1)]
```

---

## 4E — Place the Counter Field Near the Button (Optional)

To help users track how many notifications have been sent:

*   Drag the field `x_studio_notify_count` near the button area (in the header or top of the form).
*   Keep it **Read-only**.
*   Optionally set the **Widget** to `Badge` for a clean numeric counter display.

---
