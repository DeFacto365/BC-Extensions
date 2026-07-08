# AGENTS.md instructions

Be short and sweet, concise, never assume. Ask in doubts.

## Business Central Demo Context

At the start of each new prospect/demo chat, capture and keep these session references:

- `prospectName`: the prospect/company name.
- `prospectUrl`: the prospect/company URL.

Use `prospectName` as the `Shelf No.` on every item created for that prospect. This supports filtering the Business Central item list by shelf number later.

Default BC environment:

- Base URL: `https://businesscentral.dynamics.com/eb4005a6-4bc1-41d0-93be-6595f1a5bc80/BCDemoG`
- Full URL pattern: `https://businesscentral.dynamics.com/eb4005a6-4bc1-41d0-93be-6595f1a5bc80/BCDemoG?company={companyName}`
- Current company: provided by the user for each demo, for example `G7`.
- For future demos, the user may provide only the BC company name, such as `G8`. Build the full BC URL by replacing only the `company=` query parameter.

For repeatable record creation, prefer `C:\Github\BC Extensions\bc-repeatable` over browser UI.

Before compiling or publishing the AL extension, refresh Business Central symbols unattended:

```powershell
& 'C:\Users\jack_\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' `
  'C:\Github\BC Extensions\bc-repeatable\tools\refresh_symbols.py'
```

This uses Microsoft AL's local MCP server with global sources and forced re-downloads so Application/System symbols stay current without asking the user.

## Repository Organization

Keep the repository organized by separating shared automation from demo-specific material.

- Put shared/base setup, standards, and reusable notes in `main/`.
- Put repeatable automation code in `bc-repeatable/`.
- Put each demo in `demos/{ProspectOrCompanyName}/`.
- Store demo-specific files, images, downloaded logos, product pictures, scraped data, and request JSON in that demo folder.
- Do not leave prospect-specific assets in the repository root or in shared folders.
- For a new demo, create the demo folder first, then save all related files there.

## Business Central Company Information Defaults

For each new demo, update the Business Central `Company Information` page before item/order creation when a prospect URL is provided.

- Use the prospect website URL to gather company information.
- Update the `General` tab fields when confidently available, including company name, address, phone/email/web page, and related identity fields.
- Update the company logo from the website when a clear official logo is available.
- If the website does not clearly expose a field, ask instead of guessing.
- Keep this as part of the new-demo setup procedure together with item and sales-order creation.

## Business Central Sales Order Defaults

For demo sales orders, create draft orders only unless the user explicitly asks to release or post.

- This is a reusable demo database starter; use the same demo-demand pattern for new demos unless told otherwise.
- Create one sales order per custom item.
- Create one sales line per order.
- Sales line `Type`: `Item`.
- Sales line `Quantity`: `1`.
- Sales line `Location Code`: `MAIN`.
- Put the requested/random delivery date on the sales line `Shipment Date`.
- Use random weekday dates between `2025-11-01` and `2025-12-20`.
- Use the same selling price as customer `10000` unless the user gives another price rule.
- Use customers `10000`, `20000`, and `30000`.
- Default split: 5 orders for customer `10000`, 3 orders for customer `20000`, and 2 orders for customer `30000`.
- Customer `10000` is the biggest customer and should get more orders.
- Do not create the orders grouped by customer. Alternate/shuffle customers so the list looks realistic, for example `10000`, `30000`, `20000`, `10000`, etc.
- Do not put `Codex` in `External Document Number`; use prospect/demo-facing values such as `PANTHERA-001`.
- Usually only the item number/list changes between demo sales-order batches.

## Business Central UI Notes

To assign item attributes on an item card, use `Item` > `Attributes`.

To assign a picture on an item card, first save the product image from the product webpage locally, then use `Picture` > `Import` in the FactBox.

To assign Marketing Text on an item card, click `Edit` in the Marketing Text FactBox and paste concise text from the product webpage.
