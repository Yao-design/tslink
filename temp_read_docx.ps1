$word = New-Object -ComObject Word.Application
$word.Visible = $false
$word.DisplayAlerts = $false

try {
    $doc = $word.Documents.Open("C:\Users\18836\Desktop\new sdk\ts_hq_260305\ts-hq_20260305\BLE Broadcast Loss_Memory Analysis Report.docx")
    $content = $doc.Content.Text
    $doc.Close($false)
    Write-Output $content
} catch {
    Write-Output "Error: $_"
} finally {
    $word.Quit()
    [System.Runtime.InteropServices.Marshal]::ReleaseComObject($word) | Out-Null
}
