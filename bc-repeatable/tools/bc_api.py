#!/usr/bin/env python3
import argparse
import json
import mimetypes
import os
import sys
import tempfile
import urllib.error
import urllib.parse
import urllib.request

TENANT_ID = os.environ.get("BC_TENANT_ID", "eb4005a6-4bc1-41d0-93be-6595f1a5bc80")
ENVIRONMENT = os.environ.get("BC_ENVIRONMENT", "BCDemoG")
BASE_URI = "https://api.businesscentral.dynamics.com"
DEFAULT_COMPANY = os.environ.get("BC_COMPANY")
ITEM_TABLE_ID = 27


def request(method, url, token=None, payload=None, extra_headers=None):
    headers = {"Accept": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    if extra_headers:
        headers.update(extra_headers)
    data = None
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            raw = resp.read().decode("utf-8")
            return json.loads(raw) if raw else {}
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise SystemExit(f"{method} {url} failed: HTTP {exc.code}\n{body}") from exc


def request_bytes(method, url, token, data, content_type):
    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {token}",
        "Content-Type": content_type,
        "If-Match": "*",
    }
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            raw = resp.read().decode("utf-8")
            return json.loads(raw) if raw else {}
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise SystemExit(f"{method} {url} failed: HTTP {exc.code}\n{body}") from exc


def get_s2s_token():
    client_id = os.environ.get("BC_CLIENT_ID")
    client_secret = os.environ.get("BC_CLIENT_SECRET")
    if not client_id or not client_secret:
        raise SystemExit("Set BC_CLIENT_ID and BC_CLIENT_SECRET for service-to-service API calls.")

    token_url = f"https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/token"
    data = urllib.parse.urlencode(
        {
            "grant_type": "client_credentials",
            "client_id": client_id,
            "client_secret": client_secret,
            "scope": f"{BASE_URI}/.default",
        }
    ).encode("utf-8")
    req = urllib.request.Request(
        token_url,
        data=data,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return json.loads(resp.read().decode("utf-8"))["access_token"]
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise SystemExit(f"Token request failed: HTTP {exc.code}\n{body}") from exc


def api_root():
    return f"{BASE_URI}/v2.0/{TENANT_ID}/{ENVIRONMENT}/api/v2.0"


def custom_api_root():
    return f"{BASE_URI}/v2.0/{TENANT_ID}/{ENVIRONMENT}/api/codex/automation/v1.0"


def odata_quote(value):
    return "'" + value.replace("'", "''") + "'"


def odata_filter_url(base_url, filter_text):
    params = urllib.parse.urlencode({"$filter": filter_text}, safe="'")
    return f"{base_url}?{params}"


def company_id(token, company_name):
    url = odata_filter_url(f"{api_root()}/companies", f"name eq {odata_quote(company_name)}")
    data = request("GET", url, token)
    rows = data.get("value", [])
    if not rows:
        all_companies = request("GET", f"{api_root()}/companies", token).get("value", [])
        names = ", ".join(c.get("name", "") for c in all_companies)
        raise SystemExit(f"Company not found: {company_name}. Available: {names}")
    return rows[0]["id"]


def picture_file(args):
    if args.picture_path:
        return args.picture_path
    if not args.picture_url:
        return None

    suffix = os.path.splitext(urllib.parse.urlparse(args.picture_url).path)[1] or ".jpg"
    target = os.path.join(tempfile.gettempdir(), f"bc-item-picture{suffix}")
    try:
        urllib.request.urlretrieve(args.picture_url, target)
    except urllib.error.HTTPError as exc:
        raise SystemExit(f"Picture download failed: HTTP {exc.code}. Save it locally and use --picture-path.") from exc
    return target


def attach_item_picture(token, company_guid, item_guid, file_path):
    picture_url = f"{api_root()}/companies({company_guid})/items({item_guid})/picture"
    picture = request("GET", picture_url, token)
    edit_link = (
        picture.get("pictureContent@odata.mediaEditLink")
        or picture.get("content@odata.mediaEditLink")
        or picture.get("pictureContent@odata.editLink")
        or f"{picture_url}/pictureContent"
    )
    if not edit_link:
        raise SystemExit(f"Picture created but no media edit link was returned:\n{json.dumps(picture, indent=2)}")

    content_type = mimetypes.guess_type(file_path)[0] or "application/octet-stream"
    with open(file_path, "rb") as handle:
        return request_bytes("PATCH", edit_link, token, handle.read(), content_type)


def get_first_by_filter(token, url, filter_text):
    return next(iter(request("GET", odata_filter_url(url, filter_text), token).get("value", [])), None)


def assign_item_attribute(token, company_guid, item_number, attribute_name, attribute_value):
    attributes_url = f"{custom_api_root()}/companies({company_guid})/codexItemAttributes"
    values_url = f"{custom_api_root()}/companies({company_guid})/codexItemAttributeValues"
    mappings_url = f"{custom_api_root()}/companies({company_guid})/codexItemAttributeMappings"

    attribute = get_first_by_filter(token, attributes_url, f"name eq {odata_quote(attribute_name)}")
    if not attribute:
        raise SystemExit(f"Item attribute not found: {attribute_name}")
    attribute_id = attribute["attributeId"]

    value_filter = f"attributeId eq {attribute_id} and value eq {odata_quote(attribute_value)}"
    value = get_first_by_filter(token, values_url, value_filter)
    if not value:
        value = request("POST", values_url, token, {"attributeId": attribute_id, "value": attribute_value})
    value_id = value["valueId"]

    mapping_filter = (
        f"recordTableId eq {ITEM_TABLE_ID} and recordNo eq {odata_quote(item_number)} "
        f"and attributeId eq {attribute_id}"
    )
    mapping = get_first_by_filter(token, mappings_url, mapping_filter)
    payload = {
        "recordTableId": ITEM_TABLE_ID,
        "recordNo": item_number,
        "attributeId": attribute_id,
        "attributeValueId": value_id,
    }
    if mapping:
        return request(
            "PATCH",
            f"{mappings_url}({mapping['id']})",
            token,
            {"attributeValueId": value_id},
            extra_headers={"If-Match": "*"},
        )
    return request("POST", mappings_url, token, payload)


def create_item(args):
    selected_company = resolve_company(args.company)
    token = get_s2s_token()
    cid = company_id(token, selected_company)
    payload = {
        "displayName": args.description,
        "type": "Inventory",
        "shelfNo": args.shelf_no,
        "baseUnitOfMeasureCode": args.uom,
        "salesUnitOfMeasureCode": args.uom,
        "purchUnitOfMeasureCode": args.uom,
        "priceProfitCalculation": args.price_profit_calculation,
        "taxGroupCode": args.tax_group_code,
        "replenishmentSystem": args.replenishment,
        "leadTimeCalculation": args.lead_time,
        "costingMethod": args.costing_method,
        "genProdPostingGroup": args.gen_prod_posting_group,
        "inventoryPostingGroup": args.inventory_posting_group,
        "reorderingPolicy": args.reordering_policy,
        "lotAccumulationPeriod": args.lot_accumulation_period,
        "reschedulingPeriod": args.rescheduling_period,
    }
    if args.item_tracking_code:
        payload["itemTrackingCode"] = args.item_tracking_code
    if args.serial_nos:
        payload["serialNos"] = args.serial_nos
    if args.unit_cost is not None:
        payload["unitCost"] = args.unit_cost
    if args.profit_percent is not None:
        payload["profitPercent"] = args.profit_percent
    if args.vendor_no and not args.no_vendor:
        payload["vendorNo"] = args.vendor_no
    if args.number:
        payload["number"] = args.number
    if args.item_category_code:
        payload["itemCategoryCode"] = args.item_category_code
    url = f"{custom_api_root()}/companies({cid})/codexItems"
    existing = get_first_by_filter(token, url, f"number eq {odata_quote(args.number)}") if args.number else None
    if existing:
        item_id = existing["id"]
        created = request("PATCH", f"{url}({item_id})", token, payload, extra_headers={"If-Match": "*"})
    else:
        created = request("POST", url, token, payload)
    item_number = created.get("number") or args.number
    item_id = created.get("id")
    if item_number and item_id:
        patch_url = f"{url}({item_id})"
        patch_payload = {"unitPrice": args.unit_price}
        if args.unit_cost is not None:
            patch_payload["unitCost"] = args.unit_cost
        if args.profit_percent is not None:
            patch_payload["profitPercent"] = args.profit_percent
        if args.vendor_no and not args.no_vendor:
            patch_payload["vendorItemNo"] = item_number
        if args.marketing_text:
            patch_payload["marketingText"] = args.marketing_text
        created = request("PATCH", patch_url, token, patch_payload, extra_headers={"If-Match": "*"})
    for attribute in args.attribute:
        if "=" not in attribute:
            raise SystemExit(f"Attribute must be NAME=VALUE, got: {attribute}")
        name, value = attribute.split("=", 1)
        assign_item_attribute(token, cid, item_number, name, value)
    file_path = picture_file(args)
    if file_path and item_id:
        attach_item_picture(token, cid, item_id, file_path)
        created["pictureAttached"] = True
    print(json.dumps(created, indent=2))


def create_item_attribute(args):
    selected_company = resolve_company(args.company)
    token = get_s2s_token()
    cid = company_id(token, selected_company)
    attributes_url = f"{custom_api_root()}/companies({cid})/codexItemAttributes"
    values_url = f"{custom_api_root()}/companies({cid})/codexItemAttributeValues"
    existing = request("GET", odata_filter_url(attributes_url, f"name eq {odata_quote(args.name)}"), token).get("value", [])

    if existing:
        attribute = existing[0]
    else:
        attribute = request("POST", attributes_url, token, {"name": args.name, "type": args.type})

    attribute_id = attribute.get("attributeId")
    if attribute_id is None:
        raise SystemExit(f"Attribute response did not include attributeId:\n{json.dumps(attribute, indent=2)}")

    created_values = []
    for value in args.values:
        value_filter = f"attributeId eq {attribute_id} and value eq {odata_quote(value)}"
        existing_values = request("GET", odata_filter_url(values_url, value_filter), token).get("value", [])
        if existing_values:
            created_values.append(existing_values[0])
            continue
        created_values.append(request("POST", values_url, token, {"attributeId": attribute_id, "value": value}))

    print(json.dumps({"attribute": attribute, "values": created_values}, indent=2))


def resolve_company(company_name):
    if company_name:
        return company_name
    raise SystemExit("Set --company or BC_COMPANY. Do not rely on a hard-coded company for demo automation.")


def main():
    parser = argparse.ArgumentParser(description="Repeatable Business Central record automation.")
    sub = parser.add_subparsers(dest="command", required=True)

    item = sub.add_parser("create-item")
    item.add_argument("--company", default=DEFAULT_COMPANY)
    item.add_argument("--description", required=True)
    item.add_argument("--shelf-no", required=True, help="Demo/customer name to put in Shelf No.")
    item.add_argument("--unit-price", required=True, type=float)
    item.add_argument("--uom", default="PCS")
    item.add_argument("--replenishment", required=True, choices=["Purchase", "Prod. Order", "Assembly"])
    item.add_argument("--vendor-no", default="10000")
    item.add_argument("--no-vendor", action="store_true")
    item.add_argument("--number")
    item.add_argument("--item-category-code")
    item.add_argument("--costing-method", default="FIFO")
    item.add_argument("--gen-prod-posting-group", default="RETAIL")
    item.add_argument("--inventory-posting-group", default="RESALE")
    item.add_argument("--tax-group-code", default="TAXABLE")
    item.add_argument("--price-profit-calculation", default="Price=Cost+Profit")
    item.add_argument("--lead-time", default="3D")
    item.add_argument("--reordering-policy", default="Lot-for-Lot")
    item.add_argument("--lot-accumulation-period", default="1M")
    item.add_argument("--rescheduling-period", default="1D")
    item.add_argument("--item-tracking-code")
    item.add_argument("--serial-nos")
    item.add_argument("--unit-cost", type=float)
    item.add_argument("--profit-percent", type=float)
    item.add_argument("--attribute", action="append", default=[])
    item.add_argument("--picture-url")
    item.add_argument("--picture-path")
    item.add_argument("--marketing-text")
    item.set_defaults(func=create_item)

    attr = sub.add_parser("create-item-attribute")
    attr.add_argument("--company", default=DEFAULT_COMPANY)
    attr.add_argument("--name", required=True)
    attr.add_argument("--type", default="Option", choices=["Option", "Text", "Integer", "Decimal", "Date"])
    attr.add_argument("--values", nargs="+", required=True)
    attr.set_defaults(func=create_item_attribute)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    sys.exit(main())
