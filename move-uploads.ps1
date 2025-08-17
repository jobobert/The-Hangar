$dir = "D:\System Backups\The Hangar\uploads"
$files = Get-ChildItem -path $dir -file

foreach ($f in $files) {
    Write-Output $f
    $parts = $f.name -split "\."

    $rootFolderName = ($parts[0], $parts[1]) -join "."
    $subFolderName = $parts[2].substring(0, 2)
    #write-host $subFolderName

    if (test-path "$dir\$rootFolderName") {
        #write-host "$rootFolderName Exists"
    }
    else {
        New-Item -Path $dir -Name $rootFolderName -ItemType Directory | Out-Null
        #write-host "root '$rootFolderName' created"
    }

    if (test-path "$dir\$rootFolderName\$subFolderName") {
        #write-host "$subFolderName Exists"
    }
    else {
        New-Item -Path "$dir\$rootFolderName" -Name $subFolderName -ItemType Directory | Out-Null
        #write-host "root '$subFolderName' created"
    }

    Move-Item -Path $f.fullname -Destination "$dir\$rootFolderName\$subFolderName"

}