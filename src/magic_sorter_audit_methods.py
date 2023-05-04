def assign_default_section(card):
	color = card["color"]
	if color != "C":
		if len(color) > 1:
			return "31 - Multicolor"
		elif color == "W":
			return "21 - White"
		elif color == "U":
			return "22 - Blue"
		elif color == "B":
			return "23 - Black"
		elif color == "R":
			return "24 - Red"
		elif color == "G":
			return "25 - Green"
	elif "Artifact" in card["card type"]:
		pass
	elif "Land" in card["card type"]:
		pass
	else:
		return "11 - Colorless"

# 11 - Colorless
# 21 - White
# 22 - Blue
# 23 - Black
# 24 - Red
# 25 - Green
# 31 - Multicolor
# 40 - Artifact
# 41 - Artifact (Artifact Creature)
# 42 - Artifact (Utility Artifact)
# 43 - Artifact (Mana Rock)
# 44 - Artifact (Equipment)
# 50 - Land
# 51 - Basic Land
# 52 - Color Fixing Lands
# 53 - Utility Lands
# 99 - Unsorted
