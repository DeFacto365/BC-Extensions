page 50105 "Codex Access Control API"
{
    PageType = API;
    APIPublisher = 'codex';
    APIGroup = 'automation';
    APIVersion = 'v1.0';
    EntityName = 'codexAccessControl';
    EntitySetName = 'codexAccessControls';
    SourceTable = "Access Control";
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
                field(userSecurityId; Rec."User Security ID")
                {
                    Caption = 'User Security Id';
                }
                field(roleId; Rec."Role ID")
                {
                    Caption = 'Role Id';

                    trigger OnValidate()
                    begin
                        PermissionSetLookupRecord.SetRange("Role ID", Rec."Role ID");
                        PermissionSetLookupRecord.FindFirst();
                        Rec.Scope := PermissionSetLookupRecord.Scope;
                        Rec."App ID" := PermissionSetLookupRecord."App ID";
                        PermissionSetLookupRecord.Reset();
                    end;
                }
                field(companyName; Rec."Company Name")
                {
                    Caption = 'Company Name';
                }
                field(scope; Rec.Scope)
                {
                    Caption = 'Scope';
                }
                field(appId; Rec."App ID")
                {
                    Caption = 'App Id';
                }
            }
        }
    }

    var
        PermissionSetLookupRecord: Record "Aggregate Permission Set";
}
