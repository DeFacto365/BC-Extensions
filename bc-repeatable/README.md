# BC Repeatable Automation

This folder is the repeatable path for Codex-created Business Central records.

Keep this folder generic. Demo-specific request files, images, logos, and downloaded assets belong in `../demos/{ProspectOrCompanyName}/`, not in `bc-repeatable/`.

## Environment URL

Default Business Central environment:

- Base URL: `https://businesscentral.dynamics.com/eb4005a6-4bc1-41d0-93be-6595f1a5bc80/BCDemoG`
- Full URL pattern: `https://businesscentral.dynamics.com/eb4005a6-4bc1-41d0-93be-6595f1a5bc80/BCDemoG?company={companyName}`
- Current company: provide this per demo with `--company` or `BC_COMPANY`

For future demos, the user may provide only the BC company name, such as `G8`. Build the full BC URL by replacing only the `company=` query parameter.

## One-time setup

1. Publish the AL extension in this folder to `BCDemoG`.
2. Create a Microsoft Entra app for service-to-service auth.
3. Grant it Dynamics 365 Business Central `API.ReadWrite.All`.
4. In Business Central, add the app on the `Microsoft Entra Applications` page.
5. Assign permission set `CODEX AUTOMATION`.

Microsoft documents that Business Central APIs use OAuth bearer tokens, and S2S API calls use scope `https://api.businesscentral.dynamics.com/.default`.

## Create an item

```powershell
$env:BC_CLIENT_ID = '<client id>'
$env:BC_CLIENT_SECRET = '<client secret>'
$company = '<company name>'

& 'C:\Users\jack_\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' `
  'C:\Github\BC Extensions\bc-repeatable\tools\bc_api.py' `
  create-item --company $company --description Test --shelf-no "Prospect Name" --unit-price 100 --uom PCS --replenishment Purchase
```

Attach a picture when available:

```powershell
& 'C:\Users\jack_\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' `
  'C:\Github\BC Extensions\bc-repeatable\tools\bc_api.py' `
  create-item --company $company --description "Metal Implant Bar" --shelf-no "Panthera" --unit-price 100 --uom PCS --replenishment Purchase --picture-path "C:\path\metal-implant-bar.jpg"
```

In the Business Central web client, attach a picture from an item card with `Picture` > `Import` after saving the webpage product image locally.

In the Business Central web client, assign Marketing Text from an item card with Marketing Text `Edit`, then paste concise product text from the webpage.

Add Marketing Text when available:

```powershell
& 'C:\Users\jack_\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' `
  'C:\Github\BC Extensions\bc-repeatable\tools\bc_api.py' `
  create-item --company $company --number MIB-DOLDER-TI --description "Metal Implant Bar - Dolder - Ti" --shelf-no "Panthera" --unit-price 100 --uom PCS --replenishment Purchase --item-category-code METAL-BAR --marketing-text "Unrivaled`n`nOur bar is compatible with the vast majority of known implants, of course, but also with those of emerging and foreign companies. Offered with the longest warranty on the market, this product is simply unrivaled in the industry. Forget standardized bars: the Panthera Dental metallic bar is customized to satisfy the needs of your patients."
```

## Create an item attribute

```powershell
& 'C:\Users\jack_\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' `
  'C:\Github\BC Extensions\bc-repeatable\tools\bc_api.py' `
  create-item-attribute --company $company --name "Available materials and finish types" --type Option --values Ti Co-Cr Silicoating Ionized Sandblast
```

After this is configured, user instructions can be short:

`In G8 create purchased item "Test" UOM PCS price 100.`

## Company Selection

Do not hard-code the Business Central company in automation.

Use either:

- `--company <companyName>` on each command.
- `BC_COMPANY=<companyName>` for the current demo.

For example:

```powershell
$company = 'G8'
$env:BC_COMPANY = $company
```

## Item Defaults

At the start of each new prospect/demo chat, capture `prospectName` and `prospectUrl`.

Use `prospectName` as `Shelf No.` on every item created for that prospect. This supports filtering the item list by shelf number later.

Defaults for item cards:

- `Tax Group Code`: `TAXABLE`
- `Price/Profit Calculation`: `Price=Cost+Profit`
- `Lead Time Calculation`: `3D`
- `Vendor No.`: `10000`
- `Vendor Item No.`: same as the final item number
- `Reordering Policy`: `Lot-for-Lot`
- `Lot Accumulation Period`: `1M`
- `Rescheduling Period`: `1D`

User-provided per item:

- Description/name
- Unit price
- Replenishment system
- UOM when not `PCS`

## Company Information Defaults

For each new demo, update the Business Central `Company Information` page before item/order creation when a prospect URL is provided.

- Use the prospect website URL to gather company information.
- Update the `General` tab fields when confidently available, including company name, address, phone/email/web page, and related identity fields.
- Update the company logo from the website when a clear official logo is available.
- If the website does not clearly expose a field, ask instead of guessing.
- Keep this as part of the new-demo setup procedure together with item and sales-order creation.

## Sales Order Defaults

For demo demand creation, use these defaults unless the user overrides them:

- This is a reusable demo database starter; use the same demo-demand pattern for new demos unless told otherwise.
- Create draft sales orders only; do not release or post.
- Create one sales order per custom item.
- Create one sales line per order.
- Sales line `Type`: `Item`.
- Sales line `Quantity`: `1`.
- Sales line `Location Code`: `MAIN`.
- Put the requested/random delivery date on the sales line `Shipment Date`.
- Use random weekday dates between `2025-11-01` and `2025-12-20`.
- Use the same selling price as customer `10000`.
- Use customers `10000`, `20000`, and `30000`.
- Default split: 5 orders for customer `10000`, 3 orders for customer `20000`, and 2 orders for customer `30000`.
- Customer `10000` is the biggest customer and should get more orders.
- Do not create the orders grouped by customer. Alternate/shuffle customers so the list looks realistic, for example `10000`, `30000`, `20000`, `10000`, etc.
- Do not put `Codex` in `External Document Number`; use prospect/demo-facing values such as `PANTHERA-001`.
- For repeat batches, update the item numbers/list and keep the other defaults.
