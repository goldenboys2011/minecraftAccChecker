Minecraft Account Valluer

========

Calcualtion Base

---

===Name===
In Special Dictionary | Inner API [1]
In English Dictionary | https://api.dictionaryapi.dev/api/v2/entries/en/ [2]
Creation Date | Mojang API [3]
Username changes # | Mojang API [4]

===Capes===
Capes # |NameMC Wrapper API [5]
	┕Cape worth | Inner API [6]


===Hypixel=== (cause why not)
Hypixel bans | Hypixel API [7]
	┕Hypixel ranks | Hypixel API [8]


Calculations

===[1]===
Check if specified username is in speciall dictionary
- if yes [+$100] & procced to [3] (skip 2)
- if no check for prefix suffix
 - if no [+-$0] & procced to [2]
 - if yes | Short prefix/suffix (<2 chars) [+$(80 * 0.8)]
	  | Medium prefix/suffix (3–4 chars) [+$(80 * 0.5)]
	  | Long prefix/suffix (>5 chars) [+-$0] 
	  & procced to [2]

===[2]===
Check using api if word in english dictionary
- if yes [+$80] & procced to [3]
- if no check for prefix suffix
 - if no [+-$0] & procced to [3]
 - if yes | Short prefix/suffix (<2 chars) [+$(80 * 0.8)]
	  | Medium prefix/suffix (3–4 chars) [+$(80 * 0.5)]
	  | Long prefix/suffix (>5 chars) [+-$0] 
	  & procced to [3]

===[3]===
Check when account was created using the offical mojang api
- if date missing [+-$0] & raiseError[missingCreationDate] & procced to [4]
- if date NOT missing for each year [+$2] * year lenght (e.x for 2 years = 2 + 4, for 4 years 2 + 4 + 6, etc.) & procced to [4]

===[4]===
Check if account changes using the offical mojang api
- if yes [-$5] * N of changes & procced to [5]
- if not [+-$0] & procced to [5]

===[5]===
Check for number of capes using  namemc wrapper
- if capes [+$2] * N of capes & procced to [6]
- if NO capes [+-$0] & procced to [7]

===[7]===
Get cape types and calculate worth based on each cape from special dictionary
(e.x.: {
MIGRATOR: +$20,
MINECON2010: +$1500
})

===[8]===
Use hypixel api to determine if user is banned / had banned
- if banned [-$1] (just for the shake of it) & raiseError[hypixelBanned] & procced to [finish]
- if past-bans [-$1] (just for the shake of it) & raiseError[hypixelPastBanned] & procced to [9]
- if NO banned [+$1] (just for the shake of it) & raiseInformation[goodHypixelQuolity] & procced to [9]

===[9]===
Get bought hypixel ranks using hypixel api.
- if ranks ([+$rankWorht] / 2.3) * each rank & procced to [finish]
- if NO ranks [+-$0] & procced to [finish]
 
