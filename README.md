Not Maintained

# Blockhunts-status
Keeps track of your blockhunts (aka pomodore). 

No Timer or bus communication is used.
A GUI (e.g. polybar) can call ```blockhunt_status stats polybar``` periodically in order to check if a blockhunt is running and how much time is left until completion. Starting a blockhunt stores the start datetime. Checking the status again via the ```blockhunt_status``` interface will update the state and calculates the remaining time. No loop inside, no dbus spamming.

## Install
Link the script to /usr/bin or somewhere in your Path. 

```bash
ln blockhunt_status.py /usr/bin/blockhunt_status
```


## Usage

```
usage: blockhunt_status.py [-h] {add,stats,backup,init} ...

positional arguments:
  {add,stats,backup,init}

optional arguments:
  -h, --help            show this help message and exit
```

### add 
```add <location> <success>``` adds a new blockhunt. where ```<location>``` is either ```home```  or ```mobile```  and ```success either``` ``` succeeded```  or ```aborted```  (anything else will count as aborted as well). 

### stat
```stat total``` will show the total number of blockhunts

## i3 Shortchut

```  
bindsym $mod+Shift+t exec blockhunt_status hunt home
``` 


## Polybar integration
```ini
[module/blockhunts]
type = custom/script
interval = 0
tail = true
format-prefix = "hunt: "
format = <label>
exec =  blockhunt_status stats polybar
```
```ini
[module/blockhuntscount]
type = custom/script
interval = 0
tail = true
format-prefix = "Hunts today: "
format = <label>
exec = blockhunt_status stats today
 ```
