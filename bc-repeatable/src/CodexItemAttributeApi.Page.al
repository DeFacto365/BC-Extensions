page 50101 "Codex Item Attribute API"
{
    PageType = API;
    APIPublisher = 'codex';
    APIGroup = 'automation';
    APIVersion = 'v1.0';
    EntityName = 'codexItemAttribute';
    EntitySetName = 'codexItemAttributes';
    SourceTable = "Item Attribute";
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
                field(attributeId; Rec.ID)
                {
                    Caption = 'Attribute Id';
                    Editable = false;
                }
                field(name; Rec.Name)
                {
                    Caption = 'Name';
                }
                field(type; Rec.Type)
                {
                    Caption = 'Type';
                }
                field(blocked; Rec.Blocked)
                {
                    Caption = 'Blocked';
                }
            }
        }
    }
}
