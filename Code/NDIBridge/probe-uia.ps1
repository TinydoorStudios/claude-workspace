# Probe: does NDI Bridge expose its Join/Leave button to UI Automation?
Add-Type -AssemblyName UIAutomationClient
Add-Type -AssemblyName UIAutomationTypes
$AE = [System.Windows.Automation.AutomationElement]
$TS = [System.Windows.Automation.TreeScope]
$CT = [System.Windows.Automation.ControlType]

$proc = Get-Process -Name 'Application.NDI.Bridge.UI' -ErrorAction SilentlyContinue
if (-not $proc) { Write-Output 'NDI Bridge UI process not running.'; return }
Write-Output ("UI PID(s): " + ($proc.Id -join ','))

$root = $AE::RootElement
foreach ($procId in $proc.Id) {
    $cond = New-Object System.Windows.Automation.PropertyCondition($AE::ProcessIdProperty, $procId)
    $win  = $root.FindFirst($TS::Children, $cond)
    if (-not $win) { Write-Output "  no top-level UIA window for PID $procId"; continue }
    Write-Output ("WINDOW [pid $procId]: name='" + $win.Current.Name + "' class='" + $win.Current.ClassName + "'")

    # every button
    $btnCond = New-Object System.Windows.Automation.PropertyCondition($AE::ControlTypeProperty, $CT::Button)
    $btns = $win.FindAll($TS::Descendants, $btnCond)
    Write-Output ("  BUTTONS found: " + $btns.Count)
    foreach ($b in $btns) {
        $inv = $null
        try { $inv = $b.GetCurrentPattern([System.Windows.Automation.InvokePattern]::Pattern) } catch {}
        $canInvoke = if ($inv) { 'Invoke=YES' } else { 'Invoke=no' }
        Write-Output ("    BTN name='" + $b.Current.Name + "' autoId='" + $b.Current.AutomationId + "' $canInvoke")
    }

    # also dump ALL descendant elements with a non-empty name (in case Join is not typed as a Button)
    $named = $win.FindAll($TS::Descendants, [System.Windows.Automation.Condition]::TrueCondition)
    Write-Output ("  total descendants: " + $named.Count + " -- named non-button elements matching join/leave/connect:")
    foreach ($e in $named) {
        $n = $e.Current.Name
        if ($n -and ($n -match 'join|leave|connect')) {
            Write-Output ("    ELEM name='$n' type=" + $e.Current.ControlType.ProgrammaticName)
        }
    }
}
