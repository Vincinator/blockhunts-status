# Blockhunts-status


## Usage

```
usage: blockhunt_status.py [-h] {add,stats,backup,init} ...

positional arguments:
  {add,stats,backup,init}

optional arguments:
  -h, --help            show this help message and exit
```

### add 
```add <location> <success>``` adds a new blockhunt. where ```<location>``` is either ```home or ```mobile and ```success either ```succeeded or ```aborted (anything else will count as aborted as well). 

### stat
```stat total``` will show the total number of blockhunts
