page 50102 "Codex Item Attribute Value API"
{
    PageType = API;
    APIPublisher = 'codex';
    APIGroup = 'automation';
    APIVersion = 'v1.0';
    EntityName = 'codexItemAttributeValue';
    EntitySetName = 'codexItemAttributeValues';
    SourceTable = "Item Attribute Value";
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
                field(attributeId; Rec."Attribute ID")
                {
                    Caption = 'Attribute Id';
                }
                field(valueId; Rec.ID)
                {
                    Caption = 'Value Id';
                    Editable = false;
                }
                field(value; Rec.Value)
                {
                    Caption = 'Value';
                }
                field(blocked; Rec.Blocked)
                {
                    Caption = 'Blocked';
                }
            }
        }
    }
}
