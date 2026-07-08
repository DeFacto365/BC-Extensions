page 50100 "Codex Item API"
{
    PageType = API;
    APIPublisher = 'codex';
    APIGroup = 'automation';
    APIVersion = 'v1.0';
    EntityName = 'codexItem';
    EntitySetName = 'codexItems';
    SourceTable = Item;
    DelayedInsert = true;
    InsertAllowed = true;
    ModifyAllowed = true;
    DeleteAllowed = false;
    ODataKeyFields = SystemId;

    layout
    {
        area(Content)
        {
            repeater(Group)
            {
                field(id; Rec.SystemId)
                {
                    Caption = 'Id';
                    Editable = false;
                }
                field(number; Rec."No.")
                {
                    Caption = 'Number';
                }
                field(displayName; Rec.Description)
                {
                    Caption = 'Display Name';
                }
                field(displayName2; Rec."Description 2")
                {
                    Caption = 'Display Name 2';
                }
                field(type; Rec.Type)
                {
                    Caption = 'Type';
                }
                field(itemCategoryCode; Rec."Item Category Code")
                {
                    Caption = 'Item Category Code';
                }
                field(baseUnitOfMeasureCode; Rec."Base Unit of Measure")
                {
                    Caption = 'Base Unit of Measure Code';
                }
                field(shelfNo; Rec."Shelf No.")
                {
                    Caption = 'Shelf No.';
                }
                field(salesUnitOfMeasureCode; Rec."Sales Unit of Measure")
                {
                    Caption = 'Sales Unit of Measure Code';
                }
                field(purchUnitOfMeasureCode; Rec."Purch. Unit of Measure")
                {
                    Caption = 'Purch. Unit of Measure Code';
                }
                field(replenishmentSystem; Rec."Replenishment System")
                {
                    Caption = 'Replenishment System';
                }
                field(leadTimeCalculation; Rec."Lead Time Calculation")
                {
                    Caption = 'Lead Time Calculation';
                }
                field(vendorNo; Rec."Vendor No.")
                {
                    Caption = 'Vendor No.';
                }
                field(vendorItemNo; Rec."Vendor Item No.")
                {
                    Caption = 'Vendor Item No.';
                }
                field(costingMethod; Rec."Costing Method")
                {
                    Caption = 'Costing Method';
                }
                field(unitPrice; Rec."Unit Price")
                {
                    Caption = 'Unit Price';
                }
                field(priceProfitCalculation; Rec."Price/Profit Calculation")
                {
                    Caption = 'Price/Profit Calculation';
                }
                field(genProdPostingGroup; Rec."Gen. Prod. Posting Group")
                {
                    Caption = 'Gen. Prod. Posting Group';
                }
                field(inventoryPostingGroup; Rec."Inventory Posting Group")
                {
                    Caption = 'Inventory Posting Group';
                }
                field(taxGroupCode; Rec."Tax Group Code")
                {
                    Caption = 'Tax Group Code';
                }
                field(reorderingPolicy; Rec."Reordering Policy")
                {
                    Caption = 'Reordering Policy';
                }
                field(lotAccumulationPeriod; Rec."Lot Accumulation Period")
                {
                    Caption = 'Lot Accumulation Period';
                }
                field(reschedulingPeriod; Rec."Rescheduling Period")
                {
                    Caption = 'Rescheduling Period';
                }
                field(itemTrackingCode; Rec."Item Tracking Code")
                {
                    Caption = 'Item Tracking Code';
                }
                field(serialNos; Rec."Serial Nos.")
                {
                    Caption = 'Serial Nos.';
                }
                field(blocked; Rec.Blocked)
                {
                    Caption = 'Blocked';
                }
                field(marketingText; MarketingText)
                {
                    Caption = 'Marketing Text';

                    trigger OnValidate()
                    begin
                        SaveMarketingText(MarketingText);
                    end;
                }
                field(lastModifiedDateTime; Rec.SystemModifiedAt)
                {
                    Caption = 'Last Modified Date Time';
                    Editable = false;
                }
            }
        }
    }

    trigger OnAfterGetRecord()
    var
        EntityText: Codeunit "Entity Text";
    begin
        MarketingText := EntityText.GetText(Database::Item, Rec.SystemId, "Entity Text Scenario"::"Marketing Text");
    end;

    var
        MarketingText: Text;

    local procedure SaveMarketingText(NewMarketingText: Text)
    var
        EntityTextRecord: Record "Entity Text";
        EntityText: Codeunit "Entity Text";
    begin
        if IsNullGuid(Rec.SystemId) then
            exit;

        if not EntityTextRecord.Get(CompanyName(), Database::Item, Rec.SystemId, "Entity Text Scenario"::"Marketing Text") then begin
            EntityTextRecord.Init();
            EntityTextRecord.Company := CopyStr(CompanyName(), 1, MaxStrLen(EntityTextRecord.Company));
            EntityTextRecord."Source Table Id" := Database::Item;
            EntityTextRecord."Source System Id" := Rec.SystemId;
            EntityTextRecord.Scenario := "Entity Text Scenario"::"Marketing Text";
            EntityTextRecord.Insert();
        end;

        EntityText.UpdateText(EntityTextRecord, NewMarketingText);
    end;
}
