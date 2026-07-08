permissionset 50100 "CODEX AUTOMATION"
{
    Assignable = true;
    Caption = 'Codex Automation';
    Permissions =
        tabledata Item = RIM,
        tabledata "Item Attribute" = RIM,
        tabledata "Item Attribute Value" = RIM,
        tabledata "Item Attribute Value Mapping" = RIM,
        tabledata "Entity Text" = RIM,
        tabledata "AAD Application" = RIM,
        tabledata "Access Control" = RIM,
        page "Codex Item API" = X,
        page "Codex Item Attribute API" = X,
        page "Codex Item Attribute Value API" = X,
        page "Codex Item Attr Mapping API" = X,
        page "Codex AAD Application API" = X,
        page "Codex Access Control API" = X;
}
