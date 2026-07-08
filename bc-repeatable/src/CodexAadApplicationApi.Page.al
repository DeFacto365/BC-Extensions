page 50104 "Codex AAD Application API"
{
    PageType = API;
    APIPublisher = 'codex';
    APIGroup = 'automation';
    APIVersion = 'v1.0';
    EntityName = 'codexAadApplication';
    EntitySetName = 'codexAadApplications';
    SourceTable = "AAD Application";
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
                field(clientId; Rec."Client Id")
                {
                    Caption = 'Client Id';
                }
                field(description; Rec.Description)
                {
                    Caption = 'Description';
                }
                field(contactInformation; Rec."Contact Information")
                {
                    Caption = 'Contact Information';
                }
                field(state; Rec.State)
                {
                    Caption = 'State';
                }
                field(userId; Rec."User ID")
                {
                    Caption = 'User Id';
                    Editable = false;
                }
                field(permissionGranted; Rec."Permission Granted")
                {
                    Caption = 'Permission Granted';
                }
            }
        }
    }
}
