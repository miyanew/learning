$distName = $MyInvocation.MyCommand.Name.replace(".ps1","")
$iniDir = "/home/user"

code --remote "wsl+$distName" $iniDir

wsl -d $distName -u root --exec sudo service ssh status
