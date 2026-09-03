#Install-Module ImportExcel -Scope CurrentUser -Force
# ==========================================================
# Generate-F7FolderInventory.ps1
# Creates an Excel inventory of the F7Hub folder structure
# Requires: ImportExcel
# ==========================================================

$Root = "C:\Users\Jo\OneDrive\Desktop\LAB\F7Hub"

$OutputFile = Join-Path $Root "F7Hub_FolderInventory.xlsx"

Import-Module ImportExcel

$Folders = Get-ChildItem -Path $Root -Directory -Recurse |
Sort-Object FullName

$i = 1

$Inventory = foreach ($Folder in $Folders)
{
    $Relative = $Folder.FullName.Replace("$Root\", "")

    [PSCustomObject]@{

        ID           = $i++

        Name         = $Folder.Name

        ParentFolder = $Folder.Parent.Name

        RelativePath = $Relative

        FullPath     = $Folder.FullName

        Depth        = ($Relative.Split('\')).Count
    }
}

$Inventory |
Export-Excel `
    -Path $OutputFile `
    -WorksheetName "Folders" `
    -TableName "FolderInventory" `
    -TableStyle Medium2 `
    -AutoSize `
    -FreezeTopRow `
    -BoldTopRow `
    -AutoFilter

Write-Host ""
Write-Host "Excel inventory created successfully!" -ForegroundColor Green
Write-Host $OutputFile