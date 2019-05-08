# discord_six_bot
Python implementation of a combination translation/dictionary monitoring bot for discord designed for the Heaven's Vault conlang


# Server-wide Commands

!tmta modern word or phrase
	
	converts known English into ancient script
	
!tatm ancient word or phrase
	
	provides english equivalent for known ancient - use !tmtaf to list all known synonyms if any exist

!draw glyphs
	
	produces a png of the glyphs for confirmation and/or external use

All the above commands can have "w" appended to them to change the font color of the ancient glyphs to white (ie !draww)

!kill
	
	terminates the bot, only usable for Primary User role
	does not impact dictionary records

Various easter egg commands from talking to Six

# Archive Channel Only Commands

!Add modern _ ancient glyphs _ spoken ancient
	
	creates new record in the dictionary, everything after the ancient glyphs can be left off if the spoken form is not known
	
!Update modern _ ancient glyphs _ spoken ancient
	
	modifies an existing dictionary reference, everything after the ancient glyphs can be left off if the spoken form is not known
	
!Remove modern
	
	removes specified dictionary reference
