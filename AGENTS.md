# AGENTS.md instructions

Be short and sweet, concise, never assume. Ask in doubts.

## Business Central Demo Context

At the start of each new prospect/demo chat, capture and keep these session references:

- `prospectName`: the prospect/company name.
- `prospectUrl`: the prospect/company URL.

Use `prospectName` as the `Shelf No.` on every item created for that prospect. This supports filtering the Business Central item list by shelf number later.

Default BC environment:

- URL: `https://businesscentral.dynamics.com/eb4005a6-4bc1-41d0-93be-6595f1a5bc80/BCDemoG`
- Company: `G7`, unless the user says otherwise.

For repeatable record creation, prefer `C:\Github\BC Extensions\bc-repeatable` over browser UI.

## Business Central Sales Order Defaults

For demo sales orders, create draft orders only unless the user explicitly asks to release or post.

- Create one sales order per custom item.
- Create one sales line per order.
- Sales line `Type`: `Item`.
- Sales line `Quantity`: `1`.
- Sales line `Location Code`: `MAIN`.
- Put the requested/random delivery date on the sales line `Shipment Date`.
- Use the same selling price as customer `10000` unless the user gives another price rule.
- Usually only the item number/list changes between demo sales-order batches.

## Business Central UI Notes

To assign item attributes on an item card, use `Item` > `Attributes`.

To assign a picture on an item card, first save the product image from the product webpage locally, then use `Picture` > `Import` in the FactBox.

To assign Marketing Text on an item card, click `Edit` in the Marketing Text FactBox and paste concise text from the product webpage.
