page 50103 "Codex Item Attr Mapping API"
{
    PageType = API;
    APIPublisher = 'codex';
    APIGroup = 'automation';
    APIVersion = 'v1.0';
    EntityName = 'codexItemAttributeMapping';
    EntitySetName = 'codexItemAttributeMappings';
    SourceTable = "Item Attribute Value Mapping";
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
                field(recordTableId; Rec."Table ID")
                {
                    Caption = 'Record Table Id';
                }
                field(recordNo; Rec."No.")
                {
                    Caption = 'Record No.';
                }
                field(attributeId; Rec."Item Attribute ID")
                {
                    Caption = 'Attribute Id';
                }
                field(attributeValueId; Rec."Item Attribute Value ID")
                {
                    Caption = 'Attribute Value Id';
                }
            }
        }
    }
}
